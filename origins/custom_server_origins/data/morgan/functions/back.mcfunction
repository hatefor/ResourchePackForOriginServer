execute unless score @s morgan_id matches 1.. run function morgan:assign_id
scoreboard players operation #me morgan_id = @s morgan_id
scoreboard players set #moved morgan_rng 0
execute as @e[type=marker,tag=morgan_ret] if score @s morgan_id = #me morgan_id run scoreboard players set #moved morgan_rng 1
execute at @s run particle minecraft:dust 1 0.5 0 1.2 ~ ~1 ~ 0.4 0.8 0.4 0.1 80 force
execute at @s run particle minecraft:flame ~ ~1 ~ 0.4 0.8 0.4 0.05 25 force
execute at @s run playsound minecraft:entity.enderman.teleport master @a ~ ~ ~ 1 0.7
tag @s add morgan_tp
execute as @e[type=marker,tag=morgan_ret] if score @s morgan_id = #me morgan_id at @s run tp @a[tag=morgan_tp,limit=1] ~ ~ ~
execute at @s run particle minecraft:dust 1 0.5 0 1.2 ~ ~1 ~ 0.4 0.8 0.4 0.1 80 force
execute at @s run particle minecraft:flame ~ ~1 ~ 0.4 0.8 0.4 0.05 25 force
execute at @s run playsound minecraft:entity.enderman.teleport master @a ~ ~ ~ 1 0.7
execute as @e[type=marker,tag=morgan_ret] if score @s morgan_id = #me morgan_id at @s run forceload remove ~ ~
execute as @e[type=marker,tag=morgan_ret] if score @s morgan_id = #me morgan_id run kill @s
execute if score #moved morgan_rng matches 0 in minecraft:overworld run spreadplayers 0 0 0 50 false @s
tag @s remove morgan_tp
