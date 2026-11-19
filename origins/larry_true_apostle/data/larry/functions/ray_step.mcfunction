scoreboard players add #steps larry_tmp 1
execute if score #mode larry_tmp matches 1 run particle minecraft:soul_fire_flame ~ ~ ~ 0.03 0.03 0.03 0 1
execute if score #mode larry_tmp matches 2 run particle minecraft:dust 1 0.75 0.15 1 ~ ~ ~ 0.03 0.03 0.03 0 1
execute if score #mode larry_tmp matches 1 positioned ~ ~-0.9 ~ as @e[distance=..1.1,tag=!larry_src,type=!#larry:ray_ignore,limit=1,sort=nearest] run function larry:ray_hit
execute if score #mode larry_tmp matches 2 positioned ~ ~-0.9 ~ as @e[distance=..1.1,tag=!larry_src,type=player,gamemode=!spectator,limit=1,sort=nearest] run function larry:ray_hit
execute if score #hit larry_tmp matches 0 if score #steps larry_tmp matches ..60 positioned ^ ^ ^0.5 if block ~ ~ ~ #larry:ray_passable run function larry:ray_step
