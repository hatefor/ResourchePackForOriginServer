scoreboard players add #steps vs_tmp 1
scoreboard players set #go vs_tmp 0
execute if score #steps vs_tmp matches ..1000 positioned ^ ^ ^0.5 if block ~ ~0.2 ~ #vsealkwt:body_passable if block ~ ~ ~ #vsealkwt:body_passable if block ~ ~-0.8 ~ #vsealkwt:body_passable if block ~ ~-1.6 ~ #vsealkwt:body_passable run scoreboard players set #go vs_tmp 1
execute if score #go vs_tmp matches 1 positioned ^ ^ ^0.5 run function vsealkwt:blink_step
execute if score #go vs_tmp matches 0 if score #done vs_tmp matches 0 if score #steps vs_tmp matches 3..1000 run function vsealkwt:blink_end
