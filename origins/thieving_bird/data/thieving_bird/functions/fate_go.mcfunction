tag @s add tb_fate_tgt
scoreboard players operation @s tb_link = #me tb_id
tag @a[tag=tb_self] add tb_fate_bird
scoreboard players set @a[tag=tb_self] tb_fate 15
title @s[type=minecraft:player] actionbar {"text":"A thief has stolen your fate!","color":"dark_purple"}
title @a[tag=tb_self] actionbar [{"text":"Fate stolen from ","color":"light_purple","italic":true},{"selector":"@s","color":"yellow"}]
particle minecraft:enchant ~ ~1.2 ~ 0.4 0.6 0.4 0.5 40
particle minecraft:end_rod ~ ~1.2 ~ 0.3 0.5 0.3 0.05 12
playsound minecraft:entity.evoker.cast_spell player @a ~ ~ ~ 1 1.4
playsound minecraft:block.amethyst_block.chime player @a ~ ~ ~ 1 0.8
