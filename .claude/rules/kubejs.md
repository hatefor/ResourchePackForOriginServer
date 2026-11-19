---
paths:
  - "kubejs/**"
  - "origins/**/*.js"
---

# KubeJS engine (KubeJS 2001.6.5, Rhino, Forge 1.20.1)

## API (`global.OrderTest`)

| Call | Does |
|---|---|
| `component(id, spec)` | Registers a component. `spec.defaults` are its options; hooks below |
| `domain(name, spec)` | Defines a domain by name: `radius`, `duration` (s), `cooldown` (s), `components`, `extraComponents`, `removeComponents`, `options` |
| `power(id, json)` / `origin(id, spec)` | Origins JSON injected on `/reload` (`spec.layer`, default `origins:origin`) |
| `open(server, caster, name)` / `close(server, domain)` | Open or close from another script |
| `domainOf(entity)` / `ownedBy(entity)` / `registeredName(player)` | Lookups |

## Component hooks

| Hook | Called | Arguments |
|---|---|---|
| `open` | once, after the owner is added | `ctx` |
| `enter` | when an entity is caught | `ctx, entity` |
| `tick` | every tick | `ctx` |
| `memberTick` | every tick, per live member | `ctx, entity` |
| `exit` | member leaves, dies or the domain closes | `ctx, entity` |
| `close` | once, before members are released | `ctx` |

`ctx` gives `id name slug owner dim x y z radius age ticksLeft durationTicks server level`, `options` (this
component's merged options), `store` (per-domain scratch object for this component), `nameTag`,
`powerSource`, and helpers `members() addMember(e) removeMember(e) isMember(e) isOwner(e) ownerEntity()
distance(e) distanceTo(x,y,z) inSameDimension(e) entitiesWithin(range) teleport(e,x,y,z) placeAtDistance(e,d)
run(cmd) runAs(e,cmd) runAtCenter(cmd) uuid(e) fmt(n) close()`. `placeAtDistance` keeps the entity's height
when the sphere reaches it, so walkers move sideways along the ground.

## Priorities

`// priority: N` on the first line; higher loads first. `core.js` 1000, components 500, content 0. A file
that calls `global.OrderTest` must load after `core.js`.

## Verified accessors (production server, probed)

| Works | Fails |
|---|---|
| `e.stringUuid`, `e.uuid`, `e.getUuid()` | `e.getStringUUID()`, `e.getUUID()` |
| `Date.now()` for real time | `level.getGameTime()` (not mapped); `server.getTickCount()` resets every boot |
| `server.persistentData` (saved with the world), `e.motionX` | |
| `e.getX()`, `e.isAlive()`, `e.isLiving()`, `e.isPlayer()`, `e.isSpectator()`, `e.getEncodeId()` | |
| `e.addTag()`, `e.removeTag()`, `e.getTags()`, `e.discard()`, `e.setMotionX()` | |
| `e.level.getDimension()`, `level.getEntitiesWithin(AABB.of(...))`, `level.getEntity(UUID)` | |
| `server.getTickCount()`, `server.getPlayerList()`, `server.getAllLevels()`, `server.runCommandSilent()` | |
| `e.persistentData` (copied to the new player on respawn) | |

When unsure of a name, check the jar with `javap` or ProbeJS typings in `run/kubejs/probe/generated`.

## Traps

| Trap | Rule |
|---|---|
| Brigadier "An unexpected error occurred" | The real error is in `logs/kubejs/server.log`; every `/domain` command is wrapped in `safe` |
| `Math.PI`, `Math.E` and the other Math constants | Undefined in Rhino, so maths silently becomes NaN and commands fail; use `Math.acos(-1)`. `validate` rejects them, `ctx.fmt` throws on NaN |
| Anything stored across restarts | Never `server.getTickCount()` (it starts at 0 each boot); use `Date.now()` |
| Coordinates in a command | Through `ctx.fmt`; a raw number near zero prints as `5e-17`, which commands reject |
| A hook that throws | `callAll` logs the component and hook once and carries on, so cleanup still runs |
| `const` in a `for` body | Rhino "redeclaration of var"; use a function per iteration (Critical Rule 4) |
| Top-level names across files | Wrap each file in an IIFE (Critical Rule 5) |
| `server.runCommandSilent` | Runs as the server in the overworld at spawn; add `execute in`/`as` |
| `/reload` | Re-runs every script; `global` survives, so state there must be plain data |
| Restart | `global` is gone; open domains end, `PlayerEvents.loggedIn` cleans player tags |
