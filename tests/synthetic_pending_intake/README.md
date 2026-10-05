# Synthetic Pending-Only Intake Reference Harness

**Status:** Local, synthetic, and non-deployable.
**Purpose:** Provide deterministic behaviour tests for the pending-only GitHub intake contract while the canonical bonus-backend source and authenticated repository access remain unavailable.

## What it proves

- source allow-list enforcement by numeric repository ID, name, and workflow identity;
- verified source facts before record creation;
- immutable event identity derived from repository ID, PR number, and merge SHA;
- exact replay returning the same record/receipt;
- `PENDING_REVIEW`, `HELD_IDENTITY`, and `HELD_POLICY` outcomes only; and
- an explicit `external_calls = []` receipt for every test.

## What it does not do

- verify real GitHub OIDC JWT signatures or call GitHub;
- store or access real member data;
- contact a bonus, Wix, coupon, payout, messaging, or reward service; or
- constitute production endpoint code or release authority.

## Run

```bash
python3 -m unittest -v tests.synthetic_pending_intake.test_pending_intake
```

The suite uses no third-party package and no network access.
