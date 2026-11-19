execute unless score @s morgan_id matches 1.. run function morgan:assign_id
scoreboard players operation #me morgan_id = @s morgan_id
execute as @e[type=marker,tag=morgan_ret] if score @s morgan_id = #me morgan_id at @s run forceload remove ~ ~
execute as @e[type=marker,tag=morgan_ret] if score @s morgan_id = #me morgan_id run kill @s
execute at @s run forceload add ~ ~
summon marker ~ ~ ~ {Tags:["morgan_ret","morgan_new"]}
scoreboard players operation @e[type=marker,tag=morgan_new,limit=1] morgan_id = #me morgan_id
tag @e[type=marker,tag=morgan_new] remove morgan_new
execute at @s run particle minecraft:dust 1 0.5 0 1.2 ~ ~1 ~ 0.4 0.8 0.4 0.1 80 force
execute at @s run particle minecraft:flame ~ ~1 ~ 0.4 0.8 0.4 0.05 25 force
execute at @s run playsound minecraft:entity.enderman.teleport master @a ~ ~ ~ 1 0.7
execute in morgan:larrys_realm run tp @s 0 17 0
execute at @s run particle minecraft:dust 1 0.5 0 1.2 ~ ~1 ~ 0.4 0.8 0.4 0.1 80 force
execute at @s run particle minecraft:flame ~ ~1 ~ 0.4 0.8 0.4 0.05 25 force
execute at @s run playsound minecraft:entity.enderman.teleport master @a ~ ~ ~ 1 0.7
