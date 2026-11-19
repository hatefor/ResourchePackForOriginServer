data modify storage morgan:tmp who set from entity @s UUID
execute store success score #diff morgan_rng run data modify storage morgan:tmp who set from storage morgan:tmp owner
execute if score #diff morgan_rng matches 1 run effect give @s minecraft:darkness 10 0
