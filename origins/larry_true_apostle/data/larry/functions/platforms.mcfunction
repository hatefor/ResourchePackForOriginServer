execute as @a[tag=larry_arriving] at @s if block ~ ~-1 ~ #larry:void_like run fill ~-2 ~-1 ~-2 ~2 ~-1 ~2 minecraft:blackstone replace #larry:void_like
execute as @a[tag=larry_arriving] at @s if block ~ ~-1 ~ minecraft:blackstone run setblock ~ ~-1 ~ minecraft:gilded_blackstone
tag @a remove larry_arriving
