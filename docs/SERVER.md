# Server guide

The server runs no Python and builds nothing. It needs some mod jars, the KubeJS scripts, the datapack and one
setting that points at this repository's resource pack. Everything below is files you upload.

## 1. Mods

Put these in the server's `mods/` folder.

| Mod | Download | Notes |
|---|---|---|
| Photon 1.1.17 | [photon-forge-1.20.1-1.1.17.jar](https://cdn.modrinth.com/data/gzevkJbM/versions/a7chTVuf/photon-forge-1.20.1-1.1.17.jar) | Players need the same jar. It bundles LDLib, so there is nothing else to add for it |
| KubeJS 2001.6.5 | [kubejs-forge-2001.6.5-build.26.jar](https://cdn.modrinth.com/data/umyGl7zF/versions/hVR2xUSr/kubejs-forge-2001.6.5-build.26.jar) | Server only |
| Rhino 2001.2.3 | [rhino-forge-2001.2.3-build.10.jar](https://cdn.modrinth.com/data/sk9knFPE/versions/uNALdylI/rhino-forge-2001.2.3-build.10.jar) | Needed by KubeJS. Skip if the server already has Rhino |
| Architectury 9.2.14 | [architectury-9.2.14-forge.jar](https://cdn.modrinth.com/data/lhGA9TYQ/versions/1MKTLiiG/architectury-9.2.14-forge.jar) | Needed by KubeJS. Skip if the server already has it |
| Origins Forge 1.10.0.9 | [origins-forge-1.20.1-1.10.0.9-all.jar](https://cdn.modrinth.com/data/jl3m2lR9/versions/vynFXywM/origins-forge-1.20.1-1.10.0.9-all.jar) | Skip if already installed |
| Caelus 3.2.0 | [caelus-forge-3.2.0+1.20.1.jar](https://cdn.modrinth.com/data/40FYwb4z/versions/mRry0DgY/caelus-forge-3.2.0%2B1.20.1.jar) | Needed by Origins. Skip if already installed |

Never put two versions of one mod in `mods/`: the server will not start. Do not install ProbeJS on the server;
it is a script-writing tool for developers.

## 2. Scripts and datapack

From the newest [release](https://github.com/hatefor/ResourchePackForOriginServer/releases/latest):

| File | Where it goes |
|---|---|
| `ordertest-kubejs.zip` | Unzip into the server folder (the one with `mods/`). It creates `kubejs/server_scripts/ordertest/` (the engine) and `kubejs/server_scripts/origins/` (every origin) |
| `ordertest.zip` | Into `<world folder>/datapacks/`. The world folder is named by `level-name` in `server.properties`, usually `world` |

## 3. Resource pack

In `server.properties`:

```
resource-pack=https://github.com/hatefor/ResourchePackForOriginServer/releases/latest/download/ordertest-resources.zip
resource-pack-sha1=
require-resource-pack=true
```

This always serves the newest tested pack, so you never edit it again. Players download the pack (a few KB)
each time they join. To lock the server to one exact pack instead, use the pinned link and SHA-1 from that
release's notes; then you update both lines for each new release.

## 4. Start and check

1. Restart the server. The console shows `Photon is initializing on platform: Forge` and
   `Loaded 15/15 KubeJS server scripts ... with 0 errors`. An error about
   `FXEditor for invalid dist DEDICATED_SERVER` right after Photon starts is normal: the editor only exists on
   players' games.
2. Join, accept the resource pack, then run `/domain register <your name> Photon Example` and type
   `Domain expansion Photon Example`. A dome builds, a violet burst flies out, a curtain rises around the
   wall, and a gold implosion plays when it closes.

## Automatic upload (WiseHosting)

After every push to `main` that passes all tests, GitHub uploads the scripts and datapack to the server over SFTP
(`tools/deploy_sftp.py`). It only writes and deletes inside `kubejs/server_scripts/ordertest/`,
`kubejs/server_scripts/origins/` and `<world>/datapacks/ordertest.zip`; mods, worlds and everything else are never
touched. Only changed files are uploaded. The changes take effect on `/reload` (or a restart).

Set it up once, in the GitHub repository under **Settings > Secrets and variables > Actions**:

| Name | Kind | Value |
|---|---|---|
| `WISEHOSTING_SFTP_HOST` | Secret | The address on the panel's **Files > SFTP** page, without `sftp://` or a port |
| `WISEHOSTING_SFTP_PORT` | Secret | The port on that page (2022 if none is shown) |
| `WISEHOSTING_SFTP_USER` | Secret | The username on that page |
| `WISEHOSTING_SFTP_PASSWORD` | Secret | Your panel password (the SFTP password is the panel password) |
| `WISEHOSTING_SFTP_HOST_KEY` | Secret | Recommended: the output of `ssh-keyscan -p <port> <host>` (one line). Without it the server's identity is not checked |
| `SERVER_WORLD` | Variable | The world folder (`level-name` in `server.properties`), only if it is not `world` |

Check it from your PC before relying on it (set the same values as environment variables first):
`python tools/deploy_sftp.py --dry-run` connects and lists what would change without changing anything.

## Admin commands

Need permission level 2 (operators).

| Command | Does |
|---|---|
| `/domain register <player> <name>` | Gives a player their domain. Only they can cast it |
| `/domain clear <player>` | Removes a player's domain and resets their cooldown |
| `/domain open <entity> [name]` | Opens a domain for any player or mob, for events and testing |
| `/domain close <owner>` / `/domain closeall` | Closes one or every open domain |
| `/domain time <owner> <seconds>` | Changes how long an open domain has left |
| `/domain list` | Open domains, where, how many inside, time left |
| `/domain components` | Every loaded component and defined domain |

Players have `/domain cast` (same as typing the phrase) and `/domain name`.

## Updating

| What changed | What to do |
|---|---|
| Effects | Nothing. With the `latest` link, players get the new pack on their next join |
| Scripts (`kubejs/`) | Replace both `kubejs/server_scripts/ordertest/` and `kubejs/server_scripts/origins/` with the newest release's `ordertest-kubejs.zip`, then run `/reload`. Update scripts and datapack together whenever a release adds or renames an origin or effect |
| Datapack | Replace `ordertest.zip` in `datapacks/` with the newest release's, then `/reload` |
| Mod versions | Only when the guides change them; players must update Photon to the same version |

## Problems

| Symptom | Cause |
|---|---|
| The server does not start after adding mods | Two copies of one mod (Rhino, Architectury, Origins). Keep one |
| `/domain` is an unknown command | KubeJS or the scripts are missing; check `logs/kubejs/server.log` |
| Players get no effects | They declined the pack or lack Photon; see the player guide |
| A command says "An unexpected error occurred" | The real error is in `logs/kubejs/server.log` |
