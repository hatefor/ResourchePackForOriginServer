scoreboard players add #steps tb_tmp 1
scoreboard players set #go tb_tmp 0
execute if score #steps tb_tmp matches ..96 positioned ^ ^ ^0.5 if block ~ ~ ~ #thieving_bird:ray_passable if block ~ ~-1 ~ #thieving_bird:ray_passable run scoreboard players set #go tb_tmp 1
execute if score #go tb_tmp matches 1 positioned ^ ^ ^0.5 run function thieving_bird:blink_step
execute if score #go tb_tmp matches 0 if score #done tb_tmp matches 0 run function thieving_bird:blink_end
