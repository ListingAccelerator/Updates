# Listing Accelerator — updates

This is where the Listing Accelerator program checks for updates.

- `stable/` — the current update. The program reads `latest.json`, checks
  its signature against the key built into the program, then downloads and
  checks the zip.
- Every update is signed by GitHub using the repository secret
  `LA_SIGNING_KEY`. The key is never stored in this repository.
- Customer information, settings, ads and photos never come here.
