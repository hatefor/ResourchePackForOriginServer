"""Write Photon 1.1.17 (Minecraft 1.20.1) effects from code.

Ported from VoidSpell's tools/photon (written for Photon on Minecraft 26.x, whose file layout differs). Every
emitter here is a copy of a template Photon itself serialized (templates/, made by the dev client's
`!photon_dump` step), so a module you never touch is written exactly as Photon writes it. Change values only
through the methods below; never hand-write a subtree from field names, a wrong key mis-renders silently.

    import fx
    doc = fx.FxDocument()
    ring = doc.particles("ring")
    ring.shape_function(x="12*cos(2*PI*randomA)", y="0", z="12*sin(2*PI*randomA)")
    ring.burst(time=0, count=400).emission_rate(0).looping(False).duration(40).lifetime(30)
    doc.write("resourcepack/assets/ordertest/fx/ring.fx")

Function-shape expressions are evaluated by Photon on each client: `t` is the emitter's progress [0, 1),
`PI` is pi, `randomA`..`randomE` are random [0, 1) per particle (the same letter is the same value within one
expression). x/y/z set the spawn offset in blocks; speedX/Y/Z only set the direction, `speed` sets how fast.
"""
from __future__ import annotations

import copy
import gzip
import os
import uuid

import nbt

TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
FILE_VERSION = 1  # FXProject.VERSION in Photon 1.1.17
# Photon has no LOD or culling: every viewer pays an effect's whole count each frame (VoidSpell Rule 37).
MAX_EFFECT_PARTICLES = 8000
SHAPES = ("sphere", "function", "circle", "box", "dot", "cylinder", "cone")
BLEND_ADD = "ADD"


def _template_object(name: str) -> nbt.Compound:
    _, root = nbt.load_gzip(os.path.join(TEMPLATES, name + ".fx"))
    return root["fx"]["mainFX"]["fxObjects"][0]


_PARTICLE = _template_object("particle_default")
_SHAPE_TEMPLATES = {s: _template_object("shape_" + s)["config"]["shape"]["shape"] for s in SHAPES}


# ---------- value types (shapes copied from the templates) ----------

def constant(value: float) -> nbt.Compound:
    return nbt.Compound({"number": nbt.Float(value), "_type": nbt.String("Constant")})


def vec3(x: float, y: float | None = None, z: float | None = None) -> nbt.Compound:
    y = x if y is None else y
    z = x if z is None else z
    return nbt.Compound({"x": constant(x), "y": constant(y), "z": constant(z)})


def argb(r: int, g: int, b: int, a: int = 255) -> int:
    """0-255 components to the signed 32-bit int Photon stores."""
    value = (a & 0xFF) << 24 | (r & 0xFF) << 16 | (g & 0xFF) << 8 | (b & 0xFF)
    return value - (1 << 32) if value >= 1 << 31 else value


def hex_color(text: str) -> tuple[int, int, int]:
    text = text.lstrip("#")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def color(r: int, g: int, b: int, a: int = 255) -> nbt.Compound:
    return nbt.Compound({"number": nbt.Int(argb(r, g, b, a)), "_type": nbt.String("Color")})


def gradient(stops) -> nbt.Compound:
    """stops: [(t, r, g, b, a), ...] with every value 0-1. Each channel is stored as a flat [t0, v0, t1, v1, ...]."""
    channels = {"r": 1, "g": 2, "b": 3, "a": 4}
    out = nbt.Compound()
    for name, index in channels.items():
        flat = []
        for stop in stops:
            value = stop[index] if index < len(stop) else 1.0
            flat += [nbt.Float(stop[0]), nbt.Float(value)]
        out[name] = nbt.List.of(flat)
    out["_type"] = nbt.String("Gradient")
    return out


# ---------- emitters ----------

