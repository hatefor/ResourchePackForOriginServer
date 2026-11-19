scoreboard players set @s tb_menu 0
execute as @a[tag=tb_victim] run scoreboard players set @s tb_vic 0
title @a[tag=tb_victim] actionbar {"text":"Something was stolen from you!","color":"red","bold":true}
particle minecraft:poof ~ ~1.2 ~ 0.3 0.4 0.3 0.05 15
playsound minecraft:entity.item.pickup player @a ~ ~ ~ 1 0.5
playsound minecraft:entity.parrot.imitate.evoker player @a ~ ~ ~ 1 1.8
function thieving_bird:theft_gain
