"""Unit tests for the Photon 1.20.1 effect generator.

    python -m unittest discover -s tools/photon -p "test_*.py" -v
"""
import copy
import gzip
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fx  # noqa: E402
import generate  # noqa: E402
import nbt  # noqa: E402


def without_id(obj):
    obj = copy.deepcopy(obj)
    obj["transform"].pop("id")
    return obj


class BuilderMatchesPhoton(unittest.TestCase):
    def test_untouched_emitter_is_photons_own_default(self):
        built = fx.ParticleEmitter("particle").obj
        self.assertEqual(without_id(built), without_id(fx._template_object("particle_default")))

    def test_file_root_is_the_1_20_1_layout(self):
        root = fx.FxDocument().root()
        self.assertEqual(set(root), {"fx", "_version"})
        self.assertEqual(int(root["_version"]), fx.FILE_VERSION)
        self.assertEqual(set(root["fx"]), {"mainFX", "subFXs"})

    def test_function_shape_keeps_photons_keys(self):
        emitter = fx.ParticleEmitter("p").shape_function(x="cos(t)", speed_y="1")
        shape = emitter.c["shape"]["shape"]
        self.assertEqual(set(shape), set(fx._SHAPE_TEMPLATES["function"]))
        self.assertEqual((shape["_type"], shape["x"], shape["speedY"]), ("function", "cos(t)", "1"))

    def test_gradient_channels_are_flat_time_value_pairs(self):
        g = fx.gradient([(0.0, 1.0, 0.5, 0.25, 1.0), (1.0, 0.0, 0.0, 0.0, 0.0)])
        self.assertEqual(list(g["g"]), [0.0, 0.5, 1.0, 0.0])
        self.assertEqual(list(g["a"]), [0.0, 1.0, 1.0, 0.0])
        self.assertEqual(g["_type"], "Gradient")

    def test_argb_is_signed_like_java(self):
        self.assertEqual(fx.argb(255, 255, 255), -1)
        self.assertEqual(fx.argb(0, 0, 0, 0), 0)


class Rules(unittest.TestCase):
    def test_over_budget_effect_is_refused(self):
        doc = fx.FxDocument()
        doc.particles("a").max_particles(fx.MAX_EFFECT_PARTICLES)
        doc.particles("b").max_particles(1)
        self.assertTrue(any("budget" in p for p in doc.problems()))

    def test_one_shot_with_continuous_emission_is_refused(self):
        doc = fx.FxDocument()
        doc.particles("a").looping(False).emission_rate(2)
        self.assertTrue(any("bursts only" in p for p in doc.problems()))

    def test_one_shot_that_outlives_its_duration_is_refused(self):
        doc = fx.FxDocument()
        doc.particles("a").looping(False).emission_rate(0).duration(20).lifetime(30).burst(time=0, count=10)
        self.assertTrue(any("outlives" in p for p in doc.problems()))

    def test_a_clean_one_shot_passes(self):
        doc = fx.FxDocument()
        doc.particles("a").looping(False).emission_rate(0).duration(30).lifetime(20).burst(time=0, count=10)
        self.assertEqual(doc.problems(), [])


class Output(unittest.TestCase):
    def test_same_effect_gives_same_bytes(self):
        build = generate.load_effects()["domain_open"]
        self.assertEqual(build().encode(), build().encode())

    def test_every_shipped_effect_builds_cleanly_and_round_trips(self):
        for name, build in generate.load_effects().items():
            with self.subTest(effect=name):
                doc = build()
                self.assertEqual(doc.problems(), [])
                decoded = nbt.loads(gzip.decompress(doc.encode()))[1]
                self.assertEqual(decoded, doc.root())


if __name__ == "__main__":
    unittest.main()
