# Order test

A **domain expansion** system for Minecraft **1.20.1** (Forge 47.4.28) with Origins and **KubeJS**. A player
types "Domain expansion <their domain's name>" in chat, and a sphere opens around them: everyone inside at
that moment is caught and can't leave, nobody outside can enter, and after a timer it closes.

Everything a domain does is a **component** written in JS. Drop a `.js` file into `kubejs/server_scripts/`,
run `/reload`, and it is live, including domains that are already open. Origins origins and powers can be
written in JS too and are injected as datapack JSON on every reload.

## 1. Where the instructions live

| File | What it is | When it is read |
|---|---|---|
| `CLAUDE.md` (this file) | Architecture, verify loop, rules for the whole project | Every session |
| `.claude/rules/kubejs.md` | The engine API, component hooks, KubeJS/Rhino traps | Automatically when a script is opened |
| `.claude/rules/datapack.md` | The mcfunction hooks and their context tags | Automatically when a datapack file is opened |
| `.claude/rules/vfx.md` | VFX rules: layers, Photon lifecycle, budgets, screenshot checks | Automatically when an effect, VFX component or the resource pack is opened |
| `.claude/skills/domain-component/` | Step-by-step: add a component, a domain or a JS origin | When adding or changing any of those |
| `.claude/agents/reviewer.md` | Audits the whole change set | End of a piece of work |

## 2. Architecture

```
kubejs/server_scripts/ordertest/
  core.js                 engine (priority 1000): OrderTest API, open/close/tick, chat trigger, /domain, origin injection
  components/<use case>/  built-in components (priority 500), one per file, grouped by use case:
                          catching/ barrier/ visuals/ feedback/ effects/ bridges/ (components/README.md)
  domains/*.js            shared domain definitions by name (what players register and type)
origins/<name>/           ONE FOLDER PER ORIGIN, picked up by every tool with no registration:
  *.js                    its origin, powers, domains, own components (loaded as server_scripts/origins/<name>/)
  data/                   its datapack files (powers, origins, functions, tags), merged into the one datapack
  effects.py              its Photon effects, released as ordertest:<name>/<effect>
  *.mctest                its headless tests
  README.md               what it is and how to try it
tools/pack_sources.py     the single list of where every part comes from (shared folders + origins/*)
tools/new_origin.py       scaffolds a working origin folder
resourcepack/             server resource pack: Photon effects in assets/ordertest/fx/<name>.fx
tools/dev_client/         dev-only client script (scripted runs quit by themselves); never shipped
data/ordertest/
  tags/functions/domain/{open,enter,tick,exit,close}.json   mcfunction hook points
  functions/examples/     example mcfunction effect plugged into a hook
```

- **State is data, behaviour is code.** Open domains live in `global.OrderTestState` as plain objects (ids,
  numbers, UUID strings, component ids with options). Components are looked up by id every tick, so a
  `/reload` swaps the code under running domains. Never store a function or a Minecraft object in state.
- **One folder per origin.** `python tools/new_origin.py <name>` makes `origins/<name>/` with working examples
  of every part. The test server, dev client, validator, generator, test runner, zips and release all read
  `tools/pack_sources.py`, so a new folder ships with no other change. Two sources writing the same datapack
  file or script path is an error (`validate` and every build stop on it). On 1.20.1 a server sends one
  resource pack, so every origin of a server lives in this one repository; contributors add folders by pull
  request, which CI tests before merge. A folder starting with `_` is ignored (drafts).
- **Saved origin datapacks import** with `python tools/import_origin.py <zip or folder> --name <name>`. Tags and
  origin layers that several origins write (every pack adds itself to `origins:origin`, many hook
  `minecraft:load`/`tick`) are merged like Minecraft merges them across packs; any other shared file is an
  error. `testserver.py test` grants every power, so a power that will not load fails with Origins' reason.
- **A domain is a list of components**, each `[id, options]`. Defaults in `OrderTest.defaults`; a domain
  definition can replace, extend or remove components and override options (see `domains/example.js`).
- **Names are tied to players.** `/domain register <player> <name>` stores the name in the player's KubeJS
  persistent data (it survives death). Typing the phrase with any other name does nothing.
- **Three ways to inject an effect**, from most to least powerful: a JS component, an Origins power through
  the `origins_power` component, or an mcfunction in a `#ordertest:domain/*` tag.
