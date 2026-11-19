scoreboard players remove @s tb_alive 1
execute if score @s tb_alive matches ..0 run function thieving_bird:unregister
