scoreboard players set #m tb_tmp 0
scoreboard players add #idx tb_tmp 1
scoreboard players operation #idx tb_tmp %= #30 tb_tmp
execute if score #idx tb_tmp matches 0 as @a run scoreboard players set @s tb_b0 0
execute if score #idx tb_tmp matches 1 as @a run scoreboard players set @s tb_b1 0
execute if score #idx tb_tmp matches 2 as @a run scoreboard players set @s tb_b2 0
execute if score #idx tb_tmp matches 3 as @a run scoreboard players set @s tb_b3 0
execute if score #idx tb_tmp matches 4 as @a run scoreboard players set @s tb_b4 0
execute if score #idx tb_tmp matches 5 as @a run scoreboard players set @s tb_b5 0
execute if score #idx tb_tmp matches 6 as @a run scoreboard players set @s tb_b6 0
execute if score #idx tb_tmp matches 7 as @a run scoreboard players set @s tb_b7 0
execute if score #idx tb_tmp matches 8 as @a run scoreboard players set @s tb_b8 0
execute if score #idx tb_tmp matches 9 as @a run scoreboard players set @s tb_b9 0
execute if score #idx tb_tmp matches 10 as @a run scoreboard players set @s tb_b10 0
execute if score #idx tb_tmp matches 11 as @a run scoreboard players set @s tb_b11 0
execute if score #idx tb_tmp matches 12 as @a run scoreboard players set @s tb_b12 0
execute if score #idx tb_tmp matches 13 as @a run scoreboard players set @s tb_b13 0
execute if score #idx tb_tmp matches 14 as @a run scoreboard players set @s tb_b14 0
execute if score #idx tb_tmp matches 15 as @a run scoreboard players set @s tb_b15 0
execute if score #idx tb_tmp matches 16 as @a run scoreboard players set @s tb_b16 0
execute if score #idx tb_tmp matches 17 as @a run scoreboard players set @s tb_b17 0
execute if score #idx tb_tmp matches 18 as @a run scoreboard players set @s tb_b18 0
execute if score #idx tb_tmp matches 19 as @a run scoreboard players set @s tb_b19 0
execute if score #idx tb_tmp matches 20 as @a run scoreboard players set @s tb_b20 0
execute if score #idx tb_tmp matches 21 as @a run scoreboard players set @s tb_b21 0
execute if score #idx tb_tmp matches 22 as @a run scoreboard players set @s tb_b22 0
execute if score #idx tb_tmp matches 23 as @a run scoreboard players set @s tb_b23 0
execute if score #idx tb_tmp matches 24 as @a run scoreboard players set @s tb_b24 0
execute if score #idx tb_tmp matches 25 as @a run scoreboard players set @s tb_b25 0
execute if score #idx tb_tmp matches 26 as @a run scoreboard players set @s tb_b26 0
execute if score #idx tb_tmp matches 27 as @a run scoreboard players set @s tb_b27 0
execute if score #idx tb_tmp matches 28 as @a run scoreboard players set @s tb_b28 0
execute if score #idx tb_tmp matches 29 as @a run scoreboard players set @s tb_b29 0
execute as @a[tag=tb_user] run function thieving_bird:hoard_calc
