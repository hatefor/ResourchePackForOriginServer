execute store result score #f tb_tmp run data get entity @s foodLevel
execute store result score #s tb_tmp run data get entity @s foodSaturationLevel
scoreboard players operation #f tb_tmp /= #2 tb_tmp
scoreboard players operation #s tb_tmp /= #2 tb_tmp
scoreboard players operation #p tb_tmp = #f tb_tmp
scoreboard players operation #p tb_tmp += #s tb_tmp
execute if score #p tb_tmp matches 21.. run scoreboard players set #p tb_tmp 20
execute if score #p tb_tmp matches 1.. run function thieving_bird:hunger_go
execute if score #p tb_tmp matches ..0 run title @a[tag=tb_self] actionbar {"text":"They have no hunger left to steal","color":"gray"}
