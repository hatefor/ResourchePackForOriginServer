tag @s remove tb_fate_tgt
scoreboard players reset @s tb_link
execute as @a[tag=tb_fate_bird] if score @s tb_id = #me tb_id run function thieving_bird:fate_clear
