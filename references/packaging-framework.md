# Packaging Framework

## Evidence-first transformation

Transform repository facts in this order:

```text
implementation fact
→ engineering mechanism
→ user contribution
→ technical significance
→ measurable project outcome
→ role relevance
→ interview-safe wording
```

Do not jump directly from a filename to a resume bullet.

## Technical significance prompts

For each feature ask:

- What engineering problem did this solve?
- Why was this design chosen?
- What alternatives existed?
- What state does it manage?
- What can fail?
- How is correctness evaluated?
- How is performance observed?
- What are the latency / cost / quality tradeoffs?
- What changed because of this component?

## Agent / LLM framing

Useful categories include:

- orchestration
- tool use
- context management
- evaluation
- observability
- reliability
- structured outputs
- model routing
- prompt design
- latency / cost optimization

A CRUD endpoint should not be relabeled "Agent architecture" unless it actually participates in agent execution, state management, or an LLM workflow.

## Resume structure

Strong bullet:

```text
Action + mechanism + technical scope + outcome
```

Example:

```text
Extended multi-turn agent session persistence by adding conversation-state fields and backend APIs, enabling context continuity across diagnosis interactions.
```

This example is valid only when the underlying evidence supports it.

## Interview structure

Prepare every important claim at four depths:

1. **What:** what the component does.
2. **How:** how requests / data / state move through it.
3. **Why:** design choice and alternatives.
4. **Failure:** edge cases, reliability, evaluation, and tradeoffs.
