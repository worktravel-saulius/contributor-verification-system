# Sanitized sync receipt hierarchy

This directory defines the safe receipt layout for the staged GitHub-to-NotebookLM sync. The organization subdirectories are intentionally empty placeholders; do not place credentials, source text, PR bodies, personal/member data, or unredacted GitHub payloads here.

Expected private Google Drive receipt layout:

```text
00_MANIFESTS/
  receipts/
    saulius-systems-labs/
      YYYY-MM-DD/
        manifest.json
        source-inventory.json
        redaction-summary.json
        upload-receipt.json
    worktravel-saulius/
      YYYY-MM-DD/
        manifest.json
        source-inventory.json
        redaction-summary.json
        upload-receipt.json
```

Receipt files are metadata-only: workflow/revision identifiers, timestamps, counts, redaction outcome counts, and a non-secret destination file identifier where required. Never include file content, access tokens, private keys, emails, names, GitHub user identities, PR bodies, customer/member payloads, or raw API responses.

This committed scaffold is not a live Drive receipt and does not assert that WIF or Drive access is configured. External receipt writes remain disabled unless an administrator deliberately enables the workflow after reviewing the WIF policy, App installation, and restricted Drive folders.
