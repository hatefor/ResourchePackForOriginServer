#!/usr/bin/env python3
"""Upload the KubeJS scripts and the datapack to the game server over SFTP.

WiseHosting's Game Panel has no public API, but it has SFTP (Files -> SFTP), so this is the automated upload.
GitHub Actions runs it after every passing push to main; it can also be run by hand.

    python tools/deploy_sftp.py --plan      # list what would be uploaded; needs no credentials
    python tools/deploy_sftp.py --dry-run   # connect and show what would change, change nothing
    python tools/deploy_sftp.py             # upload

Settings come from environment variables (GitHub secrets and variables in CI):
    SFTP_HOST, SFTP_PORT (default 2022), SFTP_USER, SFTP_PASSWORD   from the panel's Files -> SFTP page
    SFTP_HOST_KEY      optional but recommended: the server's public key line (from ssh-keyscan); a server whose
                       key does not match is refused
    SERVER_WORLD       the world folder, level-name in server.properties (default world)

It only ever writes or deletes inside the folders it owns: kubejs/server_scripts/ordertest/,
kubejs/server_scripts/origins/ and <world>/datapacks/ordertest.zip. Everything else on the server is untouched.
Scripts and datapacks take effect on /reload or a restart.
"""
from __future__ import annotations

import argparse
import base64
import io
import os
import posixpath
import stat
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pack_sources  # noqa: E402

PACK_ID = "ordertest"
SCRIPTS_REMOTE = "kubejs/server_scripts"
DEFAULT_PORT = 2022
DEFAULT_WORLD = "world"
FIXED_ZIP_TIME = (2020, 1, 1, 0, 0, 0)


def managed_dirs() -> list[str]:
    """Remote folders this tool owns completely: files in them that are not in the plan are deleted."""
    return [f"{SCRIPTS_REMOTE}/{PACK_ID}", f"{SCRIPTS_REMOTE}/{pack_sources.ORIGIN_SCRIPTS_PREFIX}"]


def datapack_zip() -> bytes:
    """The shipped datapack, the same files as dist/ordertest.zip, with fixed timestamps."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for rel, src in pack_sources.datapack_files().items():
            entry = zipfile.ZipInfo(rel, date_time=FIXED_ZIP_TIME)
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, src if isinstance(src, bytes) else src.read_bytes())
    return buffer.getvalue()


def plan(world: str) -> dict[str, bytes]:
    """{remote path: content} for everything this deploy puts on the server."""
    files = {f"{SCRIPTS_REMOTE}/{rel}": src.read_bytes() for rel, src in pack_sources.script_files().items()}
    files[f"{world}/datapacks/{PACK_ID}.zip"] = datapack_zip()
    owned = managed_dirs()
    for path in files:
        if not any(path.startswith(d + "/") for d in owned) and not path.endswith(f"/datapacks/{PACK_ID}.zip"):
            raise SystemExit(f"refusing to plan {path}: outside the folders this deploy owns")
    return files


class Remote:
    """The few SFTP operations sync needs, so tests can use an in-memory fake."""

    def __init__(self, sftp):
        self.sftp = sftp

    def files_under(self, folder: str) -> list[str]:
        try:
            entries = self.sftp.listdir_attr(folder)
        except FileNotFoundError:
            return []
        found = []
        for entry in entries:
            path = posixpath.join(folder, entry.filename)
            found += self.files_under(path) if stat.S_ISDIR(entry.st_mode) else [path]
        return found

    def read(self, path: str) -> bytes | None:
        try:
            with self.sftp.open(path, "rb") as handle:
                return handle.read()
        except FileNotFoundError:
            return None

    def write(self, path: str, data: bytes):
        self.makedirs(posixpath.dirname(path))
        self.sftp.putfo(io.BytesIO(data), path)

    def remove(self, path: str):
        self.sftp.remove(path)

    def makedirs(self, folder: str):
        built = ""
        for part in folder.split("/"):
            built = posixpath.join(built, part) if built else part
            try:
                self.sftp.stat(built)
            except FileNotFoundError:
                self.sftp.mkdir(built)


def sync(remote, files: dict[str, bytes], dry_run: bool = False) -> tuple[list[str], list[str]]:
    """Upload files that differ, delete stale files in the owned folders. Returns (written, deleted)."""
    existing = [p for d in managed_dirs() for p in remote.files_under(d)]
    deleted = sorted(p for p in existing if p not in files)
    written = sorted(p for p, data in files.items() if remote.read(p) != data)
    if not dry_run:
        for path in written:
            remote.write(path, files[path])
        for path in deleted:
            remote.remove(path)
    return written, deleted


def connect(host: str, port: int, user: str, password: str, host_key: str | None):
    import paramiko

    hostkey = None
    if host_key:
        parts = host_key.split()
        if parts and not parts[0].startswith(("ssh-", "ecdsa-")):
            parts = parts[1:]  # a known_hosts line starts with the host name
        hostkey = paramiko.PKey.from_type_string(parts[0], base64.b64decode(parts[1]))
    else:
        print("warning: SFTP_HOST_KEY is not set, so the server's identity is not checked")
    transport = paramiko.Transport((host, port))
    transport.connect(username=user, password=password, hostkey=hostkey)
    return transport, paramiko.SFTPClient.from_transport(transport)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plan", action="store_true", help="list the files, do not connect")
    parser.add_argument("--dry-run", action="store_true", help="connect and compare, change nothing")
    args = parser.parse_args()
    world = os.environ.get("SERVER_WORLD") or DEFAULT_WORLD
    files = plan(world)
    if args.plan:
        for path in sorted(files):
            print(f"{len(files[path]):>8}  {path}")
        print(f"{len(files)} files; owned folders: {', '.join(managed_dirs())}")
        return 0
    host, user, password = (os.environ.get(k, "") for k in ("SFTP_HOST", "SFTP_USER", "SFTP_PASSWORD"))
    if not (host and user and password):
        print("SFTP is not configured (SFTP_HOST, SFTP_USER, SFTP_PASSWORD), so nothing was deployed.")
        return 0
    port = int(os.environ.get("SFTP_PORT") or DEFAULT_PORT)
    transport, sftp = connect(host, port, user, password, os.environ.get("SFTP_HOST_KEY"))
    try:
        written, deleted = sync(Remote(sftp), files, dry_run=args.dry_run)
    finally:
        sftp.close()
        transport.close()
    verb = "would" if args.dry_run else "did"
    print(f"{verb} upload {len(written)} and delete {len(deleted)} files ({len(files) - len(written)} already up to date)")
    for path in written:
        print(f"  upload  {path}")
    for path in deleted:
        print(f"  delete  {path}")
    if written or deleted:
        print("Run /reload on the server (or restart it) for the changes to take effect.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
