scoreboard players operation #code tb_tmp = @s tb_pick
scoreboard players set @s tb_pick 0
tag @s add tb_self
scoreboard players operation #me tb_id = @s tb_id
execute as @a if score @s tb_vic = #me tb_id run tag @s add tb_victim
execute if score @s tb_menu matches 1.. if entity @a[tag=tb_victim,distance=..20] run function thieving_bird:take_dispatch
execute unless score @s tb_menu matches 1.. run title @s actionbar {"text":"That menu has expired","color":"gray"}
execute if score @s tb_menu matches 1.. unless entity @a[tag=tb_victim,distance=..20] run title @s actionbar {"text":"Too far from your mark","color":"red"}
tag @a remove tb_victim
tag @s remove tb_self
