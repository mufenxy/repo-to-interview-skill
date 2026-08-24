# Ownership Model

## Goal

Keep project presentation accurate while still allowing a user to explain a large team system with appropriate technical depth.

## Labels

### OWNED

Use when the user independently implemented or designed the substantial part of the component or mechanism.

Safe wording may include:

- designed
- implemented
- built
- introduced
- led the implementation of

### MAJOR_CONTRIBUTOR

Use when the user made a large contribution but the work was collaborative.

Prefer:

- drove the implementation of
- implemented major parts of
- co-designed
- led / contributed substantially to

Avoid implying sole authorship.

### CONTRIBUTED

Use for bounded meaningful work.

Prefer:

- contributed to
- implemented the X portion of
- extended
- integrated
- added support for

### UNDERSTAND_ONLY

The user can discuss the component as project context but should not claim implementation ownership.

Prefer:

- the system uses
- the architecture includes
- our project adopted

### UNKNOWN

Evidence is incomplete. Ask for verification before converting the item into a first-person claim.

### DO_NOT_CLAIM

Use when attribution would be misleading, evidence conflicts, or the content is unsafe to disclose.

## Evidence priority

Strongest to weakest:

1. user confirmation tied to a concrete module / task;
2. attributable PR with meaningful diff;
3. attributable commits with meaningful changes;
4. issue / task record linking user and component;
5. surrounding repository structure only.

Level 5 is not authorship evidence.

## Interview risk

A claim's risk increases when:

- ownership is weak;
- mechanism is not understood;
- code path is complex;
- user cannot explain design alternatives;
- metrics are system-level but wording sounds personal;
- the component was built by another team;
- confidentiality constraints prevent meaningful explanation.

High-value + high-risk claims should be studied before use, not automatically included.
