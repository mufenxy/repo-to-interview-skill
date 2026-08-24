---
name: repo-to-interview
description: Analyze a software repository, extract evidence-backed technical contributions, and package them for resumes and technical interviews without inventing ownership or exposing confidential information.
---

# Repo to Interview

## Purpose

Turn a software repository into an evidence-backed project profile for technical recruiting. Inspect the repository first, identify technically meaningful components, verify what the user actually contributed, and only then produce role-oriented resume and interview material.

This skill is especially useful for internships and team projects where the repository contains substantially more work than the user personally implemented.

## Core principles

1. **Repository evidence before narrative.** Inspect code, configuration, tests, docs, commit history, and architecture before writing project claims.
2. **Project capability is not personal ownership.** Never convert a team capability into a first-person claim without evidence or user confirmation.
3. **Technical depth over generic wording.** Prefer mechanisms, tradeoffs, interfaces, data flow, evaluation, observability, and measurable outcomes.
4. **Confidentiality by default.** Portable outputs must exclude proprietary names, credentials, customer data, internal endpoints, private infrastructure details, source code, and other restricted information.
5. **Interview defensibility.** A claim is useful only if the user can explain how it works, why it was designed that way, and where the relevant implementation lives.

## Inputs

Use as many of the following as are available:

- current repository or repository URL;
- target role, e.g. Agent Engineer, LLM Application Engineer, AI Full-stack Engineer, Backend Engineer, ML Engineer;
- user's rough description of responsibilities;
- commit / PR identity when available;
- job description when available;
- existing resume bullets when available.

Do not require all inputs before beginning repository reconnaissance.

## Workflow

### Phase 1: Repository reconnaissance

Inspect the repository before asking the user to summarize it.

Start with high-signal sources:

- README and architecture docs;
- top-level directory structure;
- dependency manifests;
- application entry points;
- API / router / service layers;
- database schemas and migrations;
- configuration files;
- tests;
- Docker / deployment files;
- CI workflows;
- commit history and PR history if available.

Then identify major execution paths and produce a repository map.

For local repositories, prefer fast native inspection tools such as:

```bash
find . -maxdepth 3 -type f | sort
rg -n "agent|tool|function.?call|prompt|planner|memory|context|session|conversation|workflow|judge|eval|trace|span|opentelemetry|retry|fallback|router|token|latency|cost" .
```

Do not dump entire large files when targeted reads are sufficient.

Record:

- subsystem / module;
- purpose;
- entry points;
- important classes / functions;
- upstream / downstream dependencies;
- relevant files;
- confidence level.

### Phase 2: Architecture reconstruction

Reconstruct the project at three levels:

1. **System level** — services, UI, persistence, external dependencies, model providers, queues, observability.
2. **Workflow level** — request lifecycle, agent loop, tool execution, state transitions, evaluation loop, retry / fallback behavior.
3. **Implementation level** — key files, classes, functions, schemas, prompts, metrics, tests.

When possible, trace at least one representative end-to-end path from input to output.

### Phase 3: Technical feature mining

Search for role-relevant mechanisms, not just keywords.

For Agent / LLM application roles, inspect for:

- agent orchestration;
- tool / function calling;
- tool registry and schemas;
- planning and control flow;
- prompt construction;
- context / session management;
- memory and persistence;
- structured output;
- multi-agent coordination;
- retries and fallbacks;
- model routing;
- evaluation / LLM-as-a-Judge;
- benchmark metrics such as pass@k / success@k;
- tracing / spans / OpenTelemetry;
- latency and token accounting;
- cost controls;
- caching;
- streaming;
- guardrails;
- failure analysis.

For each candidate feature, explain the actual mechanism from code evidence. Do not infer architecture solely from a filename or keyword hit.

### Phase 4: Contribution verification

Create a candidate contribution table. Every claim must receive one ownership label:

- `OWNED` — user independently implemented or designed the substantial part.
- `MAJOR_CONTRIBUTOR` — user implemented or designed a large part with team collaboration.
- `CONTRIBUTED` — user made a meaningful but bounded contribution.
- `UNDERSTAND_ONLY` — user can explain the component but did not materially implement it.
- `UNKNOWN` — evidence is insufficient.
- `DO_NOT_CLAIM` — attribution would be misleading or confidentiality risk is too high.

Accept ownership evidence from:

1. explicit user confirmation tied to a concrete module or task;
2. commits / PRs attributable to the user;
3. issue / task records linking the user and component;
4. other direct evidence supplied by the user.

Repository presence alone is never ownership evidence.

For `UNKNOWN` items, ask the user compact verification questions with concrete choices. Prefer batching related items instead of asking one question at a time.

