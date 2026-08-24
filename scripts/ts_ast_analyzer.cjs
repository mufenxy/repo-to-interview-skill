#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function loadTS(repoRoot) {
  const candidates = [
    path.join(repoRoot, 'node_modules', 'typescript'),
    path.join(__dirname, '..', 'node_modules', 'typescript'),
    'typescript'
  ];
  for (const c of candidates) {
    try { return require(c); } catch (_) {}
  }
  return null;
}

function markerHits(texts) {
  const terms = [
    'agent','planner','executor','orchestrator','tool','function_call','functioncall','prompt',
    'memory','context','session','conversation','judge','evaluator','evaluation','trace','span',
    'opentelemetry','retry','fallback','router','stream','token','latency','cost','model','llm',
    'chat','completion','structured_output','guardrail','route','service','controller','repository',
    'registry','schema','database','storage','queue','worker','middleware','cache'
  ];
  const blob = texts.join('\n').toLowerCase().replaceAll('-', '_');
  return [...new Set(terms.filter(t => blob.includes(t)))].sort();
}

function exprName(ts, node) {
  if (!node) return '<dynamic>';
  if (ts.isIdentifier(node)) return node.text;
  if (ts.isPropertyAccessExpression(node)) return `${exprName(ts, node.expression)}.${node.name.text}`;
  if (ts.isElementAccessExpression(node)) return exprName(ts, node.expression);
  return '<dynamic>';
}

function pos(sf, node) {
  const s = sf.getLineAndCharacterOfPosition(node.getStart(sf));
  const e = sf.getLineAndCharacterOfPosition(node.getEnd());
  return { line: s.line + 1, end_line: e.line + 1 };
}

function analyzeFile(ts, repoRoot, filename) {
  const rel = path.relative(repoRoot, filename).replaceAll(path.sep, '/');
  let src;
  try { src = fs.readFileSync(filename, 'utf8'); }
  catch (e) { return { path: rel, language: 'typescript', parse_error: String(e), imports: [], symbols: [], calls: [], markers: [] }; }

  const kind = filename.endsWith('.tsx') ? ts.ScriptKind.TSX : ts.ScriptKind.TS;
  const sf = ts.createSourceFile(filename, src, ts.ScriptTarget.Latest, true, kind);
  const imports = [], symbols = [], calls = [], texts = [rel];
  const scope = [];

  function decoratorsOf(node) {
    const out = [];
    if (ts.canHaveDecorators && ts.canHaveDecorators(node)) {
      for (const d of ts.getDecorators(node) || []) out.push(d.getText(sf));
    }
    return out;
  }

  function addSymbol(kind, name, node) {
    if (!name) return;
    const qn = [...scope, name].join('.');
    const p = pos(sf, node);
    const decs = decoratorsOf(node);
    symbols.push({ kind, name, qualname: qn, line: p.line, end_line: p.end_line, decorators: decs });
    texts.push(qn, ...decs);
  }

  function visit(node) {
    if (ts.isImportDeclaration(node) && node.moduleSpecifier && ts.isStringLiteral(node.moduleSpecifier)) {
      const mod = node.moduleSpecifier.text;
      imports.push({ module: mod, name: null, alias: null, level: 0 });
      texts.push(mod);
    }

    if (ts.isFunctionDeclaration(node) && node.name) {
      addSymbol('function', node.name.text, node);
      scope.push(node.name.text); ts.forEachChild(node, visit); scope.pop(); return;
    }
    if (ts.isClassDeclaration(node) && node.name) {
      addSymbol('class', node.name.text, node);
      scope.push(node.name.text); ts.forEachChild(node, visit); scope.pop(); return;
    }
    if (ts.isMethodDeclaration(node)) {
      const name = node.name ? node.name.getText(sf) : '<method>';
      addSymbol('method', name, node);
      scope.push(name); ts.forEachChild(node, visit); scope.pop(); return;
    }
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) && node.initializer && (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer))) {
      const name = node.name.text;
      addSymbol('function', name, node);
      scope.push(name); ts.forEachChild(node.initializer, visit); scope.pop(); return;
    }
    if (ts.isCallExpression(node)) {
      const callee = exprName(ts, node.expression);
      const p = pos(sf, node);
      calls.push({ caller: scope.join('.') || '<module>', callee, line: p.line });
      texts.push(callee);
    }
    if (ts.isStringLiteralLike(node) && node.text.length <= 400) texts.push(node.text);
    ts.forEachChild(node, visit);
  }

  visit(sf);
  const diagnostics = sf.parseDiagnostics || [];
  return {
    path: rel,
    language: 'typescript',
    parse_error: diagnostics.length ? diagnostics.map(d => String(d.messageText)).join('; ') : null,
    imports, symbols, calls, markers: markerHits(texts)
  };
}

const repoRoot = path.resolve(process.argv[2] || '.');
const manifest = process.argv[3];
const ts = loadTS(repoRoot);
if (!ts) {
  console.error('TypeScript package not found. Install `typescript` in the target repository or in the skill directory.');
  process.exit(2);
}
const files = JSON.parse(fs.readFileSync(manifest, 'utf8'));
const result = { files: files.map(f => analyzeFile(ts, repoRoot, f)), warning: null };
process.stdout.write(JSON.stringify(result));
