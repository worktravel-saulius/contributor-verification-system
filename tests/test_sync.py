import json
from pathlib import Path
from unittest.mock import patch

from scripts.github_notebooklm_sync import (
    build_digest,
    is_approved_content_path,
    redact_text,
    select_repositories,
    summarize_pull_request,
)


ROOT = Path(__file__).resolve().parents[1]


def test_repository_filter_is_organization_scoped_and_excludes_archived():
    repositories = [
        {"full_name": "saulius-systems-labs/public", "owner": {"login": "saulius-systems-labs"}},
        {"full_name": "worktravel-saulius/private", "owner": {"login": "worktravel-saulius"}},
        {
            "full_name": "saulius-systems-labs/archived",
            "owner": {"login": "saulius-systems-labs"},
            "archived": True,
        },
    ]

    assert [repo["full_name"] for repo in select_repositories(repositories, "saulius-systems-labs")] == [
        "saulius-systems-labs/public"
    ]


def test_content_filter_allows_only_bounded_root_readme_and_docs_markdown():
    assert is_approved_content_path("README.md", 40_000)
    assert is_approved_content_path("docs/guide/nested.MD", 32)
    assert not is_approved_content_path("src/app.py", 32)
    assert not is_approved_content_path("docs/secrets.txt", 32)
    assert not is_approved_content_path("other/README.md", 32)
    assert not is_approved_content_path("docs/oversized.md", 40_001)


def test_redactor_removes_credentials_contact_data_and_member_fields():
    text = (
        "Contact person@example.invalid or +1 (555) 123-4567\n"
        "api_key: synthetic-secret-value\n"
        "member_email=member@example.invalid\n"
        "Customer support contact: Synthetic Person\n"
        "ghp_abcdefghijklmnopqrstuvwxyz012345"
    )

    redacted = redact_text(text)

    for sensitive_value in (
        "person@example.invalid",
        "555",
        "synthetic-secret-value",
        "member@example.invalid",
        "Synthetic Person",
        "ghp_",
    ):
        assert sensitive_value not in redacted


def test_pull_request_summary_omits_body_and_author():
    summary = summarize_pull_request(
        {
            "number": 12,
            "title": "Synthetic test PR",
            "state": "closed",
            "updated_at": "2026-10-25T00:00:00Z",
            "html_url": "https://github.com/example/repo/pull/12",
            "body": "synthetic member payload",
            "user": {"login": "synthetic-user"},
        }
    )

    assert set(summary) == {"number", "title", "state", "updated_at", "url"}
    assert "synthetic member payload" not in str(summary)
    assert "synthetic-user" not in str(summary)


def test_digest_is_org_scoped_and_labels_repository_content_untrusted():
    repositories = [
        {
            "full_name": "saulius-systems-labs/allowed",
            "owner": {"login": "saulius-systems-labs"},
            "default_branch": "main",
            "html_url": "https://github.com/saulius-systems-labs/allowed",
        },
        {
            "full_name": "worktravel-saulius/not-in-this-digest",
            "owner": {"login": "worktravel-saulius"},
        },
    ]

    def fake_github_get(path, token, query=None):
        if path.endswith("/pulls") or path.endswith("/releases"):
            return []
        return {"tree": [], "truncated": False}

    with patch("scripts.github_notebooklm_sync.github_get", side_effect=fake_github_get):
        digest = build_digest("saulius-systems-labs", repositories, "synthetic-token", "2026-10-25")

    assert "saulius-systems-labs/allowed" in digest
    assert "worktravel-saulius/not-in-this-digest" not in digest
    assert "untrusted source material" in digest


def test_wif_template_pins_exact_repository_ref_and_workflow():
    config = json.loads((ROOT / ".github" / "wif-config-template.json").read_text(encoding="utf-8"))
    condition = config["attribute_condition"]
    expected = (
        "worktravel-saulius/contributor-verification-system/.github/workflows/"
        "notebooklm-github-sync.yml@refs/heads/main"
    )

    assert config["attribute_mapping"]["google.subject"] == "assertion.sub"
    assert config["attribute_mapping"]["attribute.repository"] == "assertion.repository"
    assert config["attribute_mapping"]["attribute.ref"] == "assertion.ref"
    assert config["attribute_mapping"]["attribute.workflow_ref"] == "assertion.workflow_ref"
    assert "worktravel-saulius/contributor-verification-system" in condition
    assert "refs/heads/main" in condition
    assert expected in condition
    assert "SERVICE_ACCOUNT_EMAIL" in config["service_account_impersonation"]["service_account_email"]
    assert "private_key" not in json.dumps(config).lower()


def test_app_manifest_has_only_required_read_permissions():
    manifest = json.loads((ROOT / ".github" / "github-app-permissions.json").read_text(encoding="utf-8"))

    assert manifest["repository_permissions"] == {
        "contents": "read",
        "pull_requests": "read",
    }
    assert manifest["implicit_permissions"] == {"metadata": "read"}
    assert manifest["organization_permissions"] == {}
    assert manifest["subscribed_events"] == []
    assert "discussions" in manifest["excluded_permissions"]


def test_workflow_is_disabled_by_default_and_has_minimum_permissions():
    workflow = (ROOT / ".github" / "workflows" / "notebooklm-github-sync.yml").read_text(encoding="utf-8")

    assert "if: ${{ vars.NOTEBOOKLM_SYNC_ENABLED == 'true' }}" in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "id-token: write" in workflow
    assert "uses: google-github-actions/auth@" in workflow
    assert "permission-contents: read" in workflow
    assert "permission-pull-requests: read" in workflow
    assert "permission-discussions:" not in workflow
    assert "NOTEBOOKLM_SYNC_ENABLED" not in workflow.split("jobs:", 1)[0]


def test_receipt_scaffold_is_empty_and_org_separated():
    for organization in ("saulius-systems-labs", "worktravel-saulius"):
        receipt_dir = ROOT / "00_MANIFESTS" / "receipts" / organization
        assert receipt_dir.is_dir()
        assert sorted(path.name for path in receipt_dir.iterdir()) == [".gitkeep"]
    readme = (ROOT / "00_MANIFESTS" / "README.md").read_text(encoding="utf-8")
    assert "metadata-only" in readme
    assert "not a live Drive receipt" in readme
