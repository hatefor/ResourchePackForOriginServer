scoreboard players set #hit tb_tmp 1
execute if score #mode tb_tmp matches 1 run function thieving_bird:open_menu
execute if score #mode tb_tmp matches 2 run function thieving_bird:hunger_hit
execute if score #mode tb_tmp matches 3 run function thieving_bird:intent_hit
execute if score #mode tb_tmp matches 4 run function thieving_bird:fate_hit
