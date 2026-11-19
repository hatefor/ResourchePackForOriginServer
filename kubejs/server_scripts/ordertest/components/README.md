# Components

Every behaviour a domain can have, one component per file, grouped by what it is for. A domain lists components by
id (`'sphere_barrier'`), never by folder, so moving a file between folders changes nothing. Each file starts with
`// priority: 500` so it loads after `core.js` and before domains and origins.

| Folder | Use case | Components |
|---|---|---|
| `catching/` | Who is caught when the domain opens | `catch_radius` |
| `barrier/` | Keeping members in and everyone else out | `sphere_barrier` |
| `visuals/` | What the domain looks like | `display_shell` (the dome), `meridian_particles` (accent), `photon_fx` (Photon effects) |
| `feedback/` | Telling players what is happening | `announce_title`, `countdown_actionbar`, `sounds` |
| `effects/` | What it does to the people inside | `potion_effect`, `origins_power` |
| `bridges/` | Links to other systems | `mcfunction_hooks` (the `#ordertest:domain/*` datapack tags) |

A new component goes in the folder of its use case; add a folder only for a use case none of these cover. A
component only one origin uses belongs in that origin's folder (`origins/<name>/`) instead.
