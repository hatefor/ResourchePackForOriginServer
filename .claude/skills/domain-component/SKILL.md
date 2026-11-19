---
name: domain-component
description: Add or change a piece of the Order test domain system - a JS component (a new behaviour or effect), a domain definition (a player's named domain), an mcfunction effect hook, or an Origins origin/power written in JS. Use when the user asks for a new domain effect, a new domain, a change to the wall/visuals/timer/catching, or a new origin.
---

# Add to the domain system

## 1. Pick the smallest thing that does the job

| Want | Do |
|---|---|
| Change a number or particle of an existing behaviour | `options` in the domain's definition, or the component's `defaults` |
| A behaviour that only some domains have | A new component, listed in those domains' `extraComponents` |
| A behaviour every domain has | A new component added to `OrderTest.defaults.components` in `core.js` |
| An effect a datapack author can write | An mcfunction in a `#ordertest:domain/*` tag, filtered by `ot_in_<slug>` |
| An Origins power while inside | `['origins_power', { power: 'ns:id', target: 'others' }]` |
| A new origin | `python tools/new_origin.py <name>`: everything goes in `origins/<name>/` (scripts, `data/`, `effects.py`, tests) |
| A power for an existing origin | `OrderTest.power` in its `origins/<name>/*.js`, or JSON in its `origins/<name>/data/` |

Read `.claude/rules/kubejs.md` (and `datapack.md` for hooks) first.

## 2. Build

- A component is one file `components/<id>.js`: `// priority: 500`, an IIFE, `global.OrderTest.component('<id>',
  { defaults: {...}, <hooks> })`. Copy the closest existing one (`potion_effect` for a per-member effect,
  `sphere_barrier` for per-tick world logic, `sounds` for open/close only).
- Every number a user might tune goes in `defaults`.
- A domain is a `global.OrderTest.domain('<Name>', {...})` call: in its origin's folder (`origins/<name>/domain.js`),
  or in `kubejs/server_scripts/ordertest/domains/` when no single origin owns it.
- Hooks never throw; guard anything that can be null (`ctx.ownerEntity()` is null when the owner is offline).

## 3. Verify

1. `python tools/validate.py`: zero errors (JS syntax and component ids are checked).
2. Add lines to `tests/domain.mctest` that open a domain with a zombie (`domain open @e[...] <Name>`) and
   check what the change leaves behind (a tag, an effect, a position).
3. `python tools/testserver.py test`: all checks pass, zero load errors. For live iteration keep the server
   up and use `sync` after each edit.
4. Anything visual or a chat path: a scripted dev run that types the cast and takes `!screenshot`s
   (`CLAUDE.md` section 5, testing level 4), then read every PNG. It quits by itself; never leave a dev game
   open. Say plainly what was checked on screen and what was not.
