scoreboard players remove @s tb_menu 1
scoreboard players enable @s tb_pick
execute if score @s tb_menu matches ..0 run function thieving_bird:menu_close
