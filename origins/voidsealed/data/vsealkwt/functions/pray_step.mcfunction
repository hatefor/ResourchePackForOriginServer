scoreboard players add #steps vs_tmp 1
execute if score #hit vs_tmp matches 0 positioned ~ ~-0.9 ~ as @a[distance=..1.1,tag=!vs_self,gamemode=!spectator,limit=1,sort=nearest] run function vsealkwt:exile_target
execute if score #hit vs_tmp matches 0 if score #steps vs_tmp <= #max vs_tmp positioned ^ ^ ^0.5 if block ~ ~ ~ #vsealkwt:ray_passable run function vsealkwt:pray_step
