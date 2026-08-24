# Participation and Wording Model

## Default assumption

Treat the repository as a team project in which the user participated in development.

Do **not** automatically infer fine-grained authorship from Git history, file ownership, commit counts, or blame data unless the user explicitly asks for attribution analysis.

The purpose of this skill is to identify technically meaningful mechanisms and prepare the user to explain them accurately, not to reconstruct organizational ownership boundaries.

## Safe default framing

When discussing the project as a whole, prefer wording such as:

- the project implements ...
- the system uses ...
- our system / our project ...
- I participated in the development of ...
- I worked on ...
- I contributed to ...

When the user explicitly states stronger responsibility for a concrete area, stronger verbs may be used:

- designed
- implemented
- built
- drove
- led the implementation of

Do not invent sole ownership or leadership.

## What repository evidence proves

Repository evidence can support:

- that a mechanism exists;
- how the mechanism works;
- where it is implemented;
- which modules interact;
- what runtime path static analysis suggests;
- which source files are worth studying.

Repository presence alone does **not** prove:

- sole authorship;
- leadership;
- who made the architectural decision;
- who owns the production outcome.

The skill therefore avoids automatic per-module ownership labels by default.

## Interview defensibility

For any strong project statement, the user should be able to answer:

1. What does this component do?
2. How does the request/data/state flow through it?
3. Why is this design useful or what tradeoff does it address?
4. What can fail and how is that observed or handled?
5. Which source files/functions support the explanation?

If the Agent cannot establish the mechanism from code or docs, downgrade confidence rather than strengthening the wording.

## Optional attribution mode

Only when explicitly requested may the Agent inspect:

- git log;
- git blame;
- pull requests;
- issues/task records;
- user-provided contribution notes.

Even then, treat Git metadata as evidence rather than infallible ground truth.
