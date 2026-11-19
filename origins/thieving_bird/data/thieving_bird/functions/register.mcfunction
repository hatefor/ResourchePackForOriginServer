tag @s add tb_user
scoreboard players set @s tb_alive 4
execute unless score @s tb_id matches 1.. run function thieving_bird:assign_id
