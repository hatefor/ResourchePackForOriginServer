# Larry's True Apostle (Origins datapack, Minecraft 1.20.1)

Install: put this zip in `<world>/datapacks/` (or the server's world datapacks folder), then `/reload`.
Requires the Origins mod (Fabric/Quilt 1.20.1). Pick "Larry's True Apostle" on the origin screen.

Keys
- Primary: Withering Gaze. Sneak + Primary: Soul Snare (drag the player you stare at into the realm).
- Secondary: Private Realm (toggle in/out). Sneak + Secondary outside the realm: Take Along.
  Sneak + Secondary inside the realm: Release Guests.

The realm (`larry:realm`) is floating blackstone islands with gilded blackstone veins over a lava sea.
No natural mob spawning: the biome has empty spawner lists and mob generation is disabled.
Leaving: anyone in the realm (guests included) can leave at any time with `/trigger larry_leave`
(also a clickable button shown on arrival). No permissions or cooldown needed. Your position is simply remembered as numbers (no anchor entities and no
chunk force-loading), so leaving can never get stuck.

IMPORTANT: datapack dimensions only register when the world loads. After adding or updating this pack,
save and quit and reopen the world (or restart the server). /reload alone will NOT create the dimension.
Debug: `/function larry:diagnose`, then `/execute in larry:realm run tp @s 0 100 0` to visit it.
