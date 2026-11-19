scoreboard players set @s larry_wait 0
execute if score @s larry_dim matches 0..2 run function larry:return_hop
execute unless score @s larry_dim matches 0..2 run function larry:exit_fallback
