execute unless score @s tb_id matches 1.. run function thieving_bird:register
tag @s add tb_self
scoreboard players operation #me tb_id = @s tb_id

scoreboard players set #mode tb_tmp 3
scoreboard players set #hit tb_tmp 0
scoreboard players set #steps tb_tmp 0
execute anchored eyes positioned ^ ^ ^ run function thieving_bird:ray_step
execute if score #hit tb_tmp matches 0 run title @s actionbar {"text":"Your talons find no one","color":"gray"}
tag @s remove tb_self
