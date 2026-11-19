execute as @a[scores={kk_dash=1..}] at @s run function kittyknight:dash_tick
execute as @a[scores={kk_storm=1..}] at @s run function kittyknight:storm_tick
execute as @e[type=marker,tag=kk_orb] at @s run function kittyknight:orb_tick
