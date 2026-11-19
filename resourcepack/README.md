# Order test resource pack

Client assets the server sends to every player on join. Photon effects go in `assets/ordertest/fx/<name>.fx`
and are referred to as `ordertest:<name>` (in `photon_fx` options and in `/photon fx`).

Make an effect in the dev client with `/photon_editor`, then `Export > FX` into
`ldlib/assets/ordertest/fx/`. That folder is linked to this one, so the file lands here directly.
Run `/photon_client clear_client_fx_cache` and press F3+T to see a changed effect without restarting.
