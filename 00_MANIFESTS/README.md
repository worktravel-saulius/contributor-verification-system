# Sanitized sync receipt hierarchy

This directory defines a sanitized placeholder receipt layout for reference. The organization subdirectories are intentionally empty; this repository is permanently non-publishing and does not write receipts. The sole publisher is `saulius-systems-labs/saulius-ai-twin-gemini3x`. Do not place credentials, source text, PR bodies, personal/member data, or unredacted GitHub payloads here.

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

This committed scaffold is not a live Drive receipt and does not assert that WIF or Drive access is configured. Only the sole publisher repository may write to external destinations; enabling a variable in this companion repository cannot trigger a receipt or digest upload.
