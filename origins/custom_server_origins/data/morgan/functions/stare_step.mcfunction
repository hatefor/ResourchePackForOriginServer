execute if score #found morgan_rng matches 0 if entity @e[dx=0,dy=0,dz=0,tag=!morgan_self,type=!minecraft:item,type=!minecraft:marker,type=!minecraft:area_effect_cloud,type=!minecraft:experience_orb] run function morgan:stare_hit
scoreboard players remove #steps morgan_rng 1
execute if score #found morgan_rng matches 0 if score #steps morgan_rng matches 1.. if block ~ ~ ~ minecraft:air positioned ^ ^ ^0.5 run function morgan:stare_step
