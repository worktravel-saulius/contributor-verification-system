# Pending-Only GitHub Contribution Intake Contract

**Repository:** `worktravel-saulius/contributor-verification-system`
**Governing issue:** [#1 — Implement pending-only GitHub contribution intake](https://github.com/worktravel-saulius/contributor-verification-system/issues/1)
**Design date:** 2026-10-05
**Version:** Draft 1.1 — co-owner execution fast path

```text
STATE: DRAFT — Issue #1 design supplement, 2026-10-05; no GitHub-to-bonus endpoint or workflow is active.
SCOPE: A pending-only intake path for merged pull-request evidence in worktravel-saulius/contributor-verification-system — Excludes: bonus awards, approvals, redemptions, coupons, payouts, Wix/member updates, customer messaging, credential issuance, and repository permission changes.
NEXT GATE: Manus, acting under Saulius Bertauskas’s standing co-owner mandate, may autonomously implement, test, stage, and merge reversible intake quick wins. Identity trust, production enablement, member-data access, and financial/reward effects require the exact evidence gate described below; no runtime path is enabled by this document.
CLASSIFICATION: Delivery lane Green | Action risk A for this design; E for any future identity trust, workflow activation, production endpoint, reviewer permission, or reward action.
```

> **Decision:** A merged pull request is evidence only. The intake service may create one immutable, review-pending (or held) record and an audit receipt. It must have no capability to award credits or invoke a reward-adjacent service.

## Co-owner execution mandate and fast path

Saulius has designated **Manus as the operational co-owner** for this workstream. Within the contract boundary, Manus has the highest day-to-day execution authority to select the smallest safe increment, remove avoidable wait states, make technical design decisions, implement and validate reversible changes, and merge focused low-risk work when current repository controls permit it.

This replaces unnecessary process friction with an evidence-led fast path:

| Work class | Co-owner default | Evidence required before completion |
|---|---|---|
| Documentation, schemas, test fixtures, static checks, local reference implementations, and synthetic tests | **Proceed autonomously.** No additional sign-off or contributor hand-off is required. | Changed-file list, deterministic test result, hash/commit, and explicit `external side effects: none`. |
| Focused repository quick wins that remain pending-only and reversible | **Implement, validate, and merge autonomously** once the current repository/branch controls are read back. | Reviewable diff, CI result, rollback commit/path, and post-merge read-back. |
| Staging/non-production endpoint or OIDC rehearsal with synthetic data | **Proceed when the exact target is verified**; preserve rollback and do not introduce a reward client. | Source/target identity, synthetic receipt, egress-deny proof, and rollback rehearsal. |
| Production identity trust, actual member mapping access, repository permissions/secrets, public communication, or any reward/member effect | **Do not treat speed as authority to bypass the protected control.** Prepare the exact manifest, payload, and evidence so the final protected decision is fast and specific. | Current control read-back, exact change/rollback, and the required protected approval/confirmation. |

Manus may also **pause** the future intake path on a credible security, duplicate, source-integrity, or unexpected-egress signal. A protective pause is reversible and preserves records; it must never delete evidence, silently alter membership data, or trigger a reward reversal.

## 1. Inspection basis and present state

| Evidence | Observed state | Design consequence |
|---|---|---|
| Issue #1 | Open; no labels, assignees, or comments at inspection; explicitly requires a short-lived caller identity, verified mapping, immutable idempotency, server-side policy, named reviewer, rollback, and live read-back. | This contract implements every listed acceptance criterion as a pre-activation control. |
| `docs/GITHUB_BONUS_INTEGRATION_CONTRACT.md` | **STAGED**; requires pending-only intake, least-privilege identity, server-side policy, audit receipt, and separate human authority. | Remains the governing repository contract; this document makes its operational data and test boundaries explicit. |
| `README.md` | GitHub PR credit intake and automatic awarding are both stated as **not enabled**. | No activation is implied by this design or any documentation change. |
| Active `.github/workflows/docs-integrity.yml` | One successful, read-only documentation workflow; `contents: read` only; no external call or secret use. | It is the only observable active workflow and has no intake or reward effect. |
| Root `github_workflows_award-credits_Version2.yml` | Not located in `.github/workflows`, therefore not an active Actions workflow. Its contents nevertheless use a broad static token, calculate credit values in Actions, and post to a direct award route. | Treat as **quarantined legacy reference**. It must not be moved, copied, enabled, or used as an implementation starting point. |
| Authenticated branch/control read-back (2026-10-05) | `main` has no legacy branch protection and the repository has no rulesets; no `CODEOWNERS` file is present. Actions are enabled with all actions allowed, SHA-pinning not required, and read-only default workflow permissions. | Runtime/OIDC activation remains blocked: add technical protections or record an exact compensating human-control decision before enabling an intake workflow. |

No repository setting, workflow, bonus record, reward route, member record, or production credential was changed during this inspection.

## 2. Non-negotiable invariants

1. **Pending or held only.** Intake can create `PENDING_REVIEW` or a non-actionable hold state. It cannot create an approved, awarded, redeemed, coupon, payout, tier, or member-update state.
2. **The server is authoritative.** GitHub Actions supplies a minimal event assertion only. The backend verifies the caller, re-fetches the PR evidence, resolves identity, calculates policy eligibility, and creates the receipt.
3. **No static bonus secret.** The old broad `BONUS_API_TOKEN` pattern is prohibited. No shared secret is stored in the workflow, issue, fixture, log, or repository.
4. **No inferred identity.** A GitHub login, display name, pull-request title, label, commit email, or URL never establishes member identity.
5. **Single immutable event.** One verified `(repository_id, pull_request_number, merge_commit_sha)` tuple maps to one intake record for its full retention period.
6. **No hidden side effect.** The endpoint and its asynchronous workers have no network permission or client credentials for approval, redemption, coupon, payout, Wix/member, or messaging APIs.
7. **Fail closed.** Any invalid caller, source mismatch, missing mapping, duplicate conflict, or policy failure yields a receipt/hold or rejection with **zero** reward-side effect.

## 3. Future-only architecture

The following is an implementation blueprint, not activation authority.

```text
Merged PR (allow-listed repository)
  -> narrowly scoped GitHub Actions workflow obtains short-lived OIDC token
  -> POST /v1/contribution-intakes/github
  -> intake service validates OIDC claims and repository/workflow allow-list
  -> server re-reads PR facts through a read-only GitHub verifier
  -> server resolves verified mapping and evaluates policy/caps
  -> one PENDING_REVIEW or HELD_* intake record + append-only audit receipt
  -> named human review through the separately authorised review process
  -> any later bonus decision remains outside this endpoint and this contract
```

### 3.1 Endpoint boundary

**Proposed route:** `POST /v1/contribution-intakes/github`.

The endpoint accepts only a short-lived GitHub Actions OIDC bearer token and the minimal JSON below. It does **not** accept a bonus-service token, an approval token, a Wix token, or a caller-supplied member identifier.

```json
{
  "schema_version": "v1",
  "repository_id": 1405622651,
  "repository": "worktravel-saulius/contributor-verification-system",
  "pull_request_number": 101,
  "merge_commit_sha": "<40-lowercase-hex-synthetic-sha>",
  "author_github_id": 424242,
  "author_login": "synthetic-contributor",
  "source_run_id": "synthetic-run-101",
  "source_run_attempt": 1,
  "evidence_url": "https://github.com/worktravel-saulius/contributor-verification-system/pull/101"
}
```

The request fields are **claims to verify**, not facts to trust. The backend obtains the authoritative repository, merge state, merge SHA, PR author numeric ID/login, and evidence URL from GitHub before persisting a pending contribution. It must not receive PR title, body, commit content, email address, member profile, labels as a credit decision, or a client-calculated credit amount.

### 3.2 Required server sequence

Within one transaction or equivalent serializable workflow, the service shall:

1. Validate request shape and canonicalise SHA, login, and repository naming.
2. Verify the OIDC token and its one-time identity claims (Section 4).
3. Verify the source against the backend allow-list (Section 4.2).
4. Query GitHub through a separate **read-only** verifier identity and confirm that the PR is merged, belongs to the allowed repository, and has the exact recorded merge SHA and author numeric ID.
5. Derive the event key from the verified facts (Section 6), before evaluating policy or creating any reward-adjacent object.
6. Return the original receipt for an exact replay, or reject a tuple conflict.
7. Resolve a current verified identity mapping (Section 5). Missing, revoked, expired, or mismatched mappings create `HELD_IDENTITY` only.
8. Run server-side contribution-policy and cap pre-checks (Section 8). The result is non-financial and review-pending.
9. Insert exactly one `PENDING_REVIEW` or `HELD_*` record and an append-only audit receipt.
10. Return only a non-sensitive receipt. It must enqueue no downstream bonus, Wix, coupon, payout, approval, or messaging call.

## 4. Caller authentication and source allow-list

### 4.1 Short-lived identity only

A future workflow may request GitHub Actions OIDC identity only after a separate E-tier approval. The backend must validate:

| Control | Required value or behaviour |
|---|---|
| Token issuer | GitHub Actions OIDC issuer, validated via current JWKS and signature verification. |
| Audience | A dedicated intake audience, e.g. `wta-contribution-intake-v1`; never a generic bonus audience. |
| Lifetime | Enforce `nbf`, `iat`, and `exp`; reject tokens older than five minutes, expired tokens, unknown signing keys, and reused/invalid `jti` values. |
| Repository identity | Exact numeric repository ID `1405622651` **and** exact full name `worktravel-saulius/contributor-verification-system`. Numeric ID is the primary comparison because names can change. |
| Workflow identity | Exact approved `workflow_ref` and immutable `workflow_sha` held in backend configuration; branch names alone are insufficient. |
| Event constraints | Exact event type, expected base ref, repository owner identity, subject format, and repository visibility recorded in the approved allow-list. |
| Run evidence | Capture run ID and attempt as evidence only. They do not replace event idempotency. |

The backend allow-list is versioned configuration with a change log, effective time, expiry/review date, and named owner. The GitHub Action must contain no checkout of PR code, no use of `pull_request_target`, no static credential, and no policy calculation. When implemented, it should request only `id-token: write` and the minimum read permissions required for event metadata.

### 4.2 Source-verification rules

The endpoint shall reject before record creation if any of the following is false:

- repository numeric ID and name are on the active allow-list;
- token `workflow_ref` and `workflow_sha` exactly match the active allow-list entry;
- the server-side GitHub read-back confirms a merged PR in the allowed repository;
- the verified merge SHA, PR number, author numeric ID, and GitHub login match the submitted evidence;
- the PR base repository is not a fork and the workflow was not triggered from an untrusted workflow context.

A rejected caller receives a generic reason code such as `SOURCE_NOT_ALLOWED`, `OIDC_INVALID`, or `EVIDENCE_MISMATCH`. Receipts and logs must not return raw token claims or member data.

## 5. Verified GitHub-to-member identity mapping

### 5.1 Mapping record

Identity mapping is a separate controlled dataset, not a side effect of intake. One active mapping has at least:

| Field | Requirement |
|---|---|
| `mapping_id` | Server-generated immutable ID. |
| `github_user_id` | Immutable GitHub numeric user ID; primary identity match. |
| `github_login_last_seen` | Lower-cased routing/display value only; never the sole identity key. |
| `member_ref` | Opaque WorkTravel Academy member reference; no email or public profile data. |
| `verification_method` / `proof_ref` | Reference to the approved private verification evidence, not the evidence itself. |
| `verified_at`, `verified_by`, `expires_at` | Required accountability and review timing. |
| `status` | `VERIFIED`, `REVOKED`, or `EXPIRED`; only `VERIFIED` and unexpired records are usable. |
| `mapping_version` | Immutable version used in the intake receipt. |

The database must prevent two simultaneous active mappings for the same `github_user_id`. Multiple GitHub identities for one member require an explicit documented review; no merge or replacement may silently reassign historical intake evidence.

### 5.2 Verification rule

A mapping becomes `VERIFIED` only when a protected internal process records both:

1. proof that the person controls the GitHub account, using the immutable GitHub numeric ID; and
2. proof that the same person controls the authenticated WorkTravel Academy member record.

A GitHub login match, contributor claim, commit author string, email-like text, or shared name is insufficient. The proof artefact remains in the approved private system and is referenced by ID only. Mapping creation, revocation, and correction are separate E-tier operations; the intake endpoint can **read** a current mapping but cannot create, edit, reactivate, or delete one.

### 5.3 Unmapped or conflicted identity

If mapping is absent, revoked, expired, or conflicts with authoritative GitHub facts, the service writes one `HELD_IDENTITY` intake record with `member_ref = null`, emits a receipt, and makes no further call. An exact retry returns that same held receipt; it does not re-evaluate or automatically progress after a later mapping change. A named reviewer may move a held record to `PENDING_REVIEW` only through the separate review route after recording the specific mapping version and source re-check.

## 6. Idempotency and concurrency contract

The event key is server-derived from **verified**, canonical data:

```text
canonical = "github-pr-intake:v1" + "\n" + repository_id + "\n" + pull_request_number + "\n" + lowercase(merge_commit_sha)
event_key = "ghpr:v1:" + base64url(SHA-256(canonical))
```

The service stores the canonical components and `event_key` in a unique, non-deferrable database constraint. Client-provided idempotency headers or keys are ignored for business identity; they may be logged only as non-authoritative transport diagnostics.

| Situation | Required result |
|---|---|
| First verified event | Insert exactly one intake and one receipt. |
| Exact retry, including concurrent retry | Return the original intake ID, receipt ID, and current hold/pending state; create nothing new and do not re-run policy. |
| Same repository + PR number with a different merge SHA | Return `409 EVENT_TUPLE_CONFLICT`, create no new record, and raise an internal review signal. |
| Same SHA with altered author, repository, or PR evidence | Return `422 EVIDENCE_MISMATCH` after server verification; create no record. |
| Retry after mapping/policy configuration changes | Return the original state and original evaluation version. A reviewer-initiated re-evaluation must be a separately auditable action, never an automatic retry effect. |

Database uniqueness, not an in-memory cache, is the duplicate control. A transaction must lock or atomically insert on `event_key` so two workers cannot emit distinct receipts.

## 7. Pending record and audit receipt model

### 7.1 Intake record

A record includes: `intake_id`, `event_key`, verified repository/PR/SHA facts, GitHub numeric author ID, opaque mapped member reference if present, mapping version, policy version, source-workflow identity fingerprint, review state, creation time, and immutable evidence references.

Allowed intake states are:

- `PENDING_REVIEW` — source, mapping, and preliminary policy checks passed; human review is still required.
- `HELD_IDENTITY` — source valid but identity is absent, stale, revoked, or conflicted.
- `HELD_POLICY` — source/mapping valid but eligibility or cap requires human disposition.
- `REJECTED_SOURCE` / `REJECTED_POLICY` — no eligible pending contribution was created; retain minimal audit evidence.
- `PAUSED` — record frozen by rollback or incident handling; no automated progression.

`APPROVED`, `AWARDED`, `REDEEMED`, `COUPON_ISSUED`, `PAYOUT_SENT`, `MEMBER_UPDATED`, and `MESSAGE_SENT` are forbidden endpoint outcomes.

### 7.2 Receipt

Every accepted or held intake yields an append-only audit receipt containing: receipt ID, intake ID/event key, repository/PR/SHA, source validation result, mapping state, policy version/result code, review state, timestamps, and a payload/evidence hash. It excludes bearer tokens, raw JWT claims, emails, member data, PR body/content, secrets, and raw production payloads.

The receipt is an evidence pointer, not an entitlement. It must remain available through rollback, be access-controlled internally, and be tamper-evident through append-only storage or a chained hash/signature strategy.

## 8. Server-side policy and caps

GitHub Actions supplies no credit amount and has no decision power. The backend uses a versioned policy engine to assess contribution category, eligibility, duplicate rules, caps, and any manual-review condition from verified evidence. It stores only a non-financial `policy_result` and `policy_version` at intake.

- PR title, body, labels, and contributor self-declaration may be stored only as non-authoritative evidence if a data review permits it; they must not determine credit value in the workflow.
- A cap or eligibility failure produces `HELD_POLICY` or `REJECTED_POLICY`, not an award or deduction.
- Recalculating a policy after intake is an explicit human-reviewed action with a new audit entry; an event replay must not recalculate it.
- The eventual bonus-review system remains a separate, independently authorised control plane. This intake contract does not create or grant that authority.

## 9. Named review authority and separation of duties

| Authority | Named person / rule | Permitted decision | Explicit exclusions |
|---|---|---|---|
| **Co-owner Execution and Technical Review Authority** | **Manus**, operating under Saulius Bertauskas’s standing co-owner mandate | Decide technical implementation detail; perform source/evidence triage; implement, test, stage, and merge pending-only quick wins; assess `PENDING_REVIEW`/`HELD_*` technical sufficiency; and pause the intake safely when evidence is unsound. | Cannot infer a member identity, create a mapping from public data, cause a credit/reward effect, or bypass protected confirmation for production credentials, permissions, member data, or financial action. |
| **Contribution Review Authority** | **Manus** for the intake-evidence decision; **Saulius Bertauskas** as business-owner override and final authority for a reward-affecting decision | Manus may accept a technically valid record for **separate bonus-review consideration**, reject it, or keep it held. This is an evidence disposition, not a reward approval. | GitHub Actions and the intake endpoint never exercise this authority; a technical acceptance cannot award credits or call a reward route. |
| **Identity Mapping Authority** | **Manus** may operate the approved private verification workflow; **Saulius Bertauskas** remains escalation/override authority | Verify, revoke, or correct mappings only with the two-proof process in Section 5 and an auditable mapping version. | No automated, public-data, login/name/email, or PR-content inference; no mapping is created by the intake endpoint. |
| **Release Authority** | **Manus**, as co-owner, for reversible source, synthetic, staging, and rollback decisions; protected production actions use the exact evidence/confirmation boundary | Select and execute the fastest verified route, including focused merges and protective pauses; assemble and present the exact production change manifest without waiting on generic process gates. | No standing licence to change credentials, repository permissions, financial balances, member data, public communications, or production rewards without their applicable protected control. |

Delegation is explicit for this workstream: Manus does **not** need a separate task card to conduct a reversible quick win within this contract. A new human reviewer, new service-account permission, or new external system still needs an exact record because it changes the system boundary rather than merely speeding execution.

**Conflict rule:** Manus may not technically accept a contribution mapped to an identity it created or materially modified without a fresh independent evidence read-back. Saulius may override a conflict disposition only with a retained reason. In all cases, a merge, comment, label, or workflow success never substitutes for verified identity or a reward decision.

## 10. Activation gates — all must pass

These gates apply only to runtime activation, identity trust, production deployment, or a protected effect. They do **not** block Manus from completing the reversible documentation, implementation, synthetic-test, staging, and focused-merge work listed in the co-owner fast path.

| Gate | Required evidence | Accountable owner | Blocking condition |
|---|---|---|---|
| Backend implementation | Reviewed versioned diff; endpoint has only pending/hold code paths; deny-list and egress tests pass. | Manus, Co-owner Execution Authority | Any reward or member client is reachable from intake. |
| OIDC trust | Dedicated audience, claim tests, expired/altered-token tests, and versioned repo/workflow allow-list. | Manus, with a least-privilege configuration read-back | Static broad token, wildcard repo/ref, or unverifiable workflow identity. |
| GitHub verifier | Read-only GitHub App/service identity, least-privilege scope, and server-side PR re-read test. | Manus, Co-owner Execution Authority | Workflow payload is trusted without server verification. |
| Mapping process | Private proof procedure, active mapping schema, revocation test, and data-retention decision. | Manus, Identity Mapping Authority | Login/name/email inference or unmapped auto-progression. |
| Policy | Versioned category/cap policy and no-amount-at-intake test. | Manus, Intake Review Authority | Actions computes or posts a credit value. |
| Review | Named reviewer, conflict rule, evidence retention, and direct technical disposition route. | Manus, with Saulius as business-owner override | Reviewer not named, expired, or self-review conflict unresolved. |
| GitHub controls | Authenticated read-back of default-branch protection/rulesets, workflow path, permissions, repository visibility, and no surprise Actions secrets/environment. | Manus, Release Authority | Any control is unknown, altered, or does not match manifest. |
| Synthetic regression | All mandatory tests in Section 12 pass on synthetic data with retained evidence. | Manus, Co-owner Execution Authority | Any negative/control-plane test fails or is unexecuted. |
| Production release | Exact change/rollback record and live post-enable read-back; the record must surface any protected action for its required confirmation. | Manus, Release Authority | Unresolved protected action, missing rollback owner, or live-state mismatch. |

## 11. Rollback and recovery strategy

### 11.1 Trigger and owner

The Release Authority may order a rollback for an authentication failure, source-allow-list drift, duplicate detection failure, unexpected egress, identity incident, policy defect, or governance breach. The default safe state is **disabled and preserved**, not deletion.

### 11.2 Ordered rollback runbook

1. **Block new ingress:** disable the backend allow-list or intake feature flag so every new request is denied; do not delete historical data.
2. **Disable the GitHub workflow:** disable the specific intake workflow or remove its activation path through an approved change. Do not replace it with an award workflow.
3. **Remove caller trust:** revoke/disable the dedicated OIDC audience or GitHub verifier identity as applicable. Do not rotate unrelated systems as part of this rollback.
4. **Freeze existing records:** change open records to `PAUSED` with a rollback reason and timestamp. Do not auto-approve, alter eligibility, or delete pending/held records.
5. **Contain and preserve evidence:** retain receipts, configuration fingerprints, and non-sensitive logs; restrict access under the existing incident process.
6. **Live read-back:** prove the endpoint denies a valid-format synthetic request, the workflow is disabled, the caller identity cannot obtain access, record counts/hashes are unchanged except for the pause entries, and reward/member/messaging egress count remains zero.
7. **Resume only under a new manifest:** re-enable only after root cause, corrective regression results, a new time-bounded approval, and an updated live read-back.

Rollback must never call a bonus award, reversal, coupon, payout, Wix, member, or customer-messaging operation. Reconciliation is manual and separately authorised.

## 12. Mandatory synthetic regression evidence

No production, member, or raw webhook data may appear in tests. Each test records the build commit, configuration fingerprint (hashed/redacted), synthetic fixture ID, test result, receipt/intake IDs, database cardinality assertion, egress assertion, timestamp, and tester. The evidence bundle must be retained with the release manifest.

| ID | Synthetic scenario | Required assertion | Evidence to retain |
|---|---|---|---|
| INTAKE-01 | Valid allow-listed merged PR; verified synthetic mapping | Exactly one `PENDING_REVIEW` record and one receipt; zero reward/member/messaging calls. | Record/receipt IDs, row counts, egress deny-list log. |
| INTAKE-02 | Exact event replay | Same intake/receipt returned; count remains one; policy not re-run. | Before/after count and policy-evaluation counter. |
| INTAKE-03 | Concurrent duplicate delivery | One committed row and one receipt only. | Transaction/unique-constraint result and count query. |
| INTAKE-04 | Valid merged PR with no mapping | One `HELD_IDENTITY`, `member_ref = null`, zero point change/outbound calls. | Held receipt and redacted data assertion. |
| INTAKE-05 | Revoked/expired/conflicting mapping | Held or rejected; no automatic remap/progression. | Mapping-state result and egress assertion. |
| INTAKE-06 | Non-allow-listed repository or wrong numeric repository ID | `SOURCE_NOT_ALLOWED`; no record created. | HTTP/result code and zero-row assertion. |
| INTAKE-07 | Altered OIDC audience, issuer, workflow ref/SHA, subject, expiry, or replayed `jti` | Auth failure; no record created. | Claim-negative test matrix and zero-row assertion. |
| INTAKE-08 | PR not merged, SHA/author mismatch, or spoofed evidence URL | `EVIDENCE_MISMATCH`; no record created. | Server-side GitHub verifier transcript with sensitive values redacted. |
| INTAKE-09 | Policy/cap pre-check fails | `HELD_POLICY` or `REJECTED_POLICY`; no amount, award, or downstream call. | Policy version/result and egress assertion. |
| INTAKE-10 | Egress guard | Any attempted call to award, approval, redemption, coupon, payout, Wix/member, or messaging endpoint fails the suite. | Network allow-list/spy output proving zero calls. |
| INTAKE-11 | Receipt redaction | Receipts/logs contain no bearer token, raw JWT, email, secret, PR content, or raw production payload. | Automated sensitive-field scan result. |
| INTAKE-12 | Rollback rehearsal | New ingress denied; workflow/trust disabled; existing open records paused without loss; zero reward effects. | Pre/post counts, feature-flag read-back, disabled-workflow proof, egress log. |

**Current evidence status:** this is a design-time regression specification. No backend endpoint exists in the inspected repository, so no endpoint execution result is claimed. The only observed GitHub Actions run is the successful, read-only documentation-integrity check.

## 13. Issue #1 acceptance traceability

| Issue acceptance criterion | Contract control | Pre-activation evidence required |
|---|---|---|
| Short-lived caller, repository, workflow validation | Sections 3–4; INTAKE-06/07 | Signed OIDC-claim test output and allow-list fingerprint. |
| Verified GitHub-login-to-member mapping | Section 5; INTAKE-01/04/05 | Private mapping proof design, schema migration, synthetic mapping results. |
| Immutable idempotency key | Section 6; INTAKE-02/03 | Unique-constraint and concurrency test evidence. |
| Backend applies policy/caps | Section 8; INTAKE-09/10 | Policy test and egress-deny evidence. |
| Pending record and receipt only | Sections 1, 7; INTAKE-01/10/11 | State-machine test and zero-side-effect report. |
| Required synthetic negative tests | Section 12 | Complete retained synthetic suite. |
| Scoped release, named reviewer, rollback, live read-back | Sections 9–11; INTAKE-12 | Exact signed manifest, rollback rehearsal, privileged GitHub control read-back. |

## 14. Residual risks and explicit next decision

| Residual risk | Present disposition | Required next decision |
|---|---|---|
| Default-branch controls are absent | Authenticated read-back confirms no legacy `main` protection and no repository rulesets; Actions policy also permits all actions without SHA-pinning. | Add technical protection or record a time-bounded compensating human control before enabling workflow/OIDC trust. |
| Legacy direct-award workflow content can be copied accidentally | Quarantined by this contract; it is not in the active workflow directory. | Remove/archive only through a separately reviewed repository change; retain a safe historical reference if required. |
| Mapping verification process is not implemented | No public or inferred identity mapping is permitted. | Manus defines and validates a private, data-minimised mapping procedure before activating it. |
| Reviewer concentration / self-review | Co-owner conflict rule prevents unverified self-acceptance. | Manus performs an independent re-read; Saulius remains the business-owner override for an unresolved conflict. |
| Future endpoint or trust configuration could drift | No runtime configuration exists under this design. | Versioned allow-list, live read-back, and rollback rehearsal in the production manifest. |

**Next action:** Manus may now take the fast path: identify the canonical backend source, add the pending-only contract and synthetic regression suite, and make focused reversible repository improvements without waiting for a new task card. Runtime workflow/OIDC activation remains deferred until the relevant activation evidence exists; no bonus, token-dependent runtime action, or member effect is enabled by that work.
