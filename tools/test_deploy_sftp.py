"""Unit tests for deploy_sftp against an in-memory server, so they need no network and no credentials.

    python -m unittest discover -s tools -p "test_*.py" -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import deploy_sftp  # noqa: E402


class FakeRemote:
    """A server's files as a dict, with the same methods deploy_sftp.Remote offers."""

    def __init__(self, files):
        self.files = dict(files)

    def files_under(self, folder):
        return [p for p in self.files if p.startswith(folder + "/")]

    def read(self, path):
        return self.files.get(path)

    def write(self, path, data):
        self.files[path] = data

    def remove(self, path):
        del self.files[path]


class Sync(unittest.TestCase):
    def setUp(self):
        self.plan = deploy_sftp.plan("world")

    def test_plan_covers_scripts_origins_and_datapack(self):
        self.assertIn("kubejs/server_scripts/ordertest/core.js", self.plan)
        self.assertTrue(any(p.startswith("kubejs/server_scripts/origins/") for p in self.plan))
        self.assertIn("world/datapacks/ordertest.zip", self.plan)

    def test_first_deploy_uploads_everything(self):
        remote = FakeRemote({})
        written, deleted = deploy_sftp.sync(remote, self.plan)
        self.assertEqual(set(written), set(self.plan))
        self.assertEqual(deleted, [])
        self.assertEqual(remote.files, self.plan)

    def test_unchanged_files_are_not_uploaded_again(self):
        remote = FakeRemote(self.plan)
        written, deleted = deploy_sftp.sync(remote, self.plan)
        self.assertEqual((written, deleted), ([], []))

    def test_stale_files_are_deleted_only_inside_owned_folders(self):
        server = dict(self.plan)
        server["kubejs/server_scripts/origins/removed_origin/origin.js"] = b"old"
        server["kubejs/server_scripts/someone_elses_script.js"] = b"keep"
        server["world/datapacks/other_pack.zip"] = b"keep"
        server["mods/photon.jar"] = b"keep"
        remote = FakeRemote(server)
        _, deleted = deploy_sftp.sync(remote, self.plan)
        self.assertEqual(deleted, ["kubejs/server_scripts/origins/removed_origin/origin.js"])
        for kept in ("kubejs/server_scripts/someone_elses_script.js", "world/datapacks/other_pack.zip", "mods/photon.jar"):
            self.assertIn(kept, remote.files)

    def test_dry_run_changes_nothing(self):
        remote = FakeRemote({"kubejs/server_scripts/ordertest/stale.js": b"old"})
        before = dict(remote.files)
        written, deleted = deploy_sftp.sync(remote, self.plan, dry_run=True)
        self.assertTrue(written and deleted)
        self.assertEqual(remote.files, before)

    def test_datapack_zip_is_reproducible(self):
        self.assertEqual(deploy_sftp.datapack_zip(), deploy_sftp.datapack_zip())

    def test_world_folder_comes_from_the_setting(self):
        self.assertIn("survival/datapacks/ordertest.zip", deploy_sftp.plan("survival"))


if __name__ == "__main__":
    unittest.main()
