tag @s add larry_leaving
effect give @s minecraft:slow_falling 15 0 true
effect give @s minecraft:resistance 6 4 true
execute if score @s larry_dim matches 0 in minecraft:overworld run tp @s 0 400 0
execute if score @s larry_dim matches 1 in minecraft:the_nether run tp @s 0 400 0
execute if score @s larry_dim matches 2 in minecraft:the_end run tp @s 0 400 0
schedule function larry:return_finish 3t replace
