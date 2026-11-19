tag @s add tb_self
execute as @e[type=minecraft:iron_golem,distance=..24] run function thieving_bird:golem_anger
tag @s remove tb_self
