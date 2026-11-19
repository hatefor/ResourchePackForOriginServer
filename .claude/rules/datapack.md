---
paths:
  - "data/**"
  - "tests/**"
  - "origins/*/data/**"
  - "origins/*/*.mctest"
---

# Datapack hooks (1.20.1)

The engine is in KubeJS; the datapack only plugs mcfunction effects in through the `mcfunction_hooks`
component. Add a function to a tag in `data/ordertest/tags/functions/domain/`:

| Tag | Runs | As / at |
|---|---|---|
| `#ordertest:domain/open` | once when a domain opens | the owner (or the server), at the centre |
| `#ordertest:domain/enter` | when an entity is caught | the entity, at the entity |
| `#ordertest:domain/tick` | every tick | each member, at the member |
| `#ordertest:domain/exit` | member leaves or the domain closes | the entity, at the entity |
| `#ordertest:domain/close` | once before members are released | the owner (or the server), at the centre |

## Context tags

| Tag | On |
|---|---|
| `ot_inside` | every entity inside any domain |
| `ot_in_<slug>` | members of the domain whose name slugs to `<slug>` ("Infinite Garden" is `ot_in_infinite_garden`) |
| `ot_domain_owner` | a player or entity whose domain is open |

Filter by name with `@s[tag=ot_in_<slug>]`, as `functions/examples/example_domain_tick.mcfunction` does.

## Imported origins (origins/<name>/data/)

| Trap | Rule |
|---|---|
| `origins:status_effect` as a power type | Does not exist in Apoli 2.9 (only as a condition). Use `action_over_time` + `apply_effect` |
| `apoli:light_level` in an entity condition | Block condition only; entity is `origins:brightness` (light 10 in the overworld = 0.333) |
| `origins:multiple` | Defines sub-powers `<id>_<key>`; other powers reference those ids (`validate` knows) |
| `*:*_x` in a resource reference | Origins' wildcard for this power's own id |
| A `cooldown` power used as a resource | Valid: Apoli resource actions and conditions accept it |
| Exponent numbers in commands (`~1.67772e+07`) | Rejected by Minecraft; `validate` errors on them |
| Two origins writing one file | Only tags and origin layers merge; anything else is an error by design |

## Traps

| Trap | Rule |
|---|---|
| A tick hook runs for every member of every domain | Always filter by `ot_in_<slug>` |
| Effects given every tick | Give a 2 s effect and let it lapse on exit, or clear it in an exit hook |
| Effect NBT in tests | 1.20.1 is `ActiveEffects:[{Id:<int>}]` |
| Newer docs | `function/`, `tags/function/` are 1.21; this pack uses `functions/`, `tags/functions/` |
