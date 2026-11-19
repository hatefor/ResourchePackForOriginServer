scoreboard players operation #me tb_id = @s tb_id
execute as @e[tag=tb_fate_tgt] if score @s tb_link = #me tb_id run function thieving_bird:fate_free
tag @s remove tb_fate_bird
scoreboard players set @s tb_fate 0
