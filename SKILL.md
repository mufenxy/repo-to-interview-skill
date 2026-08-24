---
name: repo-to-interview
description: Analyze Python and TypeScript repositories with ASTs, build import/call graphs, trace Agent execution paths, rank interview-value source files, and generate a sanitized project_profile.md for technical interviews.
---

# Repo to Interview

## Purpose

Turn a real team repository into a technically defensible project profile for resumes and interviews. The default assumption is that the user participated in development of the repository and is allowed to describe the project at an appropriate level. Do not attempt to infer per-file or per-function authorship unless the user explicitly asks.

The primary job is to discover **what is technically important, how the system actually works, where the evidence lives, and what the user should study before an interview**.

## Core principles

1. **Code evidence before narrative.** Inspect implementation and execution paths before producing career material.
2. **Team-project framing by default.** Treat discovered modules as parts of a project the user participated in; do not make unsupported claims of sole authorship or leadership.
3. **AST and graph analysis before keyword-only conclusions.** Keywords are seeds, not proof of architecture.
4. **Interview value over repository coverage.** Find the small set of files and mechanisms most likely to support strong technical discussion.
5. **Confidentiality by default.** Portable outputs must remove proprietary identifiers, credentials, internal endpoints, customer data, source code, and restricted infrastructure details.
6. **Defensibility.** Strong material should answer What / How / Why / Failure.

## Default pipeline

For a local repository, run the automated pipeline first when Python or TypeScript/TSX code is present:

```bash
python scripts/analyze_repo.py <repo-root>
python scripts/generate_project_profile.py <repo-root>
```

This produces:

```text
<repo-root>/.repo_to_interview/
├── analysis.json
└── project_profile.md
```

The scripts are evidence collectors and first-pass generators. The Agent must still read high-value source locations and refine conclusions from actual code.

## Phase 1: Repository inventory

Inspect:

- README / architecture docs;
- dependency manifests;
- entry points;
- routers / controllers / services;
- Agent and LLM modules;
- persistence and session/state models;
- evaluation / tracing / observability;
- tests and deployment files.

Use `scripts/repo_inventory.py` for a quick inventory when useful.

Exclude generated/vendor/build directories such as `.git`, `node_modules`, `dist`, `build`, `.next`, `venv`, `.venv`, caches, generated code, and minified bundles.

## Phase 2: Python / TypeScript AST analysis

Use `scripts/analyze_repo.py`.

### Python

Parse `.py` with Python's standard-library `ast` and collect:

- module imports and from-imports;
- functions, async functions, classes and methods;
- decorators;
- line ranges;
- function/method call expressions;
- framework/architecture markers;
- Agent/LLM/evaluation/observability markers.

Do not fail the whole run because one file has a syntax error. Record parse errors and continue.

### TypeScript / TSX

Use `scripts/ts_ast_analyzer.cjs`, backed by the TypeScript Compiler API, for `.ts` / `.tsx` files. Resolve `typescript` from the target repository first, then from the Skill installation.

Collect:

- imports and exports;
- functions, methods, classes, arrow functions assigned to variables;
- call expressions;
- decorators where available;
- source line ranges;
- relevant identifiers and string markers.

If TypeScript cannot be resolved, continue Python analysis, mark TS analysis as unavailable, and tell the user how to enable it. Do not silently replace AST analysis with regex and call it equivalent.

## Phase 3: Import graph and call graph

Build two graphs from AST facts.

### Import graph

Nodes are source files. Edges represent internal imports.

Resolve conservatively:

- Python package/module paths against repository files and `__init__.py`;
- TypeScript relative imports against `.ts`, `.tsx`, `/index.ts`, `/index.tsx`;
- aliases only when they can be derived safely from common config or obvious local paths.

Unresolved external imports should remain metadata, not graph edges.

For each file calculate:

- incoming internal imports;
- outgoing internal imports;
- whether it is an entry point;
- whether it is a hub/bridge in the local architecture.

### Call graph

Nodes are functions/methods when resolvable; edges are calls.

Resolve with confidence levels:

