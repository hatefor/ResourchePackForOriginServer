"""Unit tests for pack_sources: origin folders are merged into the datapack and scripts, and clashes are caught.

    python -m unittest discover -s tools -p "test_*.py" -v
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pack_sources  # noqa: E402


class PackSources(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.patch = mock.patch.multiple(
            pack_sources, REPO=root, ORIGINS_DIR=root / "origins", SHARED_DATA=root / "data",
            SHARED_SCRIPTS=root / "kubejs" / "server_scripts", SHARED_TESTS=root / "tests",
            PACK_META=root / "pack.mcmeta")
        self.patch.start()
        self.root = root
        self.write("pack.mcmeta", "{}")
        self.write("data/ordertest/functions/shared.mcfunction", "say shared")
        self.write("kubejs/server_scripts/ordertest/core.js", "// core")
        self.write("origins/storm/data/ordertest/powers/storm/zap.json", "{}")
        self.write("origins/storm/origin.js", "// origin")
        self.write("origins/storm/effects.py", "EFFECTS = {}")
        self.write("origins/storm/tests.mctest", "say hi")
        self.write("origins/_draft/origin.js", "// ignored: leading underscore")

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_origin_data_is_merged_into_the_datapack(self):
        files = pack_sources.datapack_files()
        self.assertIn("data/ordertest/functions/shared.mcfunction", files)
        self.assertIn("data/ordertest/powers/storm/zap.json", files)
        self.assertIn("pack.mcmeta", files)

    def test_origin_scripts_load_under_origins(self):
        files = pack_sources.script_files()
        self.assertIn("ordertest/core.js", files)
        self.assertIn("origins/storm/origin.js", files)
        self.assertFalse(any("_draft" in k for k in files))

    def test_scripts_inside_an_origins_data_folder_are_not_scripts(self):
        self.write("origins/storm/data/ordertest/odd.js", "// not a script")
        self.assertNotIn("origins/storm/data/ordertest/odd.js", pack_sources.script_files())

    def test_two_sources_writing_one_file_is_an_error(self):
        self.write("origins/rival/data/ordertest/functions/shared.mcfunction", "say rival")
        with self.assertRaises(pack_sources.SourceConflict):
            pack_sources.datapack_files()

    def test_shared_tags_from_several_origins_are_merged(self):
        self.write("data/minecraft/tags/functions/load.json", '{"values": ["ordertest:load"]}')
        self.write("origins/storm/data/minecraft/tags/functions/load.json", '{"values": ["storm:load"]}')
        self.write("origins/rival/data/minecraft/tags/functions/load.json",
                   '{"replace": false, "values": ["rival:load", "storm:load"]}')
        merged = json.loads(pack_sources.datapack_files()["data/minecraft/tags/functions/load.json"])
        # Shared data first, then origins in folder-name order (rival, storm); duplicates kept once.
        self.assertEqual(merged["values"], ["ordertest:load", "rival:load", "storm:load"])
        self.assertFalse(merged["replace"])

    def test_origin_layers_from_several_origins_are_merged(self):
        layer = "data/origins/origin_layers/origin.json"
        self.write("origins/storm/" + layer, '{"replace": false, "origins": ["storm:storm"]}')
        self.write("origins/rival/" + layer, '{"origins": ["rival:rival"]}')
        merged = json.loads(pack_sources.datapack_files()[layer])
        self.assertEqual(merged["origins"], ["rival:rival", "storm:storm"])

    def test_tests_and_effects_are_found_per_origin(self):
        self.assertIn(self.root / "origins/storm/tests.mctest", pack_sources.test_files())
        self.assertIn(("storm", self.root / "origins/storm/effects.py"), pack_sources.effect_modules())


if __name__ == "__main__":
    unittest.main()
