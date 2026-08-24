#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import Counter


def md_table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
    for row in rows:
        out.append('| ' + ' | '.join(str(x).replace('|', '\\|') for x in row) + ' |')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repo_root', nargs='?', default='.')
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()
    analysis_path = root / '.repo_to_interview' / 'analysis.json'
    if not analysis_path.exists():
        raise SystemExit(f'Missing {analysis_path}. Run analyze_repo.py first.')

    data = json.loads(analysis_path.read_text(encoding='utf-8'))
    files = data.get('files', [])
    ranking = data.get('interview_value_ranking', [])
    import_edges = data.get('import_graph', {}).get('edges', [])
    call_edges = data.get('call_graph', {}).get('edges', [])
    chains = data.get('agent_execution_chains', [])
    summary = data.get('summary', {})

    marker_counts = Counter()
    for f in files:
        marker_counts.update(f.get('markers', []))

    top_import_in = sorted(data.get('import_graph', {}).get('in_degree', {}).items(), key=lambda x: (-x[1], x[0]))[:10]
    top_import_out = sorted(data.get('import_graph', {}).get('out_degree', {}).items(), key=lambda x: (-x[1], x[0]))[:10]

    ranked_rows = []
    for r in ranking[:15]:
        b = r['breakdown']
        ranked_rows.append([
            r['path'], r['score'], b['agent_llm'], b['execution_path'], b['graph_centrality'], b['architecture_signal'], b['implementation_depth'], r['reason']
        ])

    feature_rows = []
    for name, count in marker_counts.most_common(20):
        evidence = [f['path'] for f in files if name in f.get('markers', [])][:5]
        feature_rows.append([name, count, ', '.join(evidence), 'Static marker; verify mechanism from source'])

    chain_sections = []
    for i, c in enumerate(chains, 1):
        nodes = '\n'.join(f'{j+1}. `{n}`' for j, n in enumerate(c.get('nodes', [])))
        chain_sections.append(f'### Chain {i} — confidence: {c.get("confidence", "unknown")}\n\n{nodes}')

    review_rows = []
    for idx, r in enumerate(ranking[:12], 1):
        score = r['score']
        if score >= 85: pr = 'P0'
        elif score >= 70: pr = 'P1'
        elif score >= 50: pr = 'P2'
        else: pr = 'P3'
        review_rows.append([pr, r['path'], score, r['reason']])

    text = f'''# Project Profile

> Auto-generated first pass from static repository analysis. Refine narrative claims after reading high-value source files. Do not export confidential source code.

## 1. Project Overview

- Repository: `{root.name}`
- Files analyzed: {summary.get('files_analyzed', 0)}
- Languages: {json.dumps(summary.get('languages', {}), ensure_ascii=False)}
- Parse errors: {summary.get('parse_errors', 0)}
- Target role: _fill based on application_
- Problem / scenario: _derive from README/docs or user input_
- High-level solution: _refine after source review_

## 2. Static Analysis Summary

- Import graph edges: {len(import_edges)}
- Resolved call graph edges: {len(call_edges)}
- Representative Agent execution chains: {len(chains)}
- Analysis version: {data.get('version', 'unknown')}

### Warnings

''' + ('\n'.join(f'- {w}' for w in data.get('warnings', [])) if data.get('warnings') else '- None') + '''

## 3. Architecture Candidates

### Top internal import hubs

''' + (md_table(['File', 'Incoming imports'], top_import_in) if top_import_in else '_No internal import hubs resolved._') + '''

### Top internal import dependents

''' + (md_table(['File', 'Outgoing imports'], top_import_out) if top_import_out else '_No internal import dependents resolved._') + '''

## 4. Representative Agent Execution Chains

''' + ('\n\n'.join(chain_sections) if chain_sections else '_No representative chain resolved statically. Inspect dynamic registries/framework wiring manually._') + '''

## 5. Technical Feature Inventory

''' + (md_table(['Signal', 'Files', 'Example evidence', 'Interpretation'], feature_rows) if feature_rows else '_No high-signal technical markers detected._') + '''

## 6. Interview-Value Ranking

The score ranks review priority, not code quality.

''' + (md_table(['File', 'Score', 'Agent/LLM', 'Execution', 'Graph', 'Architecture', 'Depth', 'Reason'], ranked_rows) if ranked_rows else '_No ranked files._') + '''

## 7. Role-Specific Positioning

### Agent Engineer

Prioritize orchestration, tool calling, state/context, evaluation, tracing, retry/fallback, routing, and representative execution chains discovered above.

### LLM Application Engineer

Prioritize prompt/context construction, model integration, structured output, evaluation, guardrails, latency/cost, and observability.

### AI Full-stack Engineer

Prioritize Agent/LLM integration with APIs, frontend interactions, session state, streaming, schemas, deployment, and debugging.

### Backend Engineer

Prioritize API/service boundaries, data models, async execution, retries, reliability, observability, and deployment.

## 8. Resume Bullet Candidates

_Agent must generate these only after reading P0/P1 files and verifying the mechanism. Use team-project framing unless stronger wording is directly supported by user context._

## 9. 30-Second Project Pitch

_To be refined from README/docs + P0/P1 implementation evidence._

## 10. 2-Minute Project Pitch

_To be refined from system architecture + one representative end-to-end execution chain._

## 11. STAR Stories

_To be generated from concrete engineering problems, actions, and measurable outcomes supplied by code/docs/user._

## 12. Interview Question Bank

Suggested areas to generate questions from:

- Why is the Agent execution chain structured this way?
- How are tools registered, selected, validated, and executed?
- How is conversation/session state persisted and propagated?
- How are Agent failures, retries, fallback, or routing handled?
- How is evaluation implemented and what does it measure?
- How are traces/spans/metrics used to diagnose behavior?
- Which runtime behaviors cannot be proven from static analysis?

## 13. Code Review Checklist

''' + (md_table(['Priority', 'File', 'Score', 'Why review'], review_rows) if review_rows else '_No files ranked._') + '''

## 14. Confidentiality Review

Before exporting this profile outside the approved environment:

- remove proprietary project/team/customer identifiers where required;
- remove source snippets, credentials, private endpoints/IPs, and customer data;
- generalize private infrastructure topology;
- mark uncertain details as `[REVIEW_CONFIDENTIALITY]`.

## 15. Static-Analysis Limitations

''' + '\n'.join(f'- {x}' for x in data.get('limitations', [])) + '''

## 16. Open Questions / Manual Verification

- What is the externally safe description of the business/problem context?
- Which P0/P1 files contain the strongest mechanisms for the target role?
- Which execution-chain jumps depend on dependency injection, registries, decorators, or runtime dispatch?
- Which metrics/results are approved for resume/interview use?
'''

    out = root / '.repo_to_interview' / 'project_profile.md'
    out.write_text(text, encoding='utf-8')
    print(out)

if __name__ == '__main__':
    main()
