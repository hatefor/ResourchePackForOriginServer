#!/usr/bin/env python3
"""Build every effect into the server resource pack: shared ones in tools/photon/effects/*.py and each origin's
origins/<name>/effects.py. An origin's effects are named ordertest:<origin>/<effect> (fx/<origin>/<effect>.fx),
so two origins can never collide.

    python -I tools/photon/generate.py          # write resourcepack/assets/ordertest/fx/<name>.fx
    python -I tools/photon/generate.py --check  # build and check only (budget, one-shot rules, round trip)
    python -I tools/photon/generate.py --verify # also fail if a committed .fx differs from its code (CI)

Each effects module exposes EFFECTS = {name: function returning an fx.FxDocument}. A name may only be defined once.
"""
from __future__ import annotations

import argparse
import gzip
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import fx  # noqa: E402
import nbt  # noqa: E402
import pack_sources  # noqa: E402

REPO = os.path.dirname(os.path.dirname(HERE))
NAMESPACE = "ordertest"
OUT_DIR = os.path.join(REPO, "resourcepack", "assets", NAMESPACE, "fx")


def load_effects() -> dict:
    """{effect id path: build function}; an origin's effects are prefixed with '<origin>/'."""
    effects = {}
    for origin, file in pack_sources.effect_modules():
        module_name = "effects_" + (origin or "shared") + "_" + file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name, build in getattr(module, "EFFECTS", {}).items():
            key = f"{origin}/{name}" if origin else name
            if key in effects:
                raise SystemExit(f"effect {key} is defined twice ({file})")
            effects[key] = build
    return effects


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="build and check without writing")
    parser.add_argument("--verify", action="store_true", help="check, and compare with the committed .fx files")
    args = parser.parse_args()
    args.check = args.check or args.verify
    failed = 0
    for name, build in load_effects().items():
        doc = build()
        problems = doc.problems()
        # A written file must decode back to the same tree Photon will read.
        decoded = nbt.loads(gzip.decompress(gzip.compress(nbt.dumps(doc.root()))))[1]
        if decoded != doc.root():
            problems.append("does not round-trip through NBT")
        committed = os.path.join(OUT_DIR, name + ".fx")
        # By content, not bytes: two zlib builds may compress the same tree differently.
        if args.verify and (not os.path.exists(committed) or nbt.load_gzip(committed)[1] != doc.root()):
            problems.append("the committed .fx is out of date; run generate.py and commit the result")
        status = "FAIL" if problems else "ok"
        print(f"{status:4}  {NAMESPACE}:{name}  {doc.particle_budget()} particles max")
        for problem in problems:
            print("        " + problem)
        failed += bool(problems)
        if not problems and not args.check and doc.write(os.path.join(OUT_DIR, name + ".fx")):
            print(f"        wrote {name}.fx")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
