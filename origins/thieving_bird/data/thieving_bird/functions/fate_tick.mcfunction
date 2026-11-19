scoreboard players operation #me tb_id = @s tb_id
execute if data entity @s {Health:0.0f} run function thieving_bird:fate_bird_died
execute as @e[tag=tb_fate_tgt] if score @s tb_link = #me tb_id if data entity @s {Health:0.0f} run function thieving_bird:fate_tgt_died
