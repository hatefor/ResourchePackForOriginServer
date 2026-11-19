function larry:return_home
tag @s remove larry_guest
effect clear @s minecraft:weakness
effect clear @s minecraft:darkness
tellraw @s {"text":"The realm lets you go.","color":"gray","italic":true}
