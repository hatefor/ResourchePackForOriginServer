tag @s add morgan_src
execute as @e[type=minecraft:enderman,distance=..16] run data modify entity @s AngryAt set from entity @a[tag=morgan_src,limit=1] UUID
execute as @e[type=minecraft:enderman,distance=..16] run data modify entity @s AngerTime set value 400
tag @s remove morgan_src
