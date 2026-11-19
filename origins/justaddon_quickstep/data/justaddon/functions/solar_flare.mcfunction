tag @s add qs_self
execute at @s run effect give @e[distance=..16,tag=!qs_self,type=!#justaddon:undead] minecraft:instant_damage 1 3 true
execute at @s run effect give @e[distance=..16,tag=!qs_self,type=#justaddon:undead] minecraft:instant_health 1 3 true
execute at @s run effect give @e[distance=..16,tag=!qs_self] minecraft:blindness 8 0 true
execute at @s run effect give @e[distance=..16,tag=!qs_self] minecraft:levitation 2 12 true
execute at @s as @e[distance=..16,tag=!qs_self,type=!minecraft:player,type=!minecraft:item,type=!minecraft:experience_orb] run data merge entity @s {Fire:200s}
execute at @s run particle minecraft:flash ~ ~1 ~ 0 0 0 0 1 force
execute at @s run particle minecraft:end_rod ~ ~1 ~ 4 2 4 0.6 400 force
execute at @s run particle minecraft:explosion_emitter ~ ~1 ~ 3 1 3 0 8 force
execute at @s run playsound minecraft:entity.lightning_bolt.thunder player @a ~ ~ ~ 3 1.2
execute at @s run playsound minecraft:block.beacon.activate player @a ~ ~ ~ 2 1.5
title @s actionbar {"text":"☀ SOLAR FLARE ☀","color":"yellow","bold":true}
tag @s remove qs_self
