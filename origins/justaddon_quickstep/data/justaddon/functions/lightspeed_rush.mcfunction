effect give @s minecraft:speed 8 5 true
effect give @s minecraft:resistance 8 4 true
effect give @s minecraft:strength 8 4 true
effect give @s minecraft:regeneration 8 3 true
effect give @s minecraft:jump_boost 8 3 true
effect give @s minecraft:absorption 8 4 true
execute at @s run particle minecraft:end_rod ~ ~1 ~ 0.4 0.8 0.4 0.3 120 force
execute at @s run playsound minecraft:entity.player.levelup player @a ~ ~ ~ 1.5 0.6
title @s actionbar {"text":"☀ LIGHTSPEED RUSH ☀","color":"yellow","bold":true}
