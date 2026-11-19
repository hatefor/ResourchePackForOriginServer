execute store result score @s vs_x run data get entity @s Pos[0] 4
execute store result score @s vs_y run data get entity @s Pos[1] 4
execute store result score @s vs_z run data get entity @s Pos[2] 4
scoreboard players add @s vs_y 256
execute if predicate vsealkwt:in_overworld run scoreboard players set @s vs_dim 0
execute if predicate vsealkwt:in_nether run scoreboard players set @s vs_dim 1
execute unless predicate vsealkwt:in_overworld unless predicate vsealkwt:in_nether run scoreboard players set @s vs_dim 2
