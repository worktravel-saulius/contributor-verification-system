import unittest

from tests.synthetic_pending_intake.pending_intake import (
    AllowList,
    IdentityMapping,
    IntakeError,
    PendingOnlyIntake,
    SourceIdentity,
    VerifiedPullRequest,
)

REPO_ID = 1405622651
REPO = "worktravel-saulius/contributor-verification-system"
WORKFLOW_REF = REPO + "/.github/workflows/github-contribution-intake.yml@refs/heads/main"
WORKFLOW_SHA = "b" * 40
AUDIENCE = "wta-contribution-intake-v1"


def source(**overrides):
    values = dict(
        repository_id=REPO_ID,
        repository=REPO,
        workflow_ref=WORKFLOW_REF,
        workflow_sha=WORKFLOW_SHA,
        audience=AUDIENCE,
        event_name="pull_request",
    )
    values.update(overrides)
    return SourceIdentity(**values)


def pr(**overrides):
    values = dict(
        repository_id=REPO_ID,
        repository=REPO,
        number=101,
        merge_sha="a" * 40,
        author_github_id=424242,
        author_login="synthetic-contributor",
        merged=True,
    )
    values.update(overrides)
    return VerifiedPullRequest(**values)


def mapping(**overrides):
    values = dict(github_user_id=424242, member_ref="member-synthetic-001", version=3)
    values.update(overrides)
    return IdentityMapping(**values)


class PendingOnlyIntakeTests(unittest.TestCase):
    def setUp(self):
        self.service = PendingOnlyIntake(
            AllowList(REPO_ID, REPO, WORKFLOW_REF, WORKFLOW_SHA, AUDIENCE)
        )

    def test_valid_mapped_contribution_creates_one_pending_record_without_egress(self):
        record = self.service.intake(source(), pr(), mapping())
        receipt = self.service.receipt(record)
        self.assertEqual(record.state, "PENDING_REVIEW")
        self.assertEqual(self.service.record_count, 1)
        self.assertEqual(receipt["external_calls"], [])
        self.assertNotIn("member_ref", receipt)

    def test_exact_replay_returns_same_record_without_re_evaluating_policy(self):
        first = self.service.intake(source(), pr(), mapping())
        second = self.service.intake(source(), pr(), mapping())
        self.assertEqual(first.intake_id, second.intake_id)
        self.assertEqual(first.receipt_id, second.receipt_id)
        self.assertTrue(second.replayed)
        self.assertEqual(self.service.record_count, 1)
        self.assertEqual(self.service.policy_evaluations, 1)

    def test_unmapped_contributor_is_held_without_member_reference_or_egress(self):
        record = self.service.intake(source(), pr(), None)
        self.assertEqual(record.state, "HELD_IDENTITY")
        self.assertIsNone(record.mapping_version)
        self.assertEqual(record.external_calls, ())

    def test_non_allowlisted_repository_is_rejected_without_record(self):
        with self.assertRaisesRegex(IntakeError, "SOURCE_NOT_ALLOWED"):
            self.service.intake(source(repository_id=999), pr(), mapping())
        self.assertEqual(self.service.record_count, 0)

    def test_altered_workflow_identity_is_rejected_without_record(self):
        with self.assertRaisesRegex(IntakeError, "SOURCE_NOT_ALLOWED"):
            self.service.intake(source(workflow_sha="c" * 40), pr(), mapping())
        self.assertEqual(self.service.record_count, 0)

    def test_invalid_audience_is_rejected_without_record(self):
        with self.assertRaisesRegex(IntakeError, "OIDC_AUDIENCE_INVALID"):
            self.service.intake(source(audience="wrong-audience"), pr(), mapping())
        self.assertEqual(self.service.record_count, 0)

    def test_changed_merge_sha_for_same_pr_is_a_conflict(self):
        self.service.intake(source(), pr(), mapping())
        with self.assertRaisesRegex(IntakeError, "EVENT_TUPLE_CONFLICT"):
            self.service.intake(source(), pr(merge_sha="d" * 40), mapping())
        self.assertEqual(self.service.record_count, 1)

    def test_policy_hold_never_contains_a_credit_amount_or_external_call(self):
        record = self.service.intake(source(), pr(), mapping(), policy_clear=False)
        receipt = self.service.receipt(record)
        self.assertEqual(record.state, "HELD_POLICY")
        self.assertEqual(receipt["external_calls"], [])
        self.assertNotIn("credit_amount", receipt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
