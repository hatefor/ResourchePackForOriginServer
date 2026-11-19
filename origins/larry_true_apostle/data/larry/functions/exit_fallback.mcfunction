tellraw @s {"text":"You step out of the realm near the world's center.","color":"gray","italic":true}
execute in minecraft:overworld run spreadplayers 0 0 1 24 false @s
execute if entity @s[tag=larry_src] in larry:realm as @e[tag=larry_carry] in minecraft:overworld run tp @s @a[tag=larry_src,limit=1]
execute if entity @s[tag=larry_src] run function larry:carry_cleanup
