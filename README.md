# Contributor Verification System

WorkTravel Academy uses this repository to define a **review-first** pathway for recognising verified contributor work.

## Current status

| Capability | Status |
|---|---|
| Contribution guidance and pull-request evidence | **Live** |
| Wix form-to-bonus-system routes | **Live; independently governed** |
| GitHub pull-request credit intake | **Staged — not enabled** |
| Automatic credit awarding from GitHub Actions | **Not enabled** |

> A merged pull request is evidence of work, **not** an automatic financial, loyalty, or credit award. Credit decisions remain subject to approved identity mapping, duplicate prevention, policy rules, and human review.

## Verification flow

1. A contributor opens a focused pull request with the canonical template.
2. Required tests and review evidence are recorded.
3. After merge, an approved GitHub integration may create a **pending** contribution record.
4. A named WorkTravel Academy reviewer verifies the contribution, member identity, eligibility, and evidence.
5. Only the existing, authorised bonus-review process may approve a credit award.

## Credit guidance

The published contribution categories are planning guidance rather than an automatic entitlement:

| Contribution type | Reference credits |
|---|---:|
| Merged feature or stacked pull request | 500 |
| UX or bug-fix contribution | 300 |
| Documentation or tutorial | 250 |
| Course module completion | 200 |
| Peer code review | 150 |

Tier multipliers, caps, final eligibility, and the member-facing value are evaluated by the bonus system at approval time.

## Repository relationship

- [`worktravel-academy-core`](https://github.com/worktravel-saulius/worktravel-academy-core) — programme governance and operating context.
- [`developer-learning-paths`](https://github.com/worktravel-saulius/developer-learning-paths) — learning tracks and contributor-ready materials.
- This repository — verification standards and the staged GitHub-to-bonus integration contract.

## Integration and safety

The integration design, activation gates, data-minimisation rules, and test acceptance criteria are in [`docs/GITHUB_BONUS_INTEGRATION_CONTRACT.md`](docs/GITHUB_BONUS_INTEGRATION_CONTRACT.md).

Do **not** add a workflow that directly awards credits, paste service credentials into a repository, or treat pull-request title/label text as an authorization signal.

## Support

Programme support context: <https://opencollective.com/earn-to-buildincentive-flywhee>

## Reporting concerns

For security-sensitive reports, use the private contact channel described in [`SECURITY.md`](SECURITY.md). Do not include credentials, member data, or exploit details in a public issue.
