# GitHub-to-NotebookLM knowledge sync

**Status: staged implementation; not deployed or verified against Google Drive or NotebookLM.**

The planned workflow produces one redacted Markdown digest per organization, then writes it to a restricted Google Drive folder. NotebookLM can import those Drive files and refresh them when a notebook is opened. This repository does not call a NotebookLM API. A successful workflow run would only prove that the digest reached Drive; NotebookLM import and freshness must be checked separately.

## Data and safety boundaries

- The daily or manually dispatched job dynamically discovers repositories available to a GitHub App installation in `saulius-systems-labs` and `worktravel-saulius`. It includes active repositories owned by the requested organization; it does not use a frozen repository inventory.
- Each digest contains repository names, descriptions, default branches, update dates and URLs; up to five recent PR summaries and five recent release summaries; and up to twenty README/docs Markdown files per repository, each no larger than 40,000 bytes.
- PR bodies, author identities, source code, issue contents, workflow logs and raw GitHub API responses are not included. The script redacts credential patterns, email addresses, phone-like values and lines containing member/customer sensitive fields. Redaction is a safety filter, not a guarantee that arbitrary source text contains no personal or confidential data. Review source repositories and destination-folder access accordingly.
- Repository content is untrusted reference material. A merged PR or a digest entry is not a bonus/credit approval. The sync has no bonus-system endpoint, member-update endpoint, Wix integration, or credit-award side effect.
- GitHub App permissions must be read-only (`contents: read`, `pull_requests: read`); the intended job permissions are `contents: read` and `id-token: write`. App tokens should be scoped to one organization installation and revoked when the job completes.
- Google authentication is intended to use GitHub OIDC with Workload Identity Federation (WIF) and Application Default Credentials (ADC). No service-account JSON key is used or needed.
- The staged workflow is guarded by the repository Actions variable `NOTEBOOKLM_SYNC_ENABLED == 'true'`; leave it unset or `false` to keep the workflow inert. It is not set by this change. The WIF claim mapping template is `.github/wif-config-template.json`, and the minimal GitHub App manifest is `.github/github-app-permissions.json`.
- The App requests `contents: read` for repository discovery, README/docs, and releases, and `pull_requests: read` for PR summaries. `metadata: read` is implicit in GitHub App access. No `discussions`, write, or organization-administration permission is needed.
- The sanitized receipt directory scaffold is in `00_MANIFESTS/`; it contains placeholders only. Receipt metadata must never contain digest source content, credentials, member data, or raw API responses.

## Administrator setup

An administrator for both GitHub organizations and the Google Cloud project must complete these steps before enabling/running the workflow:

1. Create or designate a GitHub App for this repository. Grant only repository **Contents: read-only** and **Pull requests: read-only** permissions; subscribe to no events; install it in both organizations with access to the repositories intended for discovery. Ensure newly created repositories are included if they should be discovered. Store its numeric App ID as the repository Actions variable `GITHUB_SYNC_APP_ID`, and store the App private key as the repository Actions secret `GITHUB_SYNC_APP_PRIVATE_KEY`. Never paste or commit the private key.
2. In Google Cloud, configure a Workload Identity Pool and GitHub Actions OIDC provider. Restrict the provider condition to this repository and trusted `main` branch (for example, repository claim `assertion.repository == 'worktravel-saulius/contributor-verification-system'` and ref claim `assertion.ref == 'refs/heads/main'`). Do not trust arbitrary branches, forks, pull-request refs, or all repositories in an organization.
3. Create or designate a dedicated Google service account with only the access needed to create/update digest files in the two destination folders. Grant it `roles/iam.workloadIdentityUser` to the WIF principal set for the trusted repository (or the narrowly equivalent impersonation binding required by the chosen configuration). Do not grant project-wide editor/owner or broad Drive access.
4. Create two separate, restricted Google Drive destination folders, one per organization. Give the dedicated service account only the required ability to create/update digest files in each folder. Restrict folder membership to intended reviewers/NotebookLM users; do not make either folder public.
5. Set these repository Actions variables, using non-secret resource identifiers only:
   - `GCP_WORKLOAD_IDENTITY_PROVIDER`: full provider resource name, `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID`.
   - `GCP_SERVICE_ACCOUNT`: service-account email used for WIF impersonation.
   - `DRIVE_FOLDER_SAULIUS_SYSTEMS_LABS`: destination folder ID for the first organization.
   - `DRIVE_FOLDER_WORKTRAVEL_SAULIUS`: destination folder ID for the second organization.
6. Confirm the GitHub App is installed in both organizations, the WIF principal condition matches this repository, `refs/heads/main`, and `.github/workflows/notebooklm-github-sync.yml@refs/heads/main`, and the service account can write only to those two destination folders. Keep `NOTEBOOKLM_SYNC_ENABLED` unset while preparing this configuration. Only a separately authorized administrator may set it to `true`, then manually dispatch the workflow and review both resulting digests and Drive access controls before NotebookLM imports them.

The intended workflow must fail visibly when required variables/secrets are absent, source discovery/content requests fail, or Google Drive authentication/upload fails. It must not create cloud resources, credentials, folders, App installations, or NotebookLM notebooks.

## Local checks

The filtering, redaction, WIF-claim, permission, disabled-workflow, and receipt-layout tests use synthetic data:

```bash
python -m pytest tests/test_sync
```

The workflow installs the pinned `google-auth` dependency to obtain ADC from the WIF credentials file generated by `google-github-actions/auth`. No live sync should be tested without the administrator configuration above and explicit authorization to write to the restricted destination folders.
