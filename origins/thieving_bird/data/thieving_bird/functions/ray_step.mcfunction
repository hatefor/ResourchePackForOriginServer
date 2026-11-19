scoreboard players add #steps tb_tmp 1
execute if score #hit tb_tmp matches 0 if score #mode tb_tmp matches 1..2 positioned ~ ~-0.9 ~ as @a[distance=..1.1,tag=!tb_self,gamemode=!spectator,limit=1,sort=nearest] run function thieving_bird:ray_hit
execute if score #hit tb_tmp matches 0 if score #mode tb_tmp matches 3..4 positioned ~ ~-0.9 ~ as @e[distance=..1.1,tag=!tb_self,type=!#thieving_bird:ray_ignore,limit=1,sort=nearest] run function thieving_bird:ray_hit
execute if score #hit tb_tmp matches 0 if score #steps tb_tmp matches ..60 positioned ^ ^ ^0.5 if block ~ ~ ~ #thieving_bird:ray_passable run function thieving_bird:ray_step
