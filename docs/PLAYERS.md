# Player guide

## Install (once)

You need the same Minecraft as the server: **1.20.1 with Forge**, plus the server's mods. If the server gives
you a modpack, install that first. Then add one mod:

| Mod | Download | Put it in |
|---|---|---|
| Photon 1.1.17 | [photon-forge-1.20.1-1.1.17.jar](https://cdn.modrinth.com/data/gzevkJbM/versions/a7chTVuf/photon-forge-1.20.1-1.1.17.jar) ([Modrinth page](https://modrinth.com/mod/photon-editor)) | your game's `mods` folder |

If you are not using a modpack, you also need these, the same versions as the server:

| Mod | Download |
|---|---|
| Origins Forge 1.10.0.9 | [origins-forge-1.20.1-1.10.0.9-all.jar](https://cdn.modrinth.com/data/jl3m2lR9/versions/vynFXywM/origins-forge-1.20.1-1.10.0.9-all.jar) |
| Caelus 3.2.0 (needed by Origins) | [caelus-forge-3.2.0+1.20.1.jar](https://cdn.modrinth.com/data/40FYwb4z/versions/mRry0DgY/caelus-forge-3.2.0%2B1.20.1.jar) |

You do **not** need KubeJS, Rhino or Architectury; those run on the server only.

Where the `mods` folder is: in the CurseForge app, right-click the profile and choose **Open Folder**; in the
vanilla launcher it is `%appdata%\.minecraft\mods`.

## Join

1. Join the server as usual.
2. You are asked to download the server's resource pack. Choose **Yes**: it holds the domain effects. It is
   a few KB and updates itself; you never install it by hand.

## Use your domain

1. An admin gives you a domain name (for example `Infinite Garden`).
2. Type it in chat as one message: `Domain expansion Infinite Garden`.
3. A dome opens around you. Everyone inside is caught with you, nobody outside can enter, and it closes after
   a timer. Your domain then needs to cool down before you can open it again.

If you picked the **Domain Caster** origin, your primary ability key opens your domain too.

`/domain name` shows the name of your domain.

## Problems

| What you see | Fix |
|---|---|
| Disconnected while joining with a message about missing or mismatched mods | You are missing Photon, or a mod's version differs from the server's. Use exactly the versions above |
| You are kicked right after joining | You declined the resource pack. In **Multiplayer**, select the server, **Edit**, set **Server Resource Packs** to **Enabled**, then join again |
| The dome appears but no particles or effects | Same as above: the resource pack is off. Also check Photon is in your `mods` folder |
| "You have no domain yet" | Ask an admin to give you one |
| "That is not the name of your domain" | Type your own domain's name exactly; `/domain name` shows it |
| "Your domain is ready again in N seconds" | Wait for the cooldown |
