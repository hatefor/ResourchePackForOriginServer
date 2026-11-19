"""Where every part of the pack comes from: the shared folders plus one folder per origin.

    origins/<name>/*.js           KubeJS scripts, loaded as server_scripts/origins/<name>/...
    origins/<name>/data/...       datapack files, merged into the one shipped datapack
    origins/<name>/effects.py     Photon effects (tools/photon/generate.py), released as ordertest:<name>/<effect>
    origins/<name>/*.mctest       headless tests

Every tool (test server, dev client, validator, generator, zips, release) reads these functions, so a new
origin folder is picked up everywhere with no registration. Two sources writing the same file is an error.
"""
from __future__ import annotations

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


def datapack_files() -> dict[str, Path]:
    """Every file of the shipped datapack, keyed by its path inside the pack (pack.mcmeta, data/...)."""
    files: dict[str, Path] = {}
    _add(files, "pack.mcmeta", PACK_META)
    for root in data_roots():
        for src in sorted(root.rglob("*")):
            if src.is_file():
                _add(files, "data/" + src.relative_to(root).as_posix(), src)
    return files


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
