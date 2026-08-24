# Confidentiality Guide

## Default rule

Private repository access does not imply permission to export repository content.

The skill should help the user learn and summarize the project without moving restricted source code or sensitive implementation details outside approved environments.

## Never export by default

- credentials and secrets;
- internal IPs / hosts / URLs;
- customer identifiers;
- non-public source code;
- proprietary datasets;
- private model endpoints;
- exact restricted infrastructure topology;
- unreleased product names;
- confidential business metrics;
- internal ticket links or identifiers.

## Generalization examples

| Sensitive detail | Portable abstraction |
|---|---|
| Internal product codename | internal diagnosis platform |
| Private host / service | internal backend service |
| Customer device ID | target device |
| Proprietary telemetry table | telemetry dataset |
| Internal LLM endpoint | LLM provider |
| Restricted benchmark | internal evaluation set |

## Review marker

When disclosure status is uncertain, preserve the useful concept but mark the detail:

`[REVIEW_CONFIDENTIALITY]`

Do not silently guess that it is safe.
