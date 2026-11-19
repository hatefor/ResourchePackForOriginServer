tag @s remove larry_leaving
summon marker ~ ~ ~ {Tags:["larry_tmp"]}
execute store result entity @e[type=marker,tag=larry_tmp,limit=1] Pos[0] double 0.01 run scoreboard players get @s larry_x
execute store result entity @e[type=marker,tag=larry_tmp,limit=1] Pos[1] double 0.01 run scoreboard players get @s larry_y
execute store result entity @e[type=marker,tag=larry_tmp,limit=1] Pos[2] double 0.01 run scoreboard players get @s larry_z
tp @s @e[type=marker,tag=larry_tmp,limit=1]
kill @e[type=marker,tag=larry_tmp]
execute at @s run particle minecraft:reverse_portal ~ ~1 ~ 0.4 0.8 0.4 0.15 60
execute at @s run playsound minecraft:entity.enderman.teleport player @a ~ ~ ~ 1 1.2
execute if entity @s[tag=larry_src] run function larry:carry_back_go
