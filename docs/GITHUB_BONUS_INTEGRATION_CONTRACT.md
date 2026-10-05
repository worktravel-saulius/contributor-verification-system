# GitHub Contribution Intake Contract

**Status:** STAGED — no production GitHub-to-bonus credit award is enabled.

## Purpose

Create a controlled pathway from a merged GitHub pull request to a **pending** contribution record for WorkTravel Academy review. The pathway must never award points solely because a pull request is merged.

## Non-negotiable controls

1. **Identity mapping first.** A GitHub login must resolve to an explicit, verified WorkTravel Academy member identifier. Unmapped accounts are held for review.
2. **Deterministic idempotency.** Use an immutable key derived from the repository identifier, pull-request number, and merge commit SHA. A retried event must not create a second record.
3. **Pending-only intake.** The GitHub integration may create a record with `pending` status only. A separate authorised reviewer approves or rejects it.
4. **Server-side policy.** Point categories, eligibility, caps, tier calculations, and labels are decided by the bonus service; do not calculate or trust them in GitHub Actions.
5. **Minimal data.** Send only repository identity, PR number, merge SHA, GitHub login, evidence URL, contribution category, and the resolved member ID. Do not send secret values, commit contents, customer data, or email addresses unless the backend explicitly requires them and a data review approves it.
6. **Credential isolation.** Do not use a long-lived broad `BONUS_API_TOKEN`. The production route must authenticate GitHub using a dedicated, least-privilege identity mechanism and verify issuer, audience, repository, and workflow reference server-side.
7. **Human authority.** Awards that affect loyalty points, coupons, payouts, customer communication, or eligibility must remain behind the authorised bonus review route.

## Required backend contract

Before any workflow is enabled, the bonus service must expose a dedicated GitHub contribution-intake endpoint with all of the following:

- authenticated caller verification and repository/workflow allow-list;
- verified GitHub-login-to-member mapping;
- immutable idempotency key;
- server-side contribution policy validation;
- a pending contribution record only;
- structured audit receipt containing the event key and review state; and
- no Wix loyalty, coupon, email, payout, or tier side effect during intake.

The endpoint must reject missing or invalid identity mappings and must not share a route or secret with Wix automations.

## Activation gates

| Gate | Evidence required | Owner |
|---|---|---|
| Contract implementation | Versioned backend change and reviewed diff | Technical owner |
| Authentication | Dedicated least-privilege identity plus negative tests | Security/technical owner |
| Identity mapping | Verified member mapping strategy and mismatch handling | Programme owner |
| Idempotency | Replayed event creates no duplicate submission | Technical owner |
| Policy | Approved credit category table and cap handling | Programme owner |
| Review workflow | Named reviewer, approval route, and audit retention | Operating owner |
| Non-production test | Synthetic mapped member, pending-only receipt, no reward side effect | Technical owner |
| Production release | Explicit scoped approval, rollback, and live read-back | Saulius / release owner |

## GitHub workflow behaviour after activation

The future workflow may listen for a merged pull request in a specific allow-listed repository. It must:

1. request a short-lived identity token;
2. submit the smallest permitted payload to the dedicated intake endpoint;
3. accept a `pending` receipt only;
4. surface a non-sensitive run summary; and
5. fail closed on authentication, mapping, policy, or idempotency errors.

It must not call administrative approval, member, redemption, Wix, coupon, or payout interfaces.

## Test plan

- Merge event from an allow-listed repository and mapped synthetic contributor creates exactly one pending record.
- Retrying the same delivery creates no second record.
- Unmapped contributor is rejected/held without points.
- Non-allow-listed repository and altered workflow identity are rejected.
- Existing review action remains required for any award.
- Test output contains no secret, member email, or raw webhook payload.

## Rollback

Disable the GitHub workflow and revoke the dedicated caller identity. No existing contribution record should be auto-approved, altered, or deleted as part of rollback.
