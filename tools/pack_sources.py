"""Where every part of the pack comes from: the shared folders plus one folder per origin.

    origins/<name>/*.js           KubeJS scripts, loaded as server_scripts/origins/<name>/...
    origins/<name>/data/...       datapack files, merged into the one shipped datapack
    origins/<name>/effects.py     Photon effects (tools/photon/generate.py), released as ordertest:<name>/<effect>
    origins/<name>/*.mctest       headless tests

Every tool (test server, dev client, validator, generator, zips, release) reads these functions, so a new
origin folder is picked up everywhere with no registration. Two sources writing the same file is an error,
except for files Minecraft and Origins themselves merge across datapacks: tags (union of "values") and origin
layers (union of "origins"). Those are merged here the same way, so many imported origins can each add
themselves to data/origins/origin_layers/origin.json or hook minecraft:load and minecraft:tick.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ORIGINS_DIR = REPO / "origins"
SHARED_DATA = REPO / "data"
SHARED_SCRIPTS = REPO / "kubejs" / "server_scripts"
SHARED_TESTS = REPO / "tests"
PACK_META = REPO / "pack.mcmeta"
ORIGIN_SCRIPTS_PREFIX = "origins"


class SourceConflict(Exception):
    pass


def origin_dirs() -> list[Path]:
    if not ORIGINS_DIR.is_dir():
        return []
    return sorted(p for p in ORIGINS_DIR.iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))


def data_roots() -> list[Path]:
    """The shared data/ first, then each origin's data/."""
    roots = [SHARED_DATA] if SHARED_DATA.is_dir() else []
    return roots + [o / "data" for o in origin_dirs() if (o / "data").is_dir()]


def _add(files: dict[str, Path], rel: str, src: Path):
    if rel in files:
        raise SourceConflict(f"{rel} comes from both {files[rel].relative_to(REPO)} and {src.relative_to(REPO)}")
    files[rel] = src


MERGED_TAG = re.compile(r"^data/[^/]+/tags/.+\.json$")
MERGED_LAYER = re.compile(r"^data/[^/]+/origin_layers/.+\.json$")


def datapack_files() -> dict[str, Path | bytes]:
    """Every file of the shipped datapack, keyed by its path inside the pack (pack.mcmeta, data/...).
    A value is the source file, or the merged JSON bytes when several sources share a mergeable file."""
    sources: dict[str, list[Path]] = {"pack.mcmeta": [PACK_META]}
    for root in data_roots():
        for src in sorted(root.rglob("*")):
            if src.is_file():
                sources.setdefault("data/" + src.relative_to(root).as_posix(), []).append(src)
    files: dict[str, Path | bytes] = {}
    for rel, srcs in sources.items():
        if len(srcs) == 1:
            files[rel] = srcs[0]
        elif MERGED_TAG.match(rel):
            files[rel] = _merge(srcs, "values")
        elif MERGED_LAYER.match(rel):
            files[rel] = _merge(srcs, "origins")
        else:
            names = " and ".join(str(s.relative_to(REPO)) for s in srcs)
            raise SourceConflict(f"{rel} comes from both {names}")
    return files


def _merge(srcs: list[Path], list_key: str) -> bytes:
    """Union of list_key across the sources, in order, with the first source's other fields; replace if any does."""
    merged: dict = {}
    seen: set[str] = set()
    entries: list = []
    for src in srcs:
        try:
            data = json.loads(src.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise SourceConflict(f"cannot merge {src.relative_to(REPO)}: invalid JSON ({error})") from error
        for key, value in data.items():
            if key != list_key:
                merged.setdefault(key, value)
        merged["replace"] = bool(merged.get("replace")) or bool(data.get("replace"))
        for entry in data.get(list_key, []):
            key = json.dumps(entry, sort_keys=True)
            if key not in seen:
                seen.add(key)
                entries.append(entry)
    merged[list_key] = entries
    return (json.dumps(merged, indent=2) + "\n").encode("utf-8")


def script_files() -> dict[str, Path]:
    """Every KubeJS server script, keyed by its path under kubejs/server_scripts/."""
    files: dict[str, Path] = {}
    if SHARED_SCRIPTS.is_dir():
        for src in sorted(SHARED_SCRIPTS.rglob("*.js")):
            _add(files, src.relative_to(SHARED_SCRIPTS).as_posix(), src)
    for origin in origin_dirs():
        for src in sorted(origin.rglob("*.js")):
            if "data" in src.relative_to(origin).parts:
                continue
            _add(files, f"{ORIGIN_SCRIPTS_PREFIX}/{origin.name}/{src.relative_to(origin).as_posix()}", src)
    return files


def test_files() -> list[Path]:
    shared = sorted(SHARED_TESTS.glob("*.mctest")) if SHARED_TESTS.is_dir() else []
    return shared + [t for o in origin_dirs() for t in sorted(o.glob("*.mctest"))]


def effect_modules() -> list[tuple[str | None, Path]]:
    """(origin name or None for shared, file) for every effects module."""
    shared_dir = REPO / "tools" / "photon" / "effects"
    shared = [(None, f) for f in sorted(shared_dir.glob("*.py")) if not f.name.startswith("_")] if shared_dir.is_dir() else []
    return shared + [(o.name, o / "effects.py") for o in origin_dirs() if (o / "effects.py").is_file()]
