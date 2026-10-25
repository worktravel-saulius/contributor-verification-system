# GitHub-to-NotebookLM publisher boundary

**Status: this repository is a permanently non-publishing companion.** It does not authenticate to Google, write to Drive, or call a NotebookLM API. Its scheduled/manual workflow only runs local validation tests. Setting `NOTEBOOKLM_SYNC_ENABLED` here has no effect; no workflow step reads that variable.

The sole scheduled publisher is [`saulius-systems-labs/saulius-ai-twin-gemini3x`](https://github.com/saulius-systems-labs/saulius-ai-twin-gemini3x), using `.github/workflows/notebooklm-github-sync.yml` on `refs/heads/main`. Only that repository may receive the WIF trust binding or Drive-publishing credentials. This repository must never be added to the WIF principal set or configured with publisher secrets.

## Companion repository behavior

- `.github/workflows/notebooklm-github-sync.yml` runs only `python -m pytest tests/test_sync.py`; it has `contents: read` and no `id-token: write`.
- The workflow has no Google authentication action, GitHub App token creation, secrets/variables, Drive request, or digest upload step. It cannot publish if an enable variable is accidentally set.
- `scripts/github_notebooklm_sync.py` provides the content-selection, redaction, and digest-building logic used by local synthetic tests. It has no executable entry point, Google auth dependency, or Drive upload function.
- `.github/wif-config-template.json` and `.github/github-app-permissions.json` are reference manifests for the sole publisher only. The WIF claims must not grant this companion repository access.
- `00_MANIFESTS/` contains sanitized placeholders and documentation only. It does not create or write receipts.

The content-selection tests model the approved publisher's intended input boundary: active repositories from one named organization, repository metadata, up to five PR/release summaries, and bounded README/docs Markdown. PR bodies, author identities, source code, issue contents, and raw API responses are excluded. Redaction covers credential patterns, email and phone-like values, and member/customer-sensitive context; it is a filter, not a guarantee that arbitrary source text is safe. GitHub content remains untrusted reference material, never authorization to award credits.

## Sole-publisher administrator setup

These setup requirements apply only to administrators configuring `saulius-systems-labs/saulius-ai-twin-gemini3x`:

1. Restrict the GitHub Actions OIDC provider to the exact repository, `refs/heads/main`, and `saulius-systems-labs/saulius-ai-twin-gemini3x/.github/workflows/notebooklm-github-sync.yml@refs/heads/main`, as specified in `.github/wif-config-template.json`. The discovered pool name is `github-actions-release-control`; provider resource identifiers still need to be confirmed by the cloud administrator.
2. Bind only that publisher repository's principal set to the dedicated service account. Do not bind `worktravel-saulius/contributor-verification-system`.
3. Configure publisher-only GitHub App access with `contents: read` and `pull_requests: read` plus implicit `metadata: read`. Do not grant write, discussions, or organization-administration scopes.
4. Configure the publisher's non-secret provider/service-account/folder identifiers and its GitHub App credential in that publisher repository only. Restrict each Drive destination folder to intended reviewers/NotebookLM users. Do not commit or paste credential values.
5. The publisher may be enabled only after the trust condition, App installation, and restricted folder access have been independently verified. This repository remains non-publishing regardless of that decision.

No cloud resource, credential, folder, App installation, Drive write, or NotebookLM import was created or verified by this repository's implementation.

## Local validation

The tests use synthetic data and make no network, cloud-authentication, or Drive calls:

```bash
python -m pytest tests/test_sync.py
```

The same tests are run by the companion safety-check workflow.
