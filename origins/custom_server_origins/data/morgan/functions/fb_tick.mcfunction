data remove storage morgan:tmp owner
data modify storage morgan:tmp owner set from entity @s Owner
execute as @e[distance=..2.5,type=!minecraft:small_fireball,type=!minecraft:item,type=!minecraft:marker] run function morgan:fb_hit
