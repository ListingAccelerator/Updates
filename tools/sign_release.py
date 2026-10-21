"""
sign_release.py -- sign the update named in stable/release.json.

Run by GitHub (see .github/workflows/sign.yml) whenever release.json
changes. The signing key is the repository secret LA_SIGNING_KEY; it is
never written to this repository.

stable/release.json   {"version": "1.4", "zip": "ListingAccelerator-1.4.zip",
                       "notes": ["..."], "critical": false}
writes
stable/latest.json      what the program reads: version, notes, zip, sha256
stable/latest.json.sig  the signature the program checks before anything
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

STABLE = Path(__file__).resolve().parent.parent / "stable"


def main() -> int:
    key = os.environ.get("LA_SIGNING_KEY", "").strip()
    if not re.fullmatch(r"[0-9a-fA-F]{64}", key):
        print("LA_SIGNING_KEY secret is missing or not 64 hex characters.")
        return 1
    rel = json.loads((STABLE / "release.json").read_text(encoding="utf-8"))
    version = str(rel["version"]).strip()
    zname = str(rel["zip"]).strip()
    if not re.fullmatch(r"\d+(\.\d+){1,3}", version):
        print(f"Bad version: {version!r}")
        return 1
    if not re.fullmatch(r"ListingAccelerator-[0-9.]+\.zip", zname):
        print(f"Bad zip name: {zname!r}")
        return 1
    z = STABLE / zname
    if not z.is_file():
        print(f"{zname} is not in stable/")
        return 1
    info = {"version": version,
            "notes": [str(n) for n in rel.get("notes") or []],
            "zip": zname,
            "sha256": hashlib.sha256(z.read_bytes()).hexdigest(),
            "critical": bool(rel.get("critical"))}
    raw = json.dumps(info, indent=1).encode("utf-8")
    sk = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(key))
    (STABLE / "latest.json").write_bytes(raw)
    (STABLE / "latest.json.sig").write_text(sk.sign(raw).hex(),
                                            encoding="ascii")
    print(f"Signed {version}: {zname}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
