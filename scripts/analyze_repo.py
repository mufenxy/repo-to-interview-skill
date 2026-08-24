#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import math
import os
import subprocess
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

SKIP_DIRS = {
    '.git', 'node_modules', 'dist', 'build', '.next', '.venv', 'venv', '__pycache__',
    '.mypy_cache', '.pytest_cache', '.tox', 'coverage', '.repo_to_interview'
}
PY_EXTS = {'.py'}
TS_EXTS = {'.ts', '.tsx'}
ENTRY_MARKERS = {'main', 'app', 'server', 'cli', 'worker', 'router', 'routes', 'api'}
AGENT_TERMS = {
    'agent','planner','executor','orchestrator','tool','function_call','functioncall','prompt',
    'memory','context','session','conversation','judge','evaluator','evaluation','trace','span',
    'opentelemetry','retry','fallback','router','stream','token','latency','cost','model','llm',
    'chat','completion','structured_output','guardrail'
}
ARCH_TERMS = {
    'router','route','service','controller','repository','registry','schema','model','database',
    'storage','queue','worker','middleware','trace','span','retry','fallback','stream','cache'
}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def norm(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = dotted_name(node.value)
        return f'{left}.{node.attr}' if left else node.attr
    return None


def marker_hits(texts: list[str]) -> list[str]:
    blob = '\n'.join(texts).lower().replace('-', '_')
    return sorted({t for t in AGENT_TERMS | ARCH_TERMS if t in blob})


def py_parse(path: Path, root: Path) -> dict[str, Any]:
    rel = norm(path, root)
    try:
        src = path.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(src, filename=rel)
    except Exception as e:
        return {'path': rel, 'language': 'python', 'parse_error': str(e), 'imports': [], 'symbols': [], 'calls': [], 'markers': []}

    imports: list[dict[str, Any]] = []
    symbols: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    strings: list[str] = []

    class V(ast.NodeVisitor):
        def __init__(self):
            self.scope: list[str] = []

        def visit_Import(self, node: ast.Import):
            for n in node.names:
                imports.append({'module': n.name, 'name': None, 'alias': n.asname, 'level': 0})

        def visit_ImportFrom(self, node: ast.ImportFrom):
            for n in node.names:
                imports.append({'module': node.module or '', 'name': n.name, 'alias': n.asname, 'level': node.level})

        def visit_ClassDef(self, node: ast.ClassDef):
            qn = '.'.join(self.scope + [node.name])
            symbols.append({'kind': 'class', 'name': node.name, 'qualname': qn, 'line': node.lineno, 'end_line': getattr(node, 'end_lineno', node.lineno), 'decorators': [dotted_name(d) or '' for d in node.decorator_list]})
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()

        def _func(self, node, kind: str):
            qn = '.'.join(self.scope + [node.name])
            symbols.append({'kind': kind, 'name': node.name, 'qualname': qn, 'line': node.lineno, 'end_line': getattr(node, 'end_lineno', node.lineno), 'decorators': [dotted_name(d) or '' for d in node.decorator_list]})
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef):
            self._func(node, 'function' if not self.scope else 'method')

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            self._func(node, 'async_function' if not self.scope else 'async_method')

        def visit_Call(self, node: ast.Call):
            calls.append({'caller': '.'.join(self.scope) or '<module>', 'callee': dotted_name(node.func) or '<dynamic>', 'line': getattr(node, 'lineno', None)})
            self.generic_visit(node)

        def visit_Constant(self, node: ast.Constant):
            if isinstance(node.value, str) and len(node.value) <= 400:
                strings.append(node.value)

    V().visit(tree)
    texts = [rel] + [i['module'] for i in imports] + [s['qualname'] for s in symbols] + [c['callee'] for c in calls] + strings
    return {'path': rel, 'language': 'python', 'parse_error': None, 'imports': imports, 'symbols': symbols, 'calls': calls, 'markers': marker_hits(texts)}


