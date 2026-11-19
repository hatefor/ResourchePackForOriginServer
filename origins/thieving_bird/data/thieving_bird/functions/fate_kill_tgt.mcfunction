tag @s remove tb_fate_tgt
scoreboard players reset @s tb_link
title @s[type=minecraft:player] actionbar {"text":"The thief fell, and your stolen fate fell with it","color":"dark_purple"}
particle minecraft:soul_fire_flame ~ ~1 ~ 0.3 0.5 0.3 0.05 20
kill @s
