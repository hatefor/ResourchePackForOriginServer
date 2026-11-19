execute if data entity @s Inventory[{Slot:-106b,id:"minecraft:shield"}] run function thieving_bird:shield_fix
tag @s remove tb_shield_main
execute if data entity @s {SelectedItem:{id:"minecraft:shield"}} run tag @s add tb_shield_main
