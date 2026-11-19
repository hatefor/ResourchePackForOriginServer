xp add @s -40 levels
clear @s minecraft:nether_star 1
tag @s remove qs_quick
tag @s remove qs_ready
scoreboard players set @s qs_kills 0
title @s times 10 90 30
title @s subtitle {"text":"You have shed your mortal form","color":"yellow","italic":true}
title @s title {"text":"BEING OF LIGHT","color":"gold","bold":true}
tellraw @a [{"selector": "@s", "color": "yellow"}, {"text": " has ascended into a ", "color": "gold"}, {"text": "Being of Light", "color": "white", "bold": true}, {"text": "!", "color": "gold"}]
particle minecraft:flash ~ ~1 ~ 0 0 0 0 1 force
particle minecraft:end_rod ~ ~1 ~ 0.6 1 0.6 0.5 500 force
particle minecraft:totem_of_undying ~ ~1 ~ 0.5 1 0.5 0.6 150 force
particle minecraft:explosion_emitter ~ ~1 ~ 0 0 0 0 3 force
playsound minecraft:entity.lightning_bolt.thunder player @a ~ ~ ~ 4 1
playsound minecraft:ui.toast.challenge_complete player @a ~ ~ ~ 2 0.8
playsound minecraft:block.beacon.power_select player @a ~ ~ ~ 2 1.3
