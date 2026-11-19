---
paths:
  - "resourcepack/**"
  - "tools/photon/**"
  - "origins/*/effects.py"
  - "kubejs/server_scripts/ordertest/components/photon_fx.js"
  - "kubejs/server_scripts/ordertest/components/display_shell.js"
  - "kubejs/server_scripts/ordertest/components/meridian_particles.js"
  - "tools/dev_client/**"
---

# VFX rules

The long form is `CLAUDE.md` section 5. Read it before making or changing an effect.

| Rule | Why |
|---|---|
| The display shell carries the domain's look; Photon is the moment on top | A player without the pack, or an effect that failed to load, still sees the dome |
| At most 8,000 particles summed over one Photon effect | Photon has no LOD or culling; every viewer pays the whole count |
| A one-shot is looping off, burst-only, and ends empty inside its duration | A live particle at the end freezes on screen until F3+T |
| A looping effect is only `loop` or `memberLoop` in `photon_fx` | Those are the only slots something removes |
| Never play a Photon effect from `tick` or `memberTick` | Every trigger starts a new effect; they stack |
| Lifetimes are whole ticks of at least 4 | Below 1 floors to 0, which never expires |
| Per-domain colour goes on the shell or particles | A `.fx` bakes its colour |
| Particles use `normal`, never `force` | `force` ignores the player's setting and sends to 512 blocks |
| Every coordinate goes through `ctx.fmt`; never `Math.PI` | NaN fails the command silently; Rhino has no Math constants |
| Done means a scripted-run screenshot was read, at noon, inside and outside | Server tests cannot see anything |
| Effects are code in `origins/<name>/effects.py` (or shared ones in `tools/photon/effects/`), built by `generate.py` | The `.fx` files are build output; edit the code, never the file |
| A builder setter only changes keys present in Photon's own templates | Unknown keys are ignored silently; dump a template first |

These limits were measured by VoidSpell on Photon for 26.x. The generator here is the 1.20.1 port, rebuilt on
templates this Photon serialized (CLAUDE.md section 5).
