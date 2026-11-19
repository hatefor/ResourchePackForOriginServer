particle minecraft:reverse_portal ~ ~1 ~ 0.4 0.8 0.4 0.1 60
execute if score @s vs_dim matches 0..1 run function vsealkwt:restore_pos
execute unless score @s vs_dim matches 0..1 run function vsealkwt:spawn_fallback
