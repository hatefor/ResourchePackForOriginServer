scoreboard players add @s kk_life 1
particle minecraft:electric_spark ~ ~ ~ 0.25 0.25 0.25 0.05 8
particle minecraft:end_rod ~ ~ ~ 0.1 0.1 0.1 0.01 2
execute if score @s kk_life matches 20.. if score @s kk_life matches ..400 if block ^ ^ ^0.4 minecraft:air run tp @s ^ ^ ^0.1
execute if score @s kk_life matches 400.. run kill @s
execute unless block ^ ^ ^0.4 minecraft:air run kill @s
execute if score @s kk_life matches 20.. run playsound minecraft:block.beacon.ambient neutral @a ~ ~ ~ 0.4 2
execute if score @s kk_life matches 20.. as @e[distance=..1.5,type=!player,type=!marker,type=!item,type=!experience_orb] run damage @s 1 minecraft:lightning_bolt