def run_ts_analyzer(root: Path, files: list[Path], script_dir: Path) -> tuple[list[dict[str, Any]], str | None]:
    if not files:
        return [], None
    manifest = script_dir / '.ts_files.json'
    manifest.write_text(json.dumps([str(p.resolve()) for p in files]), encoding='utf-8')
    cmd = ['node', str(script_dir / 'ts_ast_analyzer.cjs'), str(root.resolve()), str(manifest)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if proc.returncode != 0:
            return [], (proc.stderr or proc.stdout).strip()
        data = json.loads(proc.stdout)
        return data.get('files', []), data.get('warning')
    except FileNotFoundError:
        return [], 'Node.js not found; TypeScript AST analysis unavailable.'
    except Exception as e:
        return [], str(e)
    finally:
        try: manifest.unlink()
        except OSError: pass


def py_module_candidates(rel: str) -> set[str]:
    p = Path(rel)
    parts = list(p.with_suffix('').parts)
    out = {'.'.join(parts)}
    if parts and parts[-1] == '__init__':
        out.add('.'.join(parts[:-1]))
    return {x for x in out if x}


def resolve_py_import(src: str, imp: dict[str, Any], py_modules: dict[str, str]) -> str | None:
    mod = imp.get('module') or ''
    level = int(imp.get('level') or 0)
    src_parts = list(Path(src).with_suffix('').parts[:-1])
    if level:
        keep = max(0, len(src_parts) - (level - 1))
        prefix = src_parts[:keep]
        full = '.'.join(prefix + ([mod] if mod else []))
    else:
        full = mod
    candidates = [full]
    name = imp.get('name')
    if name and name != '*':
        candidates.insert(0, f'{full}.{name}' if full else name)
    for c in candidates:
        if c in py_modules:
            return py_modules[c]
    while '.' in full:
        full = full.rsplit('.', 1)[0]
        if full in py_modules:
            return py_modules[full]
    return None


def resolve_ts_import(src: str, spec: str, existing: set[str]) -> str | None:
    if not spec.startswith('.'):
        return None
    base = (Path(src).parent / spec).as_posix()
    tries = [base, base + '.ts', base + '.tsx', base + '/index.ts', base + '/index.tsx']
    for t in tries:
        clean = Path(t).as_posix()
        if clean in existing:
            return clean
    return None


def build_import_graph(files: list[dict[str, Any]]) -> tuple[list[dict[str, str]], dict[str, int], dict[str, int]]:
    existing = {f['path'] for f in files}
    py_modules: dict[str, str] = {}
    for f in files:
        if f['language'] == 'python':
            for m in py_module_candidates(f['path']):
                py_modules[m] = f['path']
    edges = []
    indeg, outdeg = Counter(), Counter()
    for f in files:
        for imp in f.get('imports', []):
            dst = None
            if f['language'] == 'python':
                dst = resolve_py_import(f['path'], imp, py_modules)
            else:
                spec = imp.get('module') or ''
                dst = resolve_ts_import(f['path'], spec, existing)
            if dst and dst != f['path']:
                edges.append({'source': f['path'], 'target': dst})
                outdeg[f['path']] += 1; indeg[dst] += 1
    return edges, dict(indeg), dict(outdeg)


def symbol_index(files: list[dict[str, Any]]) -> tuple[dict[str, list[str]], dict[str, set[str]]]:
    by_name = defaultdict(list)
    file_syms = defaultdict(set)
    for f in files:
        for s in f.get('symbols', []):
            sid = f"{f['path']}::{s['qualname']}"
            by_name[s['name']].append(sid)
            file_syms[f['path']].add(s['name'])
    return by_name, file_syms


def build_call_graph(files: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_name, file_syms = symbol_index(files)
    edges: list[dict[str, str]] = []
    for f in files:
        for c in f.get('calls', []):
            caller = f"{f['path']}::{c.get('caller') or '<module>'}"
            callee = c.get('callee') or '<dynamic>'
            last = callee.split('.')[-1]
            matches = by_name.get(last, [])
            target, conf = None, None
            same = [m for m in matches if m.startswith(f['path'] + '::')]
            if len(same) == 1:
                target, conf = same[0], 'high'
            elif len(matches) == 1:
                target, conf = matches[0], 'medium'
            elif matches:
                target, conf = matches[0], 'low'
            if target:
                edges.append({'source': caller, 'target': target, 'confidence': conf, 'callee_text': callee})
    return edges


def entrypoint_score(f: dict[str, Any]) -> int:
    stem = Path(f['path']).stem.lower()
    path = f['path'].lower()
    score = sum(1 for t in ENTRY_MARKERS if t in stem or f'/{t}' in path)
    decs = ' '.join(d for s in f.get('symbols', []) for d in s.get('decorators', [])).lower()
    if any(x in decs for x in ['route','get','post','put','delete','command']): score += 2
    return score


def trace_chains(files: list[dict[str, Any]], call_edges: list[dict[str, str]], max_chains: int = 6) -> list[dict[str, Any]]:
    marker_files = {f['path'] for f in files if f.get('markers')}
    entry_files = {f['path'] for f in files if entrypoint_score(f) > 0}
    adj = defaultdict(list)
    for e in call_edges:
        adj[e['source']].append(e)
    starts = []
    for f in files:
        if f['path'] in entry_files:
            for s in f.get('symbols', []):
                starts.append(f"{f['path']}::{s['qualname']}")
    if not starts:
        for f in files:
            if f['path'] in marker_files:
                for s in f.get('symbols', [])[:3]: starts.append(f"{f['path']}::{s['qualname']}")
    chains = []
    seen = set()
    for start in starts[:40]:
        q = deque([(start, [start], [])])
        while q and len(chains) < max_chains:
            node, path, confs = q.popleft()
            file_path = node.split('::',1)[0]
            if len(path) >= 3 and any(p.split('::',1)[0] in marker_files for p in path[1:]):
                sig = tuple(path)
                if sig not in seen:
                    seen.add(sig)
                    chains.append({'nodes': path, 'confidence': 'low' if 'low' in confs else ('medium' if 'medium' in confs else 'high')})
                    if len(chains) >= max_chains: break
            if len(path) >= 8: continue
            for e in adj.get(node, []):
                if e['target'] not in path:
                    q.append((e['target'], path + [e['target']], confs + [e['confidence']]))
    return chains


def score_files(files: list[dict[str, Any]], indeg: dict[str,int], outdeg: dict[str,int], chains: list[dict[str,Any]]) -> list[dict[str, Any]]:
    chain_counts = Counter(n.split('::',1)[0] for c in chains for n in c['nodes'])
    ranked = []
    for f in files:
        markers = set(f.get('markers', []))
        agent = min(30, 5 * len(markers & AGENT_TERMS))
        execution = min(25, 8 * chain_counts.get(f['path'], 0) + 4 * min(2, entrypoint_score(f)))
        graph = min(20, 3 * min(4, indeg.get(f['path'],0)) + 2 * min(4, outdeg.get(f['path'],0)))
        arch = min(15, 3 * len(markers & ARCH_TERMS))
        symbols = f.get('symbols', [])
        depth = min(10, int(math.sqrt(max(0, len(symbols))) * 4))
        penalty = 0
        low = f['path'].lower()
        if any(x in low for x in ['/test','tests/','fixture','mock']): penalty += 8
        if f.get('parse_error'): penalty += 15
        score = max(0, min(100, agent + execution + graph + arch + depth - penalty))
        reasons = []
        if agent: reasons.append(f'Agent/LLM relevance {agent}/30')
        if execution: reasons.append(f'execution-path importance {execution}/25')
        if graph: reasons.append(f'graph centrality {graph}/20')
        if arch: reasons.append(f'architecture signal {arch}/15')
        if depth: reasons.append(f'implementation depth {depth}/10')
        if penalty: reasons.append(f'penalty -{penalty}')
        ranked.append({'path': f['path'], 'score': score, 'breakdown': {'agent_llm':agent,'execution_path':execution,'graph_centrality':graph,'architecture_signal':arch,'implementation_depth':depth,'penalty':penalty}, 'reason': '; '.join(reasons) or 'low static-analysis signal'})
    return sorted(ranked, key=lambda x: (-x['score'], x['path']))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repo_root', nargs='?', default='.')
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()
    script_dir = Path(__file__).resolve().parent
    py_files, ts_files = [], []
    for p in root.rglob('*'):
        if not p.is_file() or should_skip(p.relative_to(root)): continue
        if p.suffix in PY_EXTS: py_files.append(p)
        elif p.suffix in TS_EXTS and not p.name.endswith('.d.ts'): ts_files.append(p)

    files = [py_parse(p, root) for p in py_files]
    ts_data, ts_warning = run_ts_analyzer(root, ts_files, script_dir)
    files.extend(ts_data)
    files.sort(key=lambda x: x['path'])

    import_edges, indeg, outdeg = build_import_graph(files)
    call_edges = build_call_graph(files)
    chains = trace_chains(files, call_edges)
    ranking = score_files(files, indeg, outdeg, chains)

    lang_counts = Counter(f['language'] for f in files)
    output = {
        'version': '0.2',
        'repo_root': str(root),
        'summary': {'files_analyzed': len(files), 'languages': dict(lang_counts), 'python_files': len(py_files), 'typescript_files': len(ts_files), 'parse_errors': sum(1 for f in files if f.get('parse_error'))},
        'warnings': [w for w in [ts_warning] if w],
        'files': files,
        'import_graph': {'edges': import_edges, 'in_degree': indeg, 'out_degree': outdeg},
        'call_graph': {'edges': call_edges},
        'agent_execution_chains': chains,
        'interview_value_ranking': ranking,
        'limitations': [
            'Static call graphs can miss dynamic dispatch, dependency injection, decorators, event buses, reflection and runtime tool registries.',
            'Low-confidence call edges are heuristic and must be verified from source before use in interview narratives.',
            'Interview-value scores prioritize review order; they are not code-quality scores.'
        ]
    }
    out_dir = root / '.repo_to_interview'
    out_dir.mkdir(exist_ok=True)
    out = out_dir / 'analysis.json'
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(out)

if __name__ == '__main__':
    main()