### Phase 5: Claim gate

Before generating first-person resume or interview claims, verify all of the following:

- ownership label is `OWNED`, `MAJOR_CONTRIBUTOR`, or `CONTRIBUTED`;
- code or user evidence exists;
- the user can plausibly defend the mechanism in a technical interview;
- wording does not overstate scope;
- confidential details can be safely generalized.

If any condition fails, downgrade wording to project-level framing such as:

- "the system uses ...";
- "the team implemented ...";
- "I contributed to ...".

Never use "I designed", "I built", "I implemented", or equivalent wording for `UNDERSTAND_ONLY`, `UNKNOWN`, or `DO_NOT_CLAIM` items.

### Phase 6: Evidence map

Build an evidence map with at least these fields:

| Field | Meaning |
|---|---|
| Candidate claim | Technical contribution that may be useful |
| Ownership | Ownership label |
| Evidence | Files, functions, commits, PRs, or user confirmation |
| Mechanism | What the implementation actually does |
| Interview value | High / Medium / Low |
| Interview risk | High / Medium / Low |
| Confidentiality risk | High / Medium / Low |
| Recommended usage | Resume / interview / background only / do not use |

Prefer fewer high-quality claims over many shallow claims.

### Phase 7: Role-oriented packaging

Adapt the same verified project evidence to the target role.

#### Agent Engineer

Prioritize orchestration, tool calling, agent state, workflows, evaluation, tracing, reliability, prompt/context design, and model routing.

#### LLM Application Engineer

Prioritize prompt design, structured outputs, evaluation, RAG/context integration if present, model behavior analysis, guardrails, latency/cost tradeoffs, and observability.

#### AI Full-stack Engineer

Prioritize LLM/Agent integration, API design, session persistence, frontend interaction, streaming, schema contracts, deployment, and debugging.

#### Backend Engineer

Prioritize API boundaries, service design, data models, async execution, retries, reliability, observability, testing, and deployment.

Never rename ordinary CRUD work as Agent engineering unless it actually participates in agent execution, state management, evaluation, or model interaction.

### Phase 8: Interview preparation

For strong claims, generate:

- a 30-second project introduction;
- a 2-minute project introduction;
- resume bullet candidates;
- STAR stories;
- architecture explanation;
- technical deep-dive questions;
- likely follow-up questions;
- high-risk questions;
- source files / functions to review before interview.

Prepare important claims at four depths:

1. **What** — what the component does.
2. **How** — how requests, data, state, and tools move through it.
3. **Why** — why this design was chosen and what alternatives existed.
4. **Failure** — failure modes, retries, evaluation, observability, and tradeoffs.

### Phase 9: Source review prioritization

Rank source locations by interview value, not by file size.

For each recommended file/function explain:

- which claim it supports;
- what mechanism the user should understand;
- what interview question it helps answer;
- whether ownership wording needs care.

Prefer a short list of high-value locations over a broad repository dump.

### Phase 10: Confidentiality review

Before producing portable notes, resume content, or interview scripts, read `references/confidentiality.md` and sanitize sensitive details.

When disclosure status is uncertain, replace the detail with an abstraction and mark:

`[REVIEW_CONFIDENTIALITY]`

Do not export non-public source code or sensitive implementation details from restricted environments.

## Outputs

The default artifact is a structured `project_profile.md` based on `templates/project_profile.md`.

It should contain:

- project overview;
- architecture map;
- end-to-end workflow;
- technical feature inventory;
- verified contribution map;
- evidence map;
- role-specific positioning;
- resume bullet candidates;
- 30-second and 2-minute pitches;
- STAR stories;
- interview question bank;
- source-code review checklist;
- confidentiality review;
- open questions / unknowns.

## Supporting references

Read these when relevant:

- `references/ownership-model.md`
- `references/packaging-framework.md`
- `references/confidentiality.md`

Use:

- `templates/project_profile.md` for the main output;
- `templates/review_checklist.md` before interviews;
- `scripts/repo_inventory.py` for lightweight local repository inventory;
- `examples/example_project_profile.md` as a synthetic example only.

## Behavior rules

- Begin analysis before asking broad project-summary questions when repository access exists.
- Never fabricate implementation details, metrics, ownership, or design rationale.
- Distinguish clearly among project capability, team contribution, and personal contribution.
- Treat Git history as evidence, not infallible truth; pair it with user confirmation where needed.
- Do not expose company-confidential identifiers or source code in portable outputs.
- If a claim is technically attractive but poorly supported, mark it as high-risk instead of strengthening the wording.
- If the user requests only repository analysis, do not prematurely generate resume bullets.
- If the user requests only packaging, still verify the evidence map first.
