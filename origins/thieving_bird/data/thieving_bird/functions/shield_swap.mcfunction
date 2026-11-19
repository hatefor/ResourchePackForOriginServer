summon minecraft:armor_stand ~ ~ ~ {Marker:1b,Invisible:1b,NoGravity:1b,Silent:1b,Tags:["tb_tmp_stand"]}
item replace entity @e[type=minecraft:armor_stand,tag=tb_tmp_stand,limit=1,sort=nearest,distance=..2] weapon.mainhand from entity @s weapon.mainhand
item replace entity @s weapon.mainhand from entity @s weapon.offhand
item replace entity @s weapon.offhand from entity @e[type=minecraft:armor_stand,tag=tb_tmp_stand,limit=1,sort=nearest,distance=..2] weapon.mainhand
item replace entity @e[type=minecraft:armor_stand,tag=tb_tmp_stand,limit=1,sort=nearest,distance=..2] weapon.mainhand with minecraft:air
kill @e[type=minecraft:armor_stand,tag=tb_tmp_stand,distance=..2]
title @s actionbar {"text":"A bird has no use for a shield","color":"gray"}
