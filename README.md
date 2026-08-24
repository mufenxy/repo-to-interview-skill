# Repo to Interview Skill

An Agent Skill for turning a real team software repository into technically defensible resume and interview material.

Version 0.2 focuses on static repository analysis rather than fine-grained authorship inference.

## What it does

- parses Python with the standard-library AST;
- parses TypeScript / TSX with the TypeScript Compiler API;
- builds internal import graphs;
- builds a conservative static call graph with confidence levels;
- discovers representative Agent / LLM execution chains;
- calculates an explainable 0-100 interview-value score for source files;
- generates a first-pass `.repo_to_interview/project_profile.md`;
- ranks the source files you should review before an interview;
- keeps portable outputs sanitized for company-project use.

## Default assumption

The repository is treated as a team project in which the user participated in development.

The skill does not try to infer per-file authorship, commit ownership, or exact organizational boundaries unless explicitly requested. It avoids unsupported claims of sole implementation or leadership, while allowing the user to discuss the architecture and mechanisms they participated in building.

## Pipeline

```text
repository
   ↓
Python / TypeScript AST analysis
   ↓
import graph + call graph
   ↓
Agent execution-chain discovery
   ↓
interview-value scoring
   ↓
targeted source review
   ↓
project_profile.md
   ↓
resume + interview preparation
```

## Repository structure

```text
repo-to-interview-skill/
├── SKILL.md
├── README.md
├── LICENSE
├── references/
│   ├── confidentiality.md
│   ├── ownership-model.md
│   └── packaging-framework.md
├── templates/
│   ├── project_profile.md
│   └── review_checklist.md
├── examples/
│   └── example_project_profile.md
└── scripts/
    ├── analyze_repo.py
    ├── ts_ast_analyzer.cjs
    ├── generate_project_profile.py
    └── repo_inventory.py
```

## Quick start

Run the Skill against a local repository:

```bash
python scripts/analyze_repo.py /path/to/target-repo
python scripts/generate_project_profile.py /path/to/target-repo
```

Outputs:

```text
/path/to/target-repo/.repo_to_interview/
├── analysis.json
└── project_profile.md
```

Then ask your coding Agent to inspect the P0/P1 files and refine the generated profile.

Example:

```text
Use repo-to-interview on the current repository for an Agent Engineer role.
Run the static analysis pipeline first, inspect the highest interview-value files,
verify the representative Agent execution chains, and refine project_profile.md.
```

## Python AST analysis

`scripts/analyze_repo.py` uses Python's built-in `ast` module to collect:

- imports;
- classes / functions / methods;
- decorators;
- line ranges;
- function and method calls;
- Agent / LLM / architecture signals.

One syntax error does not stop the entire repository analysis.

## TypeScript / TSX AST analysis

`scripts/ts_ast_analyzer.cjs` uses the official TypeScript Compiler API.

It resolves the `typescript` package in this order:

1. target repository `node_modules`;
2. Skill directory `node_modules`;
3. normal Node module resolution.

If TypeScript is unavailable, Python analysis still completes and the missing TS analysis is reported explicitly.

## Import and call graphs

The analyzer resolves internal imports conservatively and builds file-level import edges.

The static call graph records confidence:

- `high` — same-file, unambiguous symbol match;
- `medium` — unambiguous repository-wide symbol match;
- `low` — ambiguous heuristic match.

Dynamic dispatch, dependency injection, event buses, decorators, reflection, and runtime tool registries may not be fully represented.

## Agent execution-chain tracing

The analyzer searches for likely entry points and high-signal Agent/LLM mechanisms, then traces representative paths through the call graph.

Typical output may resemble:

```text
request handler
→ conversation service
→ diagnosis agent
→ tool registry
→ tool execution
→ model decision
→ state persistence / evaluation / tracing
```

The goal is not to enumerate every runtime path. It is to find a few paths worth understanding deeply for interviews.

## Interview-value score

Every analyzed source file receives an explainable score from 0-100:

| Component | Max |
|---|---:|
| Agent / LLM relevance | 30 |
| Execution-path importance | 25 |
| Graph centrality | 20 |
| Architecture signal | 15 |
| Implementation depth | 10 |

Penalties apply to tests/fixtures, parse failures, and low-value files.

Suggested bands:

- `85-100`: must review;
- `70-84`: high priority;
- `50-69`: useful context;
- `<50`: background unless needed for a specific story.

The score is a source-review heuristic, not a code-quality metric.

## Automatic project profile

`generate_project_profile.py` converts `analysis.json` into a first-pass profile containing:

- repository/static-analysis summary;
- import graph hubs;
- call graph summary;
- representative Agent execution chains;
- technical feature inventory;
- ranked interview-value files;
- code review checklist;
- static-analysis limitations;
- placeholders for role-specific narrative, resume bullets, pitches and STAR stories.

The Agent should manually read high-value files before turning those placeholders into polished claims.

## Company repository workflow

Run the Skill inside the approved company environment. Do not copy restricted source code outside that environment.

A safe workflow is:

```text
company repository
   ↓
local Skill analysis
   ↓
.repo_to_interview/project_profile.md
   ↓
sanitation / confidentiality review
   ↓
portable project notes
```

Do not export source snippets, credentials, internal URLs/IPs, customer data, or private infrastructure details.

## License

MIT. See [LICENSE](LICENSE).
