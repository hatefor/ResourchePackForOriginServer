scoreboard players set #done vs_tmp 1
particle minecraft:portal ~ ~ ~ 0.4 0.8 0.4 0.1 50
tp @s ~ ~-1.62 ~
effect give @s minecraft:slow_falling 4 0 true
particle minecraft:reverse_portal ~ ~1 ~ 0.4 0.8 0.4 0.1 50
playsound minecraft:entity.enderman.teleport player @a ~ ~ ~ 1 1.3
scoreboard players set @s vs_ok 2
