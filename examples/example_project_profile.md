# Example Project Profile

> Synthetic example. No company or proprietary project information is included.

## Project Overview

A simulated infrastructure diagnosis platform injects device failures into a sandbox environment. A diagnosis agent calls structured tools to inspect devices and predicts the failing component. A separate evaluation workflow scores repeated runs.

## Architecture Map

| Module | Responsibility | Key files |
|---|---|---|
| diagnosis agent | orchestrates reasoning and tool calls | `src/agent/diagnosis.py` |
| tool registry | exposes structured inspection tools | `src/tools/registry.py` |
| evaluator | aggregates repeated-run metrics | `src/eval/evaluator.py` |
| tracing | records model and tool spans | `src/observability/tracing.py` |

## Verified Contribution Map

| Component | Ownership | Evidence |
|---|---|---|
| diagnosis workflow | MAJOR_CONTRIBUTOR | user confirmation + PR evidence |
| evaluator | OWNED | user confirmation + commits |
| tracing | UNDERSTAND_ONLY | repository evidence only |

## Evidence Map

| Candidate claim | Ownership | Interview value | Risk | Usage |
|---|---|---|---|---|
| implemented repeated-run evaluation and pass@k-style aggregation | OWNED | High | Low | Resume + interview |
| contributed to diagnosis-agent tool orchestration | MAJOR_CONTRIBUTOR | High | Medium | Resume + interview |
| designed OpenTelemetry tracing architecture | UNDERSTAND_ONLY | High | High | Do not claim personally |

## Resume Candidate

Contributed to a tool-calling diagnosis-agent workflow for simulated infrastructure failures and implemented repeated-run evaluation to quantify diagnosis reliability across scenarios.

## Interview Review Priorities

1. `src/agent/diagnosis.py` — agent loop and tool selection path.
2. `src/tools/registry.py` — tool schema and result contract.
3. `src/eval/evaluator.py` — repeated-run aggregation and metric definitions.
