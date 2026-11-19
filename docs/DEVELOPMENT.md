# Development guide

How the system is built, how to make domains and effects, how to test them, and how releases happen.
`CLAUDE.md` holds the full rules and traps; this guide is the overview.

## How it fits together

```
kubejs/server_scripts/ordertest/   the engine and everything a domain does (KubeJS, runs on the server)
  core.js                          open/close/tick, the chat trigger, /domain, Origins injection
  components/*.js                  one behaviour per file: the wall, the dome, effects, titles, sounds...
  domains/*.js                     named domains: which components, radius, duration, cooldown
  origins/*.js                     Origins origins and powers written in JS
data/ordertest/                    datapack: mcfunction hooks other packs can plug effects into
tools/photon/effects/*.py          Photon effects as Python; generate.py writes them into resourcepack/
resourcepack/                      what players download: assets/ordertest/fx/*.fx
tests/domain.mctest                headless tests driven over RCON
tools/                             the test server, validator, generator and dev-client helpers
```

A domain is a list of **components**. Each component is a small JS object with hooks (`open`, `enter`, `tick`,
`memberTick`, `exit`, `close`). Drop a new file in `kubejs/server_scripts/ordertest/`, run `/reload`, and it
is live, even under domains that are already open. Effects are Photon files whose shapes are maths
expressions evaluated on each player's game, so new effects never need a client update.

## Requirements

- Windows with PowerShell (the dev client and junctions are set up for Windows; CI runs the same tests on Linux)
- JDK 17 or 21 (`JAVA_HOME` set). Gradle downloads its own Java 17 toolchain for the game
- Python 3.12 or newer, Node.js (for script syntax checks), Git
- Optional: VS Code with the recommended extensions in `.vscode/extensions.json`

## First-time setup

```powershell
python tools/testserver.py setup        # installs a local Forge test server with the same mods
.\gradlew.bat runClient                 # first run downloads Minecraft; opens straight into a test world
```

## Making a domain

`kubejs/server_scripts/ordertest/domains/example.js` shows every option:

```js
global.OrderTest.domain('Infinite Garden', {
  radius: 20, duration: 30, cooldown: 60,
  extraComponents: [['potion_effect', { effect: 'minecraft:slowness', target: 'others' }]],
  options: { display_shell: { block: 'minecraft:green_concrete' } }
})
```

Give it to a player with `/domain register <player> Infinite Garden`. A name with no definition still works
and uses the default components.

## Making a component

Copy the closest file in `components/` (`potion_effect.js` for something per player, `sphere_barrier.js` for
per-tick world logic). Put every tunable number in `defaults`. Hooks receive a `ctx` with the domain's
position, radius, members and helpers (`ctx.run`, `ctx.runAs`, `ctx.teleport`, `ctx.fmt` ...). The full API
and the Rhino traps (no `Math.PI`, no `const` inside a `for` body, UUID getter names) are in
`.claude/rules/kubejs.md`.

## Making an effect

Effects are Python in `tools/photon/effects/*.py`; `domain.py` is the worked example.

```python
import fx

def ring_burst():
    doc = fx.FxDocument()
    ring = doc.particles("ring")
    ring.looping(False).duration(30).emission_rate(0).burst(time=0, count=400).max_particles(400)
    ring.shape_function(x="15*cos(2*PI*randomA)", y="0", z="15*sin(2*PI*randomA)", speed_y="1")
    ring.lifetime(20).speed(2).size(0.3).color_over_lifetime([(0, 1, 1, 1, 1), (1, 0.6, 0.3, 1, 0)])
    return doc

EFFECTS = {"ring_burst": ring_burst}
```

In the expressions, `t` is the effect's progress (0 to 1), `PI` is pi, and `randomA` to `randomE` are random
per particle. x/y/z place the particle; speed_x/y/z give its direction and `speed` how fast.

```powershell
python -I tools/photon/generate.py      # writes resourcepack/assets/ordertest/fx/ring_burst.fx
```

Play it from a domain with the `photon_fx` component (`domains/photon_example.js`): `open`, `close` and
`loop` at the centre, `enter`, `exit` and `memberLoop` on the people inside. Effects can also be made by hand
with `/photon_editor` in the dev client.

The generator refuses an effect over 8,000 particles, and a one-shot effect that would leave particles frozen
on screen.

## Testing

| Run | Checks |
|---|---|
| `python -m unittest discover -s tools/photon -p "test_*.py"` | The effect generator |
| `python tools/validate.py` | JSON, references, script syntax, component names, effect rules |
| `python tools/testserver.py test` | Boots the real Forge server and drives domains with zombies (opening, wall, effects, timer, cooldown, Origins) |
| A scripted dev run | Anything you need to see. It quits by itself and can take screenshots |

```powershell
.\gradlew.bat runClient -PquitAfter=30 "-PdevCommands=/domain clear Dev|/domain register Dev Photon Example|/time set noon|Domain expansion Photon Example|!wait 10|!screenshot"
```

Screenshots land in `run/screenshots/`. A plain `.\gradlew.bat runClient` stays open for playing.

## Releasing

Push to `main`. GitHub Actions (`.github/workflows/release-pack.yml`) then:

1. runs the generator unit tests, checks the committed `.fx` files match their code, runs the validator, and
   boots the full test server on Linux;
2. if everything passes, builds the resource pack, datapack and scripts, and publishes a release named after
   the pack's SHA-1. A pack that is already released is skipped.

Servers using the `latest` link (see `docs/SERVER.md`) pick up new effects with no action. Scripts and the
datapack still need copying to the server; they are attached to each release.

Before pushing effects, run `python -I tools/photon/generate.py` and commit the `.fx` files it changed; CI
fails if they do not match the code.

## Building files for a server by hand

`python tools/testserver.py bundle` builds `dist/server-upload/` with the tested mod jars, scripts, datapack,
resource pack and a `SERVER-SETUP.txt` with the `server.properties` lines filled in.
