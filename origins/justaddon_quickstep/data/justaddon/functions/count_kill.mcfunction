scoreboard players add @s qs_kills 1
execute if score @s qs_kills matches 301.. run scoreboard players set @s qs_kills 300
title @s actionbar [{"text": "☀ Monsters slain: ", "color": "gold"}, {"score": {"name": "@s", "objective": "qs_kills"}, "color": "yellow"}, {"text": "/300", "color": "gray"}]
execute if score @s qs_kills matches 300 run tellraw @s [{"text": "☀ ", "color": "gold"}, {"text": "Trial complete: ", "color": "yellow"}, {"text": "300 monsters slain.", "color": "white"}]
execute if score @s qs_kills matches 300 run playsound minecraft:ui.toast.challenge_complete player @s ~ ~ ~ 1 1.2
