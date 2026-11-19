tag @s add tb_marked
scoreboard players set @s tb_mark 60
scoreboard players set @a[tag=tb_self] tb_intent 60
title @a[tag=tb_self] actionbar [{"text":"Killing intent stolen from ","color":"dark_red","bold":true},{"selector":"@s","color":"red"}]
particle minecraft:angry_villager ~ ~2 ~ 0.3 0.3 0.3 0 12
playsound minecraft:entity.vex.charge player @a ~ ~ ~ 1 0.6
