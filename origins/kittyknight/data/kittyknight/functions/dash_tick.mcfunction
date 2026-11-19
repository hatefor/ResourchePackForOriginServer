scoreboard players remove @s kk_dash 1
tag @s add kk_self
particle minecraft:electric_spark ~ ~1 ~ 0.3 0.5 0.3 0.2 12
particle minecraft:end_rod ~ ~1 ~ 0.2 0.4 0.2 0.05 3
execute as @e[distance=..2.5,tag=!kk_self,type=!item,type=!marker,type=!experience_orb] at @s run function kittyknight:dash_hit
execute as @e[type=marker,tag=kk_orb,distance=..3.5] at @s run function kittyknight:orb_absorb
tag @s remove kk_self
