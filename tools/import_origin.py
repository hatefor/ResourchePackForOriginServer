#!/usr/bin/env python3
"""Import a saved Origins datapack (a .zip or a folder) as an origin folder.

    python tools/import_origin.py "C:/path/Werewolf-1.0.0-datapack.zip"            # origins/werewolf_1_0_0_datapack/
    python tools/import_origin.py "C:/path/Werewolf-1.0.0-datapack.zip" --name werewolf

Only the pack's data/ (and its README, if it has one) is taken; its pack.mcmeta is replaced by this repo's one.
Files every Origins pack shares (data/origins/origin_layers/origin.json, minecraft:load and minecraft:tick) are
merged with the other origins' copies at build time, so any number of packs can be imported side by side.
Run tools/validate.py and tools/testserver.py test afterwards.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pack_sources  # noqa: E402

TARGET_PACK_FORMAT = 15  # Minecraft 1.20.1
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,40}$")
ORIGIN_FILE = re.compile(r"^data/([^/]+)/origins/(.+)\.json$")
README_NAMES = ("readme.md", "readme.txt")


def default_name(source: Path) -> str:
    stem = source.stem if source.is_file() else source.name
    stem = re.sub(r"\s*\(\d+\)", "", stem)
    name = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    return name if name[:1].isalpha() else "origin_" + name


def read_pack(source: Path) -> dict[str, bytes]:
    """Every file of the pack, keyed by its path inside the pack, from a zip or a folder."""
    files: dict[str, bytes] = {}
    if source.is_dir():
        for path in source.rglob("*"):
            if path.is_file():
                files[path.relative_to(source).as_posix()] = path.read_bytes()
    else:
        with zipfile.ZipFile(source) as archive:
            for info in archive.infolist():
                if not info.is_dir():
                    files[info.filename] = archive.read(info)
    # Some zips wrap the pack in a folder; strip it so pack.mcmeta sits at the root.
    metas = [n for n in files if PurePosixPath(n).name == "pack.mcmeta"]
    if not metas:
        raise SystemExit(f"{source.name} has no pack.mcmeta, so it is not a datapack")
    prefix = min(metas, key=len)[:-len("pack.mcmeta")]
    return {n[len(prefix):]: data for n, data in files.items() if n.startswith(prefix)}


def safe(rel: str) -> bool:
    path = PurePosixPath(rel)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in rel


def describe(files: dict[str, bytes], source: Path, name: str) -> str:
    meta = json.loads(files["pack.mcmeta"].decode("utf-8-sig")).get("pack", {})
    origins = []
    for rel, data in sorted(files.items()):
        match = ORIGIN_FILE.match(rel)
        if match:
            try:
                title = json.loads(data.decode("utf-8-sig")).get("name", match.group(2))
            except json.JSONDecodeError:
                title = match.group(2)
            title = title if isinstance(title, str) else match.group(2)
            origins.append(f"| {title} | `{match.group(1)}:{match.group(2)}` |")
    description = meta.get("description", "")
    description = description if isinstance(description, str) else json.dumps(description)
    lines = [f"# {name}", "", f"Imported from `{source.name}`. {description}".rstrip(), "",
             "| Origin | Id |", "|---|---|", *origins, "",
             "Its datapack files are in `data/` and ship merged into the server's one datapack."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="the datapack .zip or folder")
    parser.add_argument("--name", help="origin folder name (default: from the file name)")
    args = parser.parse_args()
    name = args.name or default_name(args.source)
    if not NAME_PATTERN.match(name):
        raise SystemExit(f"'{name}' is not a usable folder name; pass --name with lowercase letters, digits and _")
    folder = pack_sources.ORIGINS_DIR / name
    if folder.exists():
        raise SystemExit(f"{folder.relative_to(pack_sources.REPO)} already exists")

    files = read_pack(args.source)
    unsafe = [rel for rel in files if not safe(rel)]
    if unsafe:
        raise SystemExit(f"refusing {args.source.name}: unsafe paths {unsafe[:3]}")
    pack_format = json.loads(files["pack.mcmeta"].decode("utf-8-sig")).get("pack", {}).get("pack_format")
    # Files directly in data/ (not in a namespace folder) are never loaded by Minecraft; keep them beside the
    # origin instead, where they cannot clash with another pack's copy.
    loose = {rel[len("data/"):]: data for rel, data in files.items() if rel.startswith("data/") and rel.count("/") == 1}
    kept = {rel: data for rel, data in files.items() if rel.startswith("data/") and rel.count("/") > 1}
    readme = next((data for rel, data in files.items() if rel.lower() in README_NAMES), None)
    skipped = sorted(rel for rel in files if not rel.startswith("data/") and rel != "pack.mcmeta"
                     and rel.lower() not in README_NAMES)
    if not kept:
        raise SystemExit(f"{args.source.name} has no data/ folder")

    for rel, data in kept.items():
        path = folder / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (folder / "README.md").write_bytes(readme if readme else describe(files, args.source, name).encode("utf-8"))
    for loose_name, data in loose.items():
        (folder / ("PACK_" + loose_name)).write_bytes(data)

    origins = [f"{m.group(1)}:{m.group(2)}" for rel in kept if (m := ORIGIN_FILE.match(rel))]
    print(f"Imported {args.source.name} -> {folder.relative_to(pack_sources.REPO).as_posix()}: "
          f"{len(kept)} files, origins {', '.join(origins) or '(none)'}")
    if pack_format != TARGET_PACK_FORMAT:
        print(f"  note: made for pack_format {pack_format}, the server is {TARGET_PACK_FORMAT}; the test server shows "
              "whether everything still loads")
    if skipped:
        print(f"  skipped (not datapack data): {', '.join(skipped[:6])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
