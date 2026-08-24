# Repo to Interview Skill

An evidence-first Agent Skill for turning a real software repository into defensible resume and technical-interview material.

It is designed for internships and team projects where the repository contains much more work than one person personally implemented.

## What it does

- inspects a repository before writing career material;
- reconstructs architecture and important execution paths;
- mines technically meaningful Agent / LLM / backend features;
- separates project capabilities from personal contributions;
- attaches code / commit / PR evidence to candidate claims;
- adapts the same project to Agent, LLM application, AI full-stack, or backend roles;
- generates interview questions and a source-code review checklist;
- sanitizes confidential implementation details before portable outputs are produced.

## Why this exists

Normal resume tools usually start from a user's summary. That loses technical detail and makes it easy to overstate team work.

This skill uses the opposite workflow:

```text
repository
   ↓
architecture reconstruction
   ↓
technical feature mining
   ↓
contribution verification
   ↓
evidence map
   ↓
role-oriented packaging
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
    └── repo_inventory.py
```

## Installation

The skill follows the Agent Skills pattern: the workflow lives in `SKILL.md`, with optional supporting references, templates, examples, and scripts.

Copy or install this directory into a Skill-compatible Agent environment such as Codex, then invoke it against the repository you want to analyze.

Example requests:

```text
Use repo-to-interview to analyze this repository for an Agent Engineer role.
```

```text
Analyze the current repository first. Do not write resume bullets yet. Build the architecture map, technical feature inventory, and candidate contribution table.
```

```text
Using the verified contribution map, generate the 10 source-code locations I should review before an Agent Engineer interview.
```

## Recommended workflow for company repositories

Run the skill inside the approved company environment. Do not copy source code out of a restricted environment.

Export only a sanitized project profile containing abstractions, contribution labels, approved metrics, technical mechanisms described at an appropriate level, and interview review topics.

## Ownership model

The skill uses six labels:

- `OWNED`
- `MAJOR_CONTRIBUTOR`
- `CONTRIBUTED`
- `UNDERSTAND_ONLY`
- `UNKNOWN`
- `DO_NOT_CLAIM`

Repository presence is never treated as proof of authorship.

## License

MIT. See [LICENSE](LICENSE).
