# Order test: domain expansion for Origins servers

A domain expansion system for a Minecraft **1.20.1 Forge** server with Origins. A player types
`Domain expansion <their domain's name>` in chat and a dome opens around them: everyone inside is caught and
can't leave, nobody outside can get in, effects play inside it, and after a timer it closes.

- **Players** install one extra mod (Photon) once. Every new effect after that arrives automatically in the
  server's resource pack when they join.
- **Server admins** add a few mods and files, and point `server.properties` at this repository's latest release.
- **Developers** write domains and their parts in JavaScript (KubeJS) and effects as Python that does the maths.
  Every push is tested on a real headless server, and a passing push publishes the new resource pack here.

## Guides

| You are | Read |
|---|---|
| A player joining the server | [docs/PLAYERS.md](docs/PLAYERS.md) |
| Setting up or running the server | [docs/SERVER.md](docs/SERVER.md) |
| Making domains, effects or changes | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) |

## The newest resource pack

Always the latest tested build:

```
https://github.com/hatefor/ResourchePackForOriginServer/releases/latest/download/ordertest-resources.zip
```

Every release is listed under [Releases](https://github.com/hatefor/ResourchePackForOriginServer/releases),
each with its SHA-1 and the matching datapack and scripts.

## What it runs on

Minecraft 1.20.1, Forge 47.4.28, Origins Forge 1.10.0.9, KubeJS 2001.6.5 (server only) and Photon 1.1.17
(server and players).