- `high`: same-file named function/method or unambiguous imported symbol;
- `medium`: qualified call that maps plausibly to a known symbol;
- `low`: textual/heuristic match only.

Never present a low-confidence call edge as certain runtime behavior. Dynamic dispatch, dependency injection, decorators, reflection, event buses, framework routing, and tool registries can make static graphs incomplete.

## Phase 4: Agent execution-chain tracing

Automatically discover representative Agent/LLM execution chains from graph evidence.

### Seed detection

Prioritize source locations containing or calling mechanisms such as:

- agent / planner / executor / orchestrator;
- tool / function calling / tool registry;
- prompt construction;
- chat/completion/model invocation;
- context / memory / session / conversation state;
- structured output;
- judge / evaluator / benchmark;
- trace / span / OpenTelemetry;
- retry / fallback / routing;
- streaming / token / latency / cost.

Also detect common framework signals without assuming a particular framework.

### Trace procedure

1. Find likely external-facing entry points: API handlers, CLI commands, workers, UI actions, scheduled jobs, test harnesses.
2. Find high-signal Agent/LLM nodes.
3. Traverse the call graph from entry points toward high-signal nodes and downstream tool/evaluation/persistence nodes.
4. Prefer chains containing distinct architectural stages rather than repeated helper calls.
5. Record confidence and unresolved jumps.
6. Produce up to several representative chains, normally 3-8, rather than every possible path.

Represent a chain like:

```text
request handler
→ conversation service
→ diagnosis agent
→ tool selector / registry
→ tool execution
→ model decision
→ state persistence
→ evaluator / tracing
```

The chain must be grounded in files/functions. If static analysis cannot bridge two stages, mark the jump as `[dynamic/unresolved]`.

## Phase 5: Interview-value scoring

Compute an explainable score from 0-100 for source files. The score is a prioritization heuristic, not a quality metric.

Default components:

- **Agent/LLM relevance (0-30):** Agent orchestration, tool calling, prompts, evaluation, context/state, model calls.
- **Execution-path importance (0-25):** participation in representative chains and proximity to important entry points.
- **Graph centrality (0-20):** meaningful internal import/call connectivity, with caps to avoid rewarding utility dumping grounds.
- **Architecture signal (0-15):** routers, services, registries, schemas, persistence boundaries, tracing, retries, streaming, deployment control.
- **Implementation depth (0-10):** substantive functions/classes and non-trivial control flow; avoid rewarding generated or huge files merely for size.

Apply penalties for:

- generated/vendor code;
- tests/fixtures when they do not explain core mechanisms;
- config-only files with little interview depth;
- parse failures or low-confidence-only evidence.

For every ranked file expose the score breakdown and a short reason.

Use score bands:

- `85-100`: must review;
- `70-84`: high priority;
- `50-69`: useful supporting context;
- `<50`: usually background unless it supports a specific claim.

The Agent should inspect the top-ranked files manually before final packaging.

## Phase 6: Architecture reconstruction

Using AST facts, graphs, execution chains, configs, docs, and targeted source reads, reconstruct:

1. **System level** — UI/services/persistence/model providers/queues/observability.
2. **Workflow level** — request lifecycle, Agent loop, tool execution, state, evaluation, retry/fallback.
3. **Implementation level** — important files, functions, schemas, prompts, metrics and tests.

Do not infer architecture solely from filenames.

## Phase 7: Technical feature mining

For each strong mechanism record:

| Field | Meaning |
|---|---|
| Feature | Technical mechanism |
| Mechanism | How it works |
| Evidence | Files/functions/graph path |
| Interview value | High/Medium/Low |
| Confidence | High/Medium/Low |
| Role relevance | Agent / LLM app / full-stack / backend |

Important areas include orchestration, tool calling, prompt/context design, state, multi-Agent coordination, evaluation, tracing, retry/fallback, routing, latency/cost, caching, streaming, structured output and guardrails.

## Phase 8: Role-oriented packaging

### Agent Engineer

Prioritize orchestration, tool calling, execution control, state, evaluation, tracing, reliability, context design, routing and failure handling.

### LLM Application Engineer