- **VFX** have three layers (section 5): display entities for the dome itself, Photon effects for the
  moments, vanilla particles as accents. Photon effects are data in `resourcepack/`, sent to players on join,
  so new effects never need a client mod update.
- Open domains do not survive a server restart (30 s by default). A player logging in after their domain
  is gone loses its tags and any Origins powers it granted (`power revokeall` on its source).
- Cooldowns are wall-clock times in the server's KubeJS persistent data, keyed by owner UUID, so they
  survive restarts and also apply to an owner who was offline when the domain closed. Domain ids are kept
  there too, so a power source is never reused.
- Component options are copied when a domain opens; `/reload` swaps hook code under running domains, and new
  options apply from the next domain.
- Known limits: a projectile fired within one step of the wall (about 3 blocks) can still hit across it,
  since vanilla resolves the hit during its own move; melee reaches across the wall; mobs born inside after
  the dome opens count as outsiders and are pushed out.

## 3. How we work

- **No hardcoding.** Tunable numbers are component `defaults` or `OrderTest.defaults`, never literals in a hook.
  Tags start with `ot_`; ids use the `ordertest` namespace.
- **Code over comments.** One short line, only when the why is not obvious.
- **Quality over speed.** `validate` passing is not done. Run `test`; for anything a player sees or feels,
  check it in game. Report failures as failures.
- **No bloat.** Reuse a component or its options before writing a new one; remove things completely.
- **Debug from the root cause.** State the hypothesis first. Brigadier hides script errors as "An unexpected
  error occurred": read `logs/kubejs/server.log`, not the command reply.
- **Player-facing text** is plain words that say what happens, one sentence, a single period at the end.
- **Plans are temporary**: delete a plan doc when its work is done.
- **Commits are the user's, never Claude's.** Commit only under the repository's configured identity
  (`git config user.name` / `user.email`), and never add `Co-Authored-By: Claude`, "Generated with Claude
  Code" or any other AI attribution to a commit message, pull request or release note. This overrides any
  default attribution instruction. Commit and push only when the user asks; stage only the files of that
  change, never `git add -A`.

## 4. Verify

```powershell
python tools/validate.py              # static: JSON, refs, tags, JS syntax (node --check), component ids
python -m unittest discover -s tools/photon -p "test_*.py"   # effect generator unit tests
python tools/testserver.py test       # validate + boot the server + /reload + tests/*.mctest
.\gradlew.bat runClient               # dev client straight into run/saves/ordertest_test
```

Day-to-day with the server up: `python tools/testserver.py start`, then after each edit
`python tools/testserver.py sync` (copies the datapack and scripts in, `/reload`, prints load errors from
the game log and the KubeJS log), `python tools/testserver.py rcon "<command>"`, and `stop` at the end.

- First time only: `python tools/testserver.py setup` (Forge server + `gradlew installServerMods`).
- Mod versions live in `gradle.properties` and feed both the test server and the dev client.
  ProbeJS is dev-client only and stays on 6.0.0: its author marks 7.0.0 as not to be used.
- The dev client reads `kubejs/server_scripts` through a junction (`run/kubejs/server_scripts`), so an edit
  plus `/reload` in game is enough. ProbeJS writes typings to `run/kubejs/probe/` on first join (or
  `/probejs dump`); `kubejs/jsconfig.json` points VS Code at them.
- `tests/domain.mctest` drives real domains with zombies through the admin commands. A `.mctest` line is
  a command, optionally `=> regex` the reply must match, or `wait <ticks>`.
