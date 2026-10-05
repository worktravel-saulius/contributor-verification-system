"""Synthetic-only reference model for a pending GitHub contribution intake.

No network calls, credentials, member data, or reward clients are present.  This
models the contract's source verification, deterministic idempotency, mapping
hold, and policy hold behaviours for regression tests.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Dict, Literal, Optional
from uuid import NAMESPACE_URL, uuid5

ReviewState = Literal["PENDING_REVIEW", "HELD_IDENTITY", "HELD_POLICY"]


@dataclass(frozen=True)
class SourceIdentity:
    repository_id: int
    repository: str
    workflow_ref: str
    workflow_sha: str
    audience: str
    event_name: str
    token_valid: bool = True


@dataclass(frozen=True)
class VerifiedPullRequest:
    repository_id: int
    repository: str
    number: int
    merge_sha: str
    author_github_id: int
    author_login: str
    merged: bool


@dataclass(frozen=True)
class IdentityMapping:
    github_user_id: int
    member_ref: str
    version: int
    status: Literal["VERIFIED", "REVOKED", "EXPIRED"] = "VERIFIED"


@dataclass(frozen=True)
class AllowList:
    repository_id: int
    repository: str
    workflow_ref: str
    workflow_sha: str
    audience: str


@dataclass
class IntakeRecord:
    intake_id: str
    receipt_id: str
    event_key: str
    state: ReviewState
    repository_id: int
    pull_request_number: int
    merge_sha: str
    author_github_id: int
    mapping_version: Optional[int]
    policy_version: str
    replayed: bool = False
    external_calls: tuple[str, ...] = ()


class IntakeError(ValueError):
    """A deterministic contract violation with no record creation."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class PendingOnlyIntake:
    """In-memory implementation of the contract's irreversible-effect boundary."""

    def __init__(self, allow_list: AllowList, policy_version: str = "policy-v1") -> None:
        self.allow_list = allow_list
        self.policy_version = policy_version
        self._records: Dict[str, IntakeRecord] = {}
        self.policy_evaluations = 0

    @staticmethod
    def event_key(pr: VerifiedPullRequest) -> str:
        canonical = "\n".join(
            ("github-pr-intake:v1", str(pr.repository_id), str(pr.number), pr.merge_sha.lower())
        )
        return "ghpr:v1:" + sha256(canonical.encode("utf-8")).hexdigest()

    def _verify_source(self, source: SourceIdentity, pr: VerifiedPullRequest) -> None:
        allow = self.allow_list
        if not source.token_valid:
            raise IntakeError("OIDC_INVALID")
        if source.audience != allow.audience:
            raise IntakeError("OIDC_AUDIENCE_INVALID")
        if source.event_name != "pull_request":
            raise IntakeError("EVENT_NOT_ALLOWED")
        if (
            source.repository_id != allow.repository_id
            or source.repository != allow.repository
            or source.workflow_ref != allow.workflow_ref
            or source.workflow_sha != allow.workflow_sha
        ):
            raise IntakeError("SOURCE_NOT_ALLOWED")
        if pr.repository_id != allow.repository_id or pr.repository != allow.repository:
            raise IntakeError("EVIDENCE_MISMATCH")
        if not pr.merged or len(pr.merge_sha) != 40 or any(c not in "0123456789abcdef" for c in pr.merge_sha.lower()):
            raise IntakeError("EVIDENCE_MISMATCH")

    def intake(
        self,
        source: SourceIdentity,
        pr: VerifiedPullRequest,
        mapping: Optional[IdentityMapping],
        *,
        policy_clear: bool = True,
    ) -> IntakeRecord:
        """Create one pending/held record, or return the original exact replay."""
        self._verify_source(source, pr)
        key = self.event_key(pr)
        existing = self._records.get(key)
        if existing:
            existing.replayed = True
            return existing

        # A same-repository/PR number with a changed merge SHA is a conflict,
        # never a second contribution.
        for record in self._records.values():
            if record.repository_id == pr.repository_id and record.pull_request_number == pr.number:
                raise IntakeError("EVENT_TUPLE_CONFLICT")

        self.policy_evaluations += 1
        if not mapping or mapping.github_user_id != pr.author_github_id or mapping.status != "VERIFIED":
            state: ReviewState = "HELD_IDENTITY"
            mapping_version: Optional[int] = None
        elif not policy_clear:
            state = "HELD_POLICY"
            mapping_version = mapping.version
        else:
            state = "PENDING_REVIEW"
            mapping_version = mapping.version

        # UUIDv5 is deterministic from the event key; production may use a
        # different opaque identifier, but the event key remains the authority.
        intake_id = str(uuid5(NAMESPACE_URL, "intake:" + key))
        receipt_id = str(uuid5(NAMESPACE_URL, "receipt:" + key))
        record = IntakeRecord(
            intake_id=intake_id,
            receipt_id=receipt_id,
            event_key=key,
            state=state,
            repository_id=pr.repository_id,
            pull_request_number=pr.number,
            merge_sha=pr.merge_sha.lower(),
            author_github_id=pr.author_github_id,
            mapping_version=mapping_version,
            policy_version=self.policy_version,
        )
        self._records[key] = record
        return record

    def receipt(self, record: IntakeRecord) -> dict:
        """Return the non-sensitive receipt surface; never expose member data."""
        return {
            "receipt_id": record.receipt_id,
            "intake_id": record.intake_id,
            "event_key": record.event_key,
            "review_state": record.state,
            "policy_version": record.policy_version,
            "external_calls": list(record.external_calls),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    @property
    def record_count(self) -> int:
        return len(self._records)
