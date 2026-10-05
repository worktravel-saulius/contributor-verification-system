# GitHub Copilot Instructions — Contributor Verification System

## Mission

Maintain a **review-first, evidence-led** contributor verification system for WorkTravel Academy. Prioritise small, reversible changes and preserve a clear audit trail.

## Bonus-system boundary

- Treat GitHub pull requests as evidence only; a merged pull request is **not** an automatic credit award.
- Do not create, enable, or modify a GitHub Actions workflow that directly calls a credit-award, approval, redemption, coupon, payout, Wix, or member-update endpoint.
- Do not introduce a generic or long-lived `BONUS_API_TOKEN`, expose secrets, or put credentials in code, issues, logs, fixtures, or documentation.
- Do not infer a member identity from a GitHub login, pull-request title, email-like string, or label. Require an explicit verified mapping.
- New integration work must remain pending-only until the dedicated backend intake endpoint, identity controls, idempotency, policy checks, reviewer flow, and rollback evidence are all present.
- Follow [`docs/GITHUB_BONUS_INTEGRATION_CONTRACT.md`](../docs/GITHUB_BONUS_INTEGRATION_CONTRACT.md) for every GitHub-to-bonus change.

## Change quality

1. Keep changes focused and explain the verification result.
2. Prefer existing repository conventions over new frameworks.
3. Add or update tests for behaviour changes.
4. Do not suppress failing checks, lower security controls, or bypass review merely to make CI pass.
5. Redact identifiers and never copy customer/member payloads into test data or pull-request descriptions.
6. For workflows, use pinned action versions and minimum permissions; request `id-token: write` only after the identity integration is approved.

## Pull-request expectations

- Use the canonical pull-request template.
- Link the governing issue or decision record.
- State whether the change is documentation-only, staged, or production-facing.
- Declare all external side effects explicitly; if none, say `External side effects: none`.

## When uncertain

Stop at a staged plan and request a named owner decision for any change that could grant credits, affect members, change an external integration, or require credentials.
