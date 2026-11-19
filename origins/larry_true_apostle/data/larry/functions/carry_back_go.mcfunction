execute if score @s larry_dim matches 0 in larry:realm as @e[tag=larry_carry] in minecraft:overworld run tp @s @a[tag=larry_src,limit=1]
execute if score @s larry_dim matches 1 in larry:realm as @e[tag=larry_carry] in minecraft:the_nether run tp @s @a[tag=larry_src,limit=1]
execute if score @s larry_dim matches 2 in larry:realm as @e[tag=larry_carry] in minecraft:the_end run tp @s @a[tag=larry_src,limit=1]
function larry:carry_cleanup
