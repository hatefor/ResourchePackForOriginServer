execute as @a[scores={tb_pick=1..}] at @s run function thieving_bird:pick
execute as @a[scores={tb_menu=1..}] run function thieving_bird:menu_tick
scoreboard players add #c tb_tmp 1
execute if score #c tb_tmp matches 20.. run function thieving_bird:second
execute as @a[tag=tb_fate_bird] run function thieving_bird:fate_tick
