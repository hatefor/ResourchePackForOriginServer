execute unless score @s tb_id matches 1.. run function thieving_bird:register
function thieving_bird:fate_clear
tag @s add tb_self
scoreboard players operation #me tb_id = @s tb_id

scoreboard players set #mode tb_tmp 4
scoreboard players set #hit tb_tmp 0
scoreboard players set #steps tb_tmp 0
execute anchored eyes positioned ^ ^ ^ run function thieving_bird:ray_step
execute if score #hit tb_tmp matches 0 run title @s actionbar {"text":"Your talons find no fate to steal","color":"gray"}
tag @s remove tb_self
