scoreboard players set #c tb_tmp 0
execute as @a[tag=tb_user] run function thieving_bird:alive_tick
execute as @a[scores={tb_intent=1..}] run scoreboard players remove @s tb_intent 1
execute as @e[tag=tb_marked] at @s run function thieving_bird:mark_second
scoreboard players add #m tb_tmp 1
execute if score #m tb_tmp matches 60.. run function thieving_bird:rotate
execute as @a[scores={tb_fate=1..}] run function thieving_bird:fate_second
execute as @e[tag=tb_fate_tgt] at @s run particle minecraft:soul ~ ~1 ~ 0.3 0.5 0.3 0.02 5