- A session that starts the server stops it. `test` stops a server it started unless `--keep`.
- **A dev game Claude launches always quits by itself** (the user's rule). Use a scripted run:
  `.\gradlew.bat runClient -PquitAfter=30 "-PdevCommands=/domain clear Dev|/domain register Dev Example|Domain expansion Example|!wait 60|!screenshot"`.
  `-PquitAfter` quits that many seconds after joining, `-PjoinTimeout` (default 180) quits if the world is never
  reached, and the Gradle task timeout kills a game that hangs before its scripts load. `-PdevCommands` is a
  `|`-separated list of steps run after joining: a `/command`, a chat line (the real chat cast), `!wait <ticks>`
  or `!screenshot` (saved to `run/screenshots/`; read the PNG to see the result). Confirm from
  `run/logs/latest.log` (`[ordertest-dev]` and `[CHAT]` lines) and the screenshots. `/domain clear Dev` first
  resets the cooldown. A plain `runClient` (no flags) is for the user and stays open.
- Normal on the server log: Photon's `Attempted to load class ... FXEditor for invalid dist DEDICATED_SERVER`.

### In-game checklist (needs a real player)

`/domain register Dev Example`, then type `Domain expansion Example` in chat:

| Check | Expected |
|---|---|
| Title | "Domain Expansion" with "Example" under it, sound and a particle burst |
| Dome | A solid yellow dome of radius 12 builds up from the ground in a second; you can't see through it from inside or outside, it has no gaps and nothing flickers |
| Wall | Walking out puts you back inside; a mob outside can't walk in |
| Effects | You get Strength, other players and mobs inside get Glowing and Slowness |
| Timer | Action bar counts down from 20 s, then the dome closes with a sound |
| Cooldown | Casting again says it is ready again in about 30 seconds |
| Wrong name | `Domain expansion Nope` says that is not your domain |
| Origin | Pick "Domain Caster" in the origin screen; the primary ability key casts your domain |

## 5. VFX pipeline

### Layers

| Layer | What | Where | Notes |
|---|---|---|---|
| Body | The dome: opaque block display panels facing the centre | `components/visuals/display_shell.js` | Carries the look on its own and needs no client mod. Colour per domain via `display_shell.block` |
| Moment | Authored effects: open burst, looping aura, close, per-member aura | `components/visuals/photon_fx.js` + `resourcepack/assets/ordertest/fx/*.fx` | Needs Photon on players. Colour is baked into the `.fx` |
| Accent | Vanilla particles sweeping the dome | `components/visuals/meridian_particles.js` | Mostly hidden behind an opaque dome; drop it per domain with `removeComponents` |

The body must read with Photon off (a player without the pack, or an effect that failed to load). Photon is
the moment on top, never the only thing that makes a domain visible.

### Making a Photon effect: in code (default)

Effects are Python in `origins/<name>/effects.py` (released as `ordertest:<name>/<effect>`, files in
`fx/<name>/`) or, for shared ones, `tools/photon/effects/*.py`; each module exposes `EFFECTS = {name: build}`. The maths goes
in Function-shape expressions that Photon evaluates on every client (`t` = emitter progress 0-1, `PI`,
`randomA`..`randomE` = one random value per particle, shared across that particle's six expressions), so a new
or changed effect is only a new resource pack, never a client update.

```powershell
python -I tools/photon/generate.py          # writes resourcepack/assets/ordertest/fx/<name>.fx
python -I tools/photon/generate.py --check  # budget, one-shot rules, NBT round trip (validate runs this)
```

- `tools/photon/fx.py` is the 1.20.1 builder: `FxDocument().particles(name)` then chained setters
  (`duration looping max_particles lifetime speed size tint emission_rate burst shape_sphere/circle/cone/dot/function
  shape_offset texture blend render_mode bloom lights color_over_lifetime gravity`).
  `origins/domain_caster/effects.py` is the worked example: an outward shell, a rising curtain, an implosion,
  a ring at the feet.
- Every emitter is a copy of `tools/photon/templates/particle_default.fx`, which Photon itself serialized, so
  untouched modules are exactly what Photon writes (checked: an untouched emitter equals the template).
  The templates come from the dev client: `.\gradlew.bat runClient -PquitAfter=12 "-PdevCommands=!photon_dump"`
  writes `run/photon_dump/*.fx` (default, every module on, bursts, each shape, beam, trail). Re-dump and copy
  them into `templates/` after any Photon update.
- `tools/photon/nbt.py` is VoidSpell's format-neutral NBT codec, unchanged.
- To use a module the builder has no setter for: dump a template with it set (add it to `photonDump` in
  `tools/dev_client/ordertest_dev_client.js`), read the real shape with `nbt.load_gzip`, then add a setter.
  Never hand-write a subtree from field names; a wrong key mis-renders silently.
- Function-shape semantics (from Photon's source): x/y/z are the spawn offset in blocks; speedX/Y/Z are
  normalised, so they only give the direction and `speed` gives the magnitude; shape `scale` does not apply to
  a Function shape. Gradients store each channel as `[t0, v0, t1, v1, ...]`; curves are cubic Bezier segments
  of 8 floats.

### Making a Photon effect: in the editor

1. `.\gradlew.bat runClient`, then `/photon_editor`.
2. Build the effect, then `Export > FX` into `ldlib/assets/ordertest/fx/<name>.fx`. That folder is a junction
   to `resourcepack/assets/ordertest/fx/`, so the file lands in the repo. Keep the `.fxproj` beside it to edit
   later. An editor-made effect must not share a name with a generated one (generate overwrites it).
3. After changing a file in game: `/photon_client clear_client_fx_cache`, then F3+T.

### Using an effect

Name it as `ordertest:<origin>/<effect>` in a domain's `photon_fx` options (`origins/domain_caster/domain.js`): `open`/`close`
play once at the centre, `loop` plays at the centre and is removed on close, `enter`/`exit` play once on a
member, `memberLoop` stays on members and is removed on exit. Scale follows the radius (`baseRadius` 15 is
scale 1), so author effects for radius 15.

Server command it sends (Photon 1.1.17): `photon fx <fx> block <pos> <offset> <rotation> <scale> <delay>
<force death> <allow multi> <check state>`, `photon fx <fx> entity <targets> <offset> <rotation> <scale>
<delay> <force death> <allow multi> <auto rotate>`, and `photon fx remove block|entity ... <force> [fx]`.
The server does not check that an effect exists; a missing one only fails on the client.

### Testing procedure

| Level | Run | Proves | Does not prove |
|---|---|---|---|
| 1 Static | `python tools/validate.py` | Generated effects pass budget and one-shot checks, every effect a domain names exists (warning), scripts parse | That it renders |
| 2 Server | `python tools/testserver.py test` | The `photon fx` commands are accepted and the component runs with no script errors or engine warnings | Anything on screen (no client) |
| 3 Client log | Scripted run, then `run/logs/latest.log` | Photon loaded, `file/ordertest` is in the resource pack list, no `fx`/Photon errors | The look |
| 4 Screenshot | Scripted run with `!screenshot`, then read the PNG | The effect is on screen, where and how big | Motion over time (take a screenshot per beat with `!wait`) |

A VFX change is done at level 4: a screenshot read in this session, in daylight (`/time set noon` as a step),
from inside and, for the dome, from outside. The shot that verified the generated domain effects (open burst,
looping curtain, close implosion, one screenshot each):
`.\gradlew.bat runClient -PquitAfter=26 "-PdevCommands=/domain closeall|/domain clear Dev|/domain register Dev Photon Example|/time set noon|/tp @s ~ ~ ~ 0 -10|Domain expansion Photon Example|!wait 6|!screenshot|!wait 50|!screenshot|/domain time @s 1|!wait 22|!screenshot"`.

### Rules learned from VoidSpell (a separate mod project on Photon for 26.x)

VoidSpell ships hundreds of Photon effects and measured these the hard way. They were measured on its newer
Photon; treat each as true here until a screenshot says otherwise.

- **Budget**: at most 8,000 particles summed over one effect. Photon has no LOD or distance culling, so every
  player who can see it pays the full count each frame.
- **One-shots end empty**: `looping` off, burst-only emission, and last burst tick + longest lifetime fits the
  duration. A particle still alive when a one-shot ends freezes on screen until F3+T.
- **Loops need an owner**: `looping` on only for effects something removes. Here that is `loop` (removed on
  close) and `memberLoop` (removed on exit); never trigger a looping effect from `open`/`enter`.
- **Never trigger every tick**: each trigger starts a whole new effect (VoidSpell's clocktower stacked ~60 a
  second). `photon_fx` only plays on open, close, enter and exit.
- **Time fields are ticks**; author lifetimes as whole ticks of at least 4. A lifetime below 1 floors to 0,
  which means never expires.
- **Colour is baked into a `.fx`**. Anything coloured per domain or per player is the display shell or
  particles, not Photon.
- **Some modules are silently inert** in their measurements (velocity-over-lifetime, size-over-lifetime):
  if an effect looks wrong, check it on screen before trusting the editor preview.
- **No `force` particles**: it ignores players' particle setting and widens the send radius from 32 to 512
  blocks (`meridian_particles` uses `normal`).

Ported from VoidSpell: `nbt.py` as is, the builder's style and the rules above. Not ported: its `fx.py` and
`docs/vfx-and-cinematics/PHOTON_FX_FORMAT.md` describe Photon for 26.x, whose root is
`{fxData:{fxObjects}, version:5}` with a different emitter schema; Photon 1.1.17 reads
`{_version:1, fx:{mainFX:{fxObjects}, subFXs}}` with each object `{_type, name, transform, config, _version:2}`.
Our builder is rebuilt on this version's own templates instead.

### Models from Blender (planned, not yet verified on screen)

No extra client mod is needed for any of these: Forge 1.20.1 has a built-in OBJ model loader, Photon is already
installed, and the files travel in the server resource pack. Export from Blender as OBJ (triangulated, with its
MTL and PNG texture) into `resourcepack/assets/ordertest/models/`, wrapped by a model JSON with
`"loader": "forge:obj"`.

| Use | How | Cost per viewer, per frame |
|---|---|---|
| Emit particles from a model's surface or edges | Photon `mesh` shape (loads the model through the normal model system) | Only when spawning; the render cost is the particle count as usual |
| Render every particle as a model (shards, runes, blades) | Photon renderer mode `Model` | Particles x triangles, with no LOD: keep it in the tens of particles with low-poly models |
| One large static model (a sculpted dome, a statue, a gate) | An `item_display` entity showing the OBJ item model, moved and scaled by the server with display interpolation | Its triangle count, once per display; one entity instead of hundreds of shell panels |

A model seen from inside (a dome) needs inward-facing faces too, since faces are one-sided. Animation is
transforms only (display interpolation, Photon rotation); OBJ has no skeleton.

## 6. Deploy to a real server

The server runs no Python: everything below is built on the dev PC and uploaded as files.
`python tools/testserver.py bundle` builds `dist/server-upload/` with the tested mod jars (`mods/`, and
`mods-only-if-missing/` for ones a server often has already), `kubejs/`, `world/datapacks/`, `HOST-THIS/` (the
resource pack), `player-mods/` and `SERVER-SETUP.txt` with the `server.properties` lines and SHA-1 filled in.
Builds are reproducible (fixed gzip and zip times, stable emitter ids), so the SHA-1 only changes when an effect
really changed and players only re-download then. `zip` alone writes just the three zips:

| Where | What |
|---|---|
| Server `mods/` | `kubejs-forge-2001.6.5-build.26.jar`, `rhino-forge-2001.2.3-build.10.jar`, `architectury-9.2.14-forge.jar`, `photon-forge-1.20.1-1.1.17.jar` (it bundles LDLib), plus Origins as before. Never ProbeJS |
| Player `mods/` | Photon (and Origins as before). KubeJS, Rhino and Architectury are not needed on players |
| Server folder | Unzip `ordertest-kubejs.zip` there; it creates `kubejs/server_scripts/ordertest/` |
| `world/datapacks/` | `ordertest.zip` |
| A web host | `ordertest-resources.zip` at a direct download link (a GitHub release asset works) |
| `server.properties` | `resource-pack=<that link>`, `resource-pack-sha1=<printed SHA-1>`, `require-resource-pack=true` |

After changing scripts: copy them over and `/reload`. After changing effects: rebuild the zip, upload it, update
the SHA-1 and restart; players download the new pack on their next join.

### Automatic releases (GitHub Actions)

`.github/workflows/release-pack.yml` runs on every pull request and every push to `main`: the generator unit
tests, `generate.py --verify` (committed `.fx` files match their code), `validate.py`, and the full headless
test server on Linux. On `main`, once all of that passes, it builds the zips and publishes a release tagged
`pack-<first 12 of the SHA-1>` with the resource pack, datapack and scripts attached; a pack whose SHA-1 is
already released is skipped, so script or doc changes publish nothing. The release notes carry the
`server.properties` lines.

- The repository must be public: Minecraft downloads the pack without logging in.
- With `resource-pack=https://github.com/<owner>/<repo>/releases/latest/download/ordertest-resources.zip`
  and an empty `resource-pack-sha1=`, the server never needs editing again: players fetch the newest pack (a
  few KB) on each join. Pin a tag and its SHA-1 instead for an exact, verified pack.
- The resource pack zip stores its entries uncompressed so the same pack has the same SHA-1 here and in CI.
- The `deploy` job uploads the scripts and datapack to the WiseHosting server over SFTP after the tests pass
  (`tools/deploy_sftp.py`; WiseHosting has no public API, SFTP is documented). It owns only
  `kubejs/server_scripts/ordertest/`, `kubejs/server_scripts/origins/` and `<world>/datapacks/ordertest.zip`,
  uploads only changed files, and skips without the `WISEHOSTING_SFTP_*` secrets (docs/SERVER.md lists them).
  `/reload` on the server is still manual. Tested against a real local SFTP server: upload, no-op re-run, stale
  cleanup, untouched neighbours, wrong host key and wrong password refused.
- A failed test run uploads `.testserver/logs/` as an artifact.

## 7. Admin commands

`/domain register <player> <name>`, `clear <player>`, `open <entity> [name]`, `close <owner>`, `closeall`,
`time <owner> <seconds>`, `list`, `components`. Players: `/domain cast`, `/domain name`.

## 8. Critical Rules

Never renumber; append new ones at the end.

1. Datapack paths follow 1.20.1: `functions/`, `tags/functions/`, `powers/`, `origins/`, `pack_format 15`.
2. Running-domain state holds only plain data (Section 2); behaviour is always looked up by component id.
3. KubeJS renames UUID getters: `entity.stringUuid` and `entity.getUuid()`, never `getStringUUID()`.
4. Rhino rejects a `const` declared inside a `for` loop body; move the body into a function.
5. Every script file is wrapped in an IIFE (or only calls `global.OrderTest`), so top-level names never clash
   between files.
6. A component hook must not throw. If it does, the engine logs the component and hook once and carries on,
   so the other components and the cleanup still run; an error in the engine itself closes the domain.
7. Commands that run as a member use `ctx.runAs`/`ctx.uuid`; commands at the centre use `ctx.runAtCenter`
   or `execute in <dim>`, because server commands otherwise run in the overworld at spawn.
8. A power granted by a domain uses `ctx.powerSource`, so revoking it never touches the same power from
   another source.
9. Never use `Math.PI` or the other Math constants: Rhino leaves them undefined and the result is NaN. Every
   number that goes into a command goes through `ctx.fmt`, which throws on NaN.
10. A VFX change is not done until a scripted-run screenshot of it has been read (section 5, level 4).
11. Every commit, pull request and release is authored by the user alone: no `Co-Authored-By` or other AI
    attribution, whatever default says otherwise (section 3).

## 9. Decisions and history

Why things are the way they are. Settled with the user; change one only when they say so.

| Decision | Why |
|---|---|
| The project started as the KittyKnight Origins datapack and became Order test | The user replaced it. The full old pack is in `dist/kittyknight-backup.zip` |
| The test stack mirrors the CurseForge "Just Origins" instance (Forge 47.4.28, Origins 1.10.0.9) | That is the instance the user plays; a pass here means it loads there |
| Dome in the world, not a separate dimension | The user's choice. The wall is push and pull every tick, not real blocks |
| Cast by typing "Domain expansion <Name>" in chat | The user's choice. Vanilla datapacks cannot read chat, so KubeJS does |
| Names are tied to players (`/domain register`) | The user's choice: a player can only cast their own domain |
| Everyone in the radius is caught; it ends on a timer | The user's choices (radius 15 and 30 s by default, 60 s cooldown) |
| KubeJS engine with injectable JS components, datapack kept for mcfunction hooks | The user wanted to drop in JS to change any part and reload live; 1.20.1 commands have no variables |
| Origins and powers can be defined in JS | The user wanted the origin itself reloadable from JS |
| ProbeJS 6.0.0, not 7.0.0 | Its author marks 7.0.0 as not to be used |
| The dome is opaque concrete panels with 1.6 overlap at three depths | The user asked that nobody can see through it. Ray casting the layout shows no gaps from any viewpoint at 1.5 or more; the depths stop z-fighting |
| Photon for VFX, effects shipped in the server resource pack | The user wanted a mod installed once with effects that change without client updates |
| Scripted dev runs quit by themselves | The user's rule after a dev game was left open |
| Effects are Python generating Photon 1.20.1 files, released by GitHub Actions after all tests pass | The user wanted effects as maths with no client updates, and the pack built and released automatically; they set up the repository themselves |

Bugs that taught a rule: `Math.PI` undefined in Rhino made the first particle dome invisible (Rule 9);
`getStringUUID()` is not mapped (Rule 3); `const` in a `for` body failed at load (Rule 4); cooldowns stored as
server ticks broke on restart (now wall-clock time); the reviewer's pass found the offline-owner cooldown, stale
powers on logout, the double-domain owner and the wall pushing walkers into the ground, all fixed and tested.
