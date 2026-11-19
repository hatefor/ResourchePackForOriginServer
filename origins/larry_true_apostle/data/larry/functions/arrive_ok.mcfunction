tag @s add larry_arriving
effect give @s minecraft:resistance 8 4 true
effect give @s minecraft:slow_falling 8 0 true
execute at @s run particle minecraft:reverse_portal ~ ~1 ~ 0.4 0.8 0.4 0.15 80
execute at @s run particle minecraft:flame ~ ~0.2 ~ 0.6 0.1 0.6 0.04 40
execute at @s run playsound minecraft:entity.enderman.teleport player @a ~ ~ ~ 1 0.5
title @s times 20 80 30
title @s subtitle {"text":"Larry is watching.","color":"dark_red","italic":true}
title @s title {"text":"The Gilded Expanse","color":"gold","bold":true}
tellraw @s [{"text":"[Leave the realm]","color":"gold","bold":true,"clickEvent":{"action":"run_command","value":"/trigger larry_leave"},"hoverEvent":{"action":"show_text","contents":"Return to where you came from"}},{"text":"  or type /trigger larry_leave at any time","color":"gray"}]
schedule function larry:platforms 10t append
