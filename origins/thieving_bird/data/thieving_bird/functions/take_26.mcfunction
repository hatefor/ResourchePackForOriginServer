execute if data entity @a[tag=tb_victim,limit=1] Inventory[{Slot:25b}] run summon minecraft:item ~ ~1 ~ {Tags:["tb_loot"],PickupDelay:0,Item:{id:"minecraft:stone",Count:1b}}
execute if data entity @a[tag=tb_victim,limit=1] Inventory[{Slot:25b}] run data modify entity @e[type=minecraft:item,tag=tb_loot,limit=1,distance=..3] Item set from entity @a[tag=tb_victim,limit=1] Inventory[{Slot:25b}]
execute if data entity @a[tag=tb_victim,limit=1] Inventory[{Slot:25b}] run data remove entity @e[type=minecraft:item,tag=tb_loot,limit=1,distance=..3] Item.Slot
execute if data entity @a[tag=tb_victim,limit=1] Inventory[{Slot:25b}] run tag @e[type=minecraft:item,tag=tb_loot,distance=..3] remove tb_loot
execute if data entity @a[tag=tb_victim,limit=1] Inventory[{Slot:25b}] run function thieving_bird:theft_done
execute if data entity @a[tag=tb_victim,limit=1] Inventory[{Slot:25b}] run item replace entity @a[tag=tb_victim,limit=1] container.25 with minecraft:air
execute unless data entity @a[tag=tb_victim,limit=1] Inventory[{Slot:25b}] unless score @s tb_menu matches 0 run title @s actionbar {"text":"That slot is empty now","color":"gray"}
