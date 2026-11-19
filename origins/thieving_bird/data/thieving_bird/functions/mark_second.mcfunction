scoreboard players remove @s tb_mark 1
particle minecraft:angry_villager ~ ~2.2 ~ 0.2 0.1 0.2 0 2
execute if score @s tb_mark matches ..0 run tag @s remove tb_marked