Prioritize prompt/context construction, model integration, structured outputs, evaluation, behavior analysis, guardrails, latency/cost and observability.

### AI Full-stack Engineer

Prioritize Agent/LLM integration with APIs, frontend interaction, session persistence, streaming, schema contracts, deployment and debugging.

### Backend Engineer

Prioritize API/service boundaries, data models, async execution, retries, reliability, observability, testing and deployment.

Never rename ordinary CRUD as Agent engineering unless it materially participates in Agent state, execution, evaluation, or model interaction.

## Phase 9: Automatic project_profile.md generation

Run:

```bash
python scripts/generate_project_profile.py <repo-root>
```

The generator reads `.repo_to_interview/analysis.json` and writes `.repo_to_interview/project_profile.md` using the structure in `templates/project_profile.md`.

Auto-populate factual sections first:

- repository summary;
- language/file statistics;
- architecture candidates;
- import graph hubs;
- call graph summary;
- representative Agent execution chains;
- technical feature inventory;
- ranked interview-value files with score breakdown;
- source-code review checklist;
- static-analysis limitations.

Then the Agent should refine narrative sections after targeted source reads:

- project overview;
- role-specific positioning;
- resume bullets;
- 30-second / 2-minute pitch;
- STAR stories;
- likely interview questions;
- design rationale and tradeoffs.

Do not invent business metrics or design rationale that cannot be found in code/docs or supplied by the user.

## Phase 10: Interview preparation

For the strongest mechanisms, prepare four depths:

1. **What** — what the component does.
2. **How** — how requests/data/state/tools flow through it.
3. **Why** — why the design is useful and what alternatives exist; distinguish code evidence from inferred rationale.
4. **Failure** — failure modes, retries, evaluation, observability and tradeoffs.

Generate likely L1/L2/L3/high-risk follow-up questions and map each to source locations.

## Phase 11: Confidentiality review

Before portable output, read `references/confidentiality.md`.

Sanitize:

- proprietary project/team/customer names when required;
- credentials/tokens/secrets;
- internal URLs/IPs/hostnames;
- customer identifiers/data;
- private infrastructure topology;
- source snippets that should not leave the environment.

When uncertain, generalize and mark `[REVIEW_CONFIDENTIALITY]`.

## Outputs

Default outputs are:

```text
.repo_to_interview/analysis.json
.repo_to_interview/project_profile.md
```

The final profile should include:

- project overview;
- architecture map;
- AST/static-analysis summary;
- import/call graph findings;
- representative Agent execution chains;
- technical feature inventory;
- interview-value ranking;
- role-specific positioning;
- resume candidates;
- project pitches;
- interview question bank;
- code review checklist;
- confidentiality review;
- limitations/open questions.

## Supporting files

- `scripts/analyze_repo.py` — orchestrates Python AST analysis, TypeScript AST analysis, graph construction, execution-chain heuristics, and scoring.
- `scripts/ts_ast_analyzer.cjs` — TypeScript/TSX AST collector using the TypeScript Compiler API.
- `scripts/generate_project_profile.py` — generates the first-pass `project_profile.md`.
- `scripts/repo_inventory.py` — lightweight inventory.
- `references/ownership-model.md` — team-project participation and wording policy; no automatic authorship inference by default.
- `references/packaging-framework.md` — role-oriented packaging guidance.
- `references/confidentiality.md` — sanitization guidance.
- `templates/project_profile.md` — output structure.

## Behavior rules

- Start by analyzing the repository when access exists; do not make the user manually explain code the Agent can inspect.
- Do not run automatic authorship/ownership inference unless explicitly requested.
- Assume the user participated in the repository, while avoiding unsupported claims of sole implementation or leadership.
- Static analysis is incomplete by nature; explicitly mark dynamic or unresolved behavior.
- Never fabricate implementation details, metrics, architecture, runtime paths, or design rationale.
- Prefer a small number of high-value files and execution chains over exhaustive dumps.
- If the user asks only for repository analysis, do not prematurely generate polished resume claims.
- Keep confidential source code inside the approved environment; portable outputs must be sanitized.
