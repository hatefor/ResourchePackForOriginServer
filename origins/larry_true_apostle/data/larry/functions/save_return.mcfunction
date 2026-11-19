execute store result score @s larry_x run data get entity @s Pos[0] 100
execute store result score @s larry_y run data get entity @s Pos[1] 100
execute store result score @s larry_z run data get entity @s Pos[2] 100
execute if predicate larry:in_overworld run scoreboard players set @s larry_dim 0
execute if predicate larry:in_nether run scoreboard players set @s larry_dim 1
execute if predicate larry:in_end run scoreboard players set @s larry_dim 2
execute unless predicate larry:in_overworld unless predicate larry:in_nether unless predicate larry:in_end run scoreboard players set @s larry_dim 3
