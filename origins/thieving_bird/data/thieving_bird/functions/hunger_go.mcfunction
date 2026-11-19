effect give @s minecraft:hunger 10 1 true
execute if score #p tb_tmp matches 1 run function thieving_bird:drain_1
execute if score #p tb_tmp matches 2 run function thieving_bird:drain_2
execute if score #p tb_tmp matches 3 run function thieving_bird:drain_3
execute if score #p tb_tmp matches 4 run function thieving_bird:drain_4
execute if score #p tb_tmp matches 5 run function thieving_bird:drain_5
execute if score #p tb_tmp matches 6 run function thieving_bird:drain_6
execute if score #p tb_tmp matches 7 run function thieving_bird:drain_7
execute if score #p tb_tmp matches 8 run function thieving_bird:drain_8
execute if score #p tb_tmp matches 9 run function thieving_bird:drain_9
execute if score #p tb_tmp matches 10 run function thieving_bird:drain_10
execute if score #p tb_tmp matches 11 run function thieving_bird:drain_11
execute if score #p tb_tmp matches 12 run function thieving_bird:drain_12
execute if score #p tb_tmp matches 13 run function thieving_bird:drain_13
execute if score #p tb_tmp matches 14 run function thieving_bird:drain_14
execute if score #p tb_tmp matches 15 run function thieving_bird:drain_15
execute if score #p tb_tmp matches 16 run function thieving_bird:drain_16
execute if score #p tb_tmp matches 17 run function thieving_bird:drain_17
execute if score #p tb_tmp matches 18 run function thieving_bird:drain_18
execute if score #p tb_tmp matches 19 run function thieving_bird:drain_19
execute if score #p tb_tmp matches 20 run function thieving_bird:drain_20
scoreboard players operation @a[tag=tb_self] tb_owed += #p tb_tmp
title @s actionbar {"text":"Your hunger is being stolen!","color":"red"}
title @a[tag=tb_self] actionbar [{"text":"Hunger stolen from ","color":"gold"},{"selector":"@s","color":"yellow"}]
particle minecraft:angry_villager ~ ~2 ~ 0.3 0.2 0.3 0 5
playsound minecraft:entity.generic.eat player @a ~ ~ ~ 1 0.7
