#!/usr/bin/env python3
"""Create a new origin folder with working examples of every part, picked up by every tool automatically.

    python tools/new_origin.py storm_caller                    # origins/storm_caller/
    python tools/new_origin.py storm_caller --title "Storm Caller"

It writes: origin.js (the origin, in JS), data/ (a power as plain datapack JSON, merged into the shipped
datapack), domain.js (a domain), effects.py (a Photon effect), tests.mctest and README.md. Run
`python -I tools/photon/generate.py` afterwards to build the effect, then the usual tests.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pack_sources  # noqa: E402

NAMESPACE = "ordertest"
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,31}$")

ORIGIN_JS = """// The {title} origin, written in JS and injected as Origins JSON on every /reload. Its passive power is plain
// datapack JSON in this folder's data/, which the tools merge into the shipped datapack.
global.OrderTest.origin('{ns}:{name}', {{
  name: '{title}',
  description: 'Describe what this origin does in one plain sentence.',
  icon: {{ item: 'minecraft:amethyst_shard' }},
  impact: 1,
  order: 300,
  powers: ['{ns}:{name}/night_eyes'],
  layer: 'origins:origin'
}})
"""

POWER_JSON = """{{
  "type": "origins:night_vision",
  "name": "Night Eyes",
  "description": "You see in the dark.",
  "strength": 0.6
}}
"""

DOMAIN_JS = """// The {title} domain. Give it to a player with /domain register <player> {title}.
global.OrderTest.domain('{title}', {{
  radius: 12,
  duration: 20,
  cooldown: 30,
  extraComponents: [
    ['photon_fx', {{ open: '{ns}:{name}/burst' }}]
  ],
  options: {{
    display_shell: {{ block: 'minecraft:purple_concrete' }}
  }}
}})
"""

EFFECTS_PY = '''"""{title} effects, released as {ns}:{name}/<effect>. Authored for radius 15; photon_fx scales them."""
import fx


def burst():
    """A ring of light thrown outward along the ground, once."""
    doc = fx.FxDocument()
    ring = doc.particles("burst_ring")
    ring.looping(False).duration(30).emission_rate(0).burst(time=0, count=300).max_particles(300)
    ring.shape_function(speed_x="cos(2*PI*randomA)", speed_y="0.1", speed_z="sin(2*PI*randomA)")
    ring.lifetime(20).speed(12).size(0.35).lights()
    ring.color_over_lifetime([(0.0, 1.0, 1.0, 1.0, 1.0), (1.0, 0.7, 0.4, 1.0, 0.0)])
    return doc


EFFECTS = {{"burst": burst}}
'''

TESTS = """# {title}: headless tests. A line is a command, optionally "=> regex" the reply must match; "wait <ticks>" pauses.
# Every power in data/ and every OrderTest.power is also checked to load by the test runner itself.

# forceload loads the chunk asynchronously, so wait before summoning into it.
forceload add {x} {x} {x2} {x2}
wait 20
kill @e[tag=t_{name}]
summon minecraft:zombie {cx} -60 {cx} {{Tags:["t_{name}"],NoAI:1b,Silent:1b,Invulnerable:1b,PersistenceRequired:1b}} => Summoned new Zombie

domain open @e[tag=t_{name},limit=1] {title} => Opened {title}
execute if entity @e[tag=t_{name},tag=ot_in_{slug}] => Test passed, count: 1
domain close @e[tag=t_{name},limit=1] => Closed {title}

kill @e[tag=t_{name}]
forceload remove {x} {x} {x2} {x2}
"""

README = """# {title}

Describe the origin here: what it is, how it plays, and what its domain looks like.

| File | What |
|---|---|
| `origin.js` | The origin (JS) |
| `data/{ns}/powers/{name}/` | Its powers as plain datapack JSON, merged into the shipped datapack |
| `domain.js` | Its domain |
| `effects.py` | Its Photon effects, released as `{ns}:{name}/<effect>` |
| `tests.mctest` | Headless tests |

Try it: pick **{title}** in the origin screen, `/domain register <you> {title}`, then type
`Domain expansion {title}`.
"""


def domain_slug(title: str) -> str:
    """The engine's tag for a domain's members is ot_in_<slug of the domain name> (core.js slugOf)."""
    return re.sub(r"^_+|_+$", "", re.sub(r"[^a-z0-9]+", "_", title.strip().lower())) or "domain"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name", help="folder and id name: lowercase letters, digits and _")
    parser.add_argument("--title", help="display name (default: the name in Title Case)")
    args = parser.parse_args()
    if not NAME_PATTERN.match(args.name):
        raise SystemExit("name must be 2-32 lowercase letters, digits or _, starting with a letter")
    folder = pack_sources.ORIGINS_DIR / args.name
    if folder.exists():
        raise SystemExit(f"{folder.relative_to(pack_sources.REPO)} already exists")
    title = args.title or args.name.replace("_", " ").title()
    # Each origin's test zombie stands in its own spot so origin tests never overlap.
    spot = 400 + 64 * len(pack_sources.origin_dirs())
    values = dict(ns=NAMESPACE, name=args.name, title=title, slug=domain_slug(title), x=spot, x2=spot + 16,
                  cx=f"{spot + 8}.5")
    files = {
        "origin.js": ORIGIN_JS,
        f"data/{NAMESPACE}/powers/{args.name}/night_eyes.json": POWER_JSON,
        "domain.js": DOMAIN_JS,
        "effects.py": EFFECTS_PY,
        "tests.mctest": TESTS,
        "README.md": README,
    }
    for rel, template in files.items():
        path = folder / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(template.format(**values), encoding="utf-8")
        print(f"  wrote {path.relative_to(pack_sources.REPO).as_posix()}")
    print(f"\nNext: python -I tools/photon/generate.py, then python tools/validate.py and python tools/testserver.py test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
