# Domain Caster

An origin whose primary ability key opens its owner's domain (`/domain cast`). Its domain, **Photon Example**,
plays four Photon effects: a violet shell thrown out to the wall on open, a curtain rising around the inside of
the wall while open, a gold implosion on close, and a ring at the feet of everyone caught.

| File | What |
|---|---|
| `origin.js` | The origin and its `ordertest:cast_domain` power, written in JS |
| `domain.js` | The Photon Example domain |
| `effects.py` | The four effects, released as `ordertest:domain_caster/<name>` |
| `tests.mctest` | Headless tests: the domain opens and closes, the power loads |

Try it: `/domain register <you> Photon Example`, then type `Domain expansion Photon Example`.