class ParticleEmitter:
    """One particle system. Every setter returns self so calls chain."""

    def __init__(self, name: str):
        self.obj = copy.deepcopy(_PARTICLE)
        self.obj["name"] = nbt.String(name)
        self.obj["transform"]["id"] = _stable_id(name)
        self.c = self.obj["config"]

    # start values; time is in ticks (VoidSpell measured ticks on Photon 26; confirm on screen here)
    def duration(self, ticks: int): self.c["duration"] = nbt.Int(ticks); return self
    def looping(self, on: bool): self.c["looping"] = nbt.Byte(1 if on else 0); return self
    def max_particles(self, n: int): self.c["maxParticles"] = nbt.Int(n); return self
    def lifetime(self, ticks: float): self.c["startLifetime"] = constant(ticks); return self
    def speed(self, value: float): self.c["startSpeed"] = constant(value); return self
    def delay(self, ticks: float): self.c["startDelay"] = constant(ticks); return self
    def size(self, x: float, y: float | None = None, z: float | None = None): self.c["startSize"] = vec3(x, y, z); return self
    def rotation(self, x: float = 0, y: float = 0, z: float = 0): self.c["startRotation"] = vec3(x, y, z); return self

    def tint(self, r: int, g: int, b: int, a: int = 255):
        self.c["startColor"] = color(r, g, b, a)
        return self

    # emission
    def emission_rate(self, per_tick: float, mode: str = "Exacting"):
        self.c["emission"]["emissionRate"] = constant(per_tick)
        self.c["emission"]["emissionMode"] = nbt.String(mode)
        return self

    def burst(self, time: int, count: int, cycles: int = 1, interval: int = 1, probability: float = 1.0):
        entry = nbt.Compound({
            "probability": nbt.Float(probability), "count": constant(count), "cycles": nbt.Int(cycles),
            "interval": nbt.Int(interval), "time": nbt.Int(time),
        })
        bursts = self.c["emission"]["bursts"]
        if bursts.element_tag_id != nbt.TAG_COMPOUND:
            bursts = self.c["emission"]["bursts"] = nbt.List(nbt.TAG_COMPOUND, [])
        bursts.append(entry)
        return self

    # shapes
    def _shape(self, kind: str, **fields):
        shape = copy.deepcopy(_SHAPE_TEMPLATES[kind])
        for key, value in fields.items():
            shape[key] = nbt.String(value) if isinstance(value, str) else nbt.Float(value)
        self.c["shape"]["shape"] = shape
        return self

    def shape_sphere(self, radius: float, thickness: float = 1.0, arc: float = 360.0):
        return self._shape("sphere", radius=radius, radiusThickness=thickness, arc=arc)

    def shape_circle(self, radius: float, thickness: float = 1.0, arc: float = 360.0):
        return self._shape("circle", radius=radius, radiusThickness=thickness, arc=arc)

    def shape_cone(self, radius: float = 0.5, angle: float = 25.0, thickness: float = 1.0, arc: float = 360.0):
        return self._shape("cone", radius=radius, angle=angle, radiusThickness=thickness, arc=arc)

    def shape_dot(self):
        return self._shape("dot")

    def shape_function(self, x: str = "0", y: str = "0", z: str = "0",
                       speed_x: str = "0", speed_y: str = "0", speed_z: str = "0"):
        """Expressions in t, PI and randomA..E, evaluated by Photon on the client per particle."""
        return self._shape("function", x=x, y=y, z=z, speedX=speed_x, speedY=speed_y, speedZ=speed_z)

    def shape_offset(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        s = self.c["shape"]
        s["position"], s["rotation"], s["scale"] = vec3(*position), vec3(*rotation), vec3(*scale)
        return self

    # look
    def texture(self, path: str):
        self.c["material"]["material"]["texture"] = nbt.String(path)
        return self

    def blend(self, func: str = BLEND_ADD):
        self.c["material"]["blendMode"]["blendFunc"] = nbt.String(func)
        return self

    def render_mode(self, mode: str):
        """Billboard, Horizontal, Vertical, VerticalBillboard (Model needs a model template, not dumped yet)."""
        self.c["renderer"]["renderMode"] = nbt.String(mode)
        return self

    def bloom(self, on: bool = True):
        self.c["renderer"]["bloomEffect"] = nbt.Byte(1 if on else 0)
        return self

    def lights(self, block: int = 15, sky: int = 15):
        self.c["lights"]["enable"] = nbt.Byte(1)
        self.c["lights"]["blockLight"], self.c["lights"]["skyLight"] = constant(block), constant(sky)
        return self

    def color_over_lifetime(self, stops):
        self.c["colorOverLifetime"]["enable"] = nbt.Byte(1)
        self.c["colorOverLifetime"]["color"] = gradient(stops)
        return self

    def gravity(self, value: float, collide: bool = False):
        physics = self.c["physics"]
        physics["enable"] = nbt.Byte(1)
        physics["gravity"] = constant(value)
        physics["hasCollision"] = nbt.Byte(1 if collide else 0)
        return self

    # checks
    @property
    def max_count(self) -> int:
        return int(self.c["maxParticles"])

    def one_shot_problems(self) -> list[str]:
        """VoidSpell's empty-frame rule: a one-shot must end with no live particle, or its last frame freezes."""
        if self.c["looping"]:
            return []
        problems = []
        duration = int(self.c["duration"])
        if float(self.c["emission"]["emissionRate"]["number"]) > 0:
            problems.append("a one-shot must use bursts only (emission_rate(0))")
        lifetime = float(self.c["startLifetime"]["number"])
        if lifetime < 4:
            problems.append("lifetime below 4 ticks flickers; below 1 never expires")
        for b in self.c["emission"]["bursts"]:
            last = int(b["time"]) + (int(b["cycles"]) - 1) * int(b["interval"])
            if last + lifetime > duration:
                problems.append(f"burst at tick {last} + lifetime {lifetime:g} outlives duration {duration}")
        return problems


class FxDocument:
    def __init__(self):
        self.objects: list[ParticleEmitter] = []

    def particles(self, name: str) -> ParticleEmitter:
        emitter = ParticleEmitter(name)
        self.objects.append(emitter)
        return emitter

    def particle_budget(self) -> int:
        return sum(o.max_count for o in self.objects)

    def problems(self) -> list[str]:
        found = [f"{o.obj['name']}: {p}" for o in self.objects for p in o.one_shot_problems()]
        if self.particle_budget() > MAX_EFFECT_PARTICLES:
            found.append(f"{self.particle_budget()} particles is over the {MAX_EFFECT_PARTICLES} budget")
        return found

    def root(self) -> nbt.Compound:
        objects = nbt.List.of([o.obj for o in self.objects]) if self.objects else nbt.List.empty()
        fx_tag = nbt.Compound({"mainFX": nbt.Compound({"fxObjects": objects}), "subFXs": nbt.Compound()})
        return nbt.Compound({"fx": fx_tag, "_version": nbt.Int(FILE_VERSION)})

    def write(self, path: str):
        problems = self.problems()
        if problems:
            raise ValueError("refusing to write " + path + ":\n  " + "\n  ".join(problems))
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = self.encode()
        if os.path.exists(path) and open(path, "rb").read() == data:
            return False
        with open(path, "wb") as f:
            f.write(data)
        return True

    def encode(self) -> bytes:
        """Same effect, same bytes: a fixed gzip time and stable ids keep the resource pack's SHA-1 unchanged."""
        return gzip.compress(nbt.dumps(self.root()), mtime=0)


def _stable_id(name: str) -> nbt.IntArray:
    raw = uuid.uuid5(uuid.NAMESPACE_URL, "ordertest:fx/" + name).int
    words = [(raw >> shift) & 0xFFFFFFFF for shift in (96, 64, 32, 0)]
    return nbt.IntArray([w - (1 << 32) if w >= 1 << 31 else w for w in words])
