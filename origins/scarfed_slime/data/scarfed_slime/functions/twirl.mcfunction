tag @s add ss_self
execute as @e[distance=0.1..4.5,type=!item,type=!experience_orb,type=!marker,type=!area_effect_cloud] run damage @s 5 minecraft:player_attack by @p[tag=ss_self]
particle minecraft:sweep_attack ~ ~1 ~ 3 0.2 3 0 14
particle minecraft:dust 0.85 0.08 0.15 1.4 ~ ~1.2 ~ 3 0.3 3 0 70
particle minecraft:item_slime ~ ~0.5 ~ 2 0.3 2 0 25
playsound minecraft:entity.player.attack.sweep player @a ~ ~ ~ 1 0.8
playsound minecraft:entity.slime.squish player @a ~ ~ ~ 1 0.7
tag @s remove ss_self
