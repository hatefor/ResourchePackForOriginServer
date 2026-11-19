scoreboard players operation @s tb_vic = #me tb_id
scoreboard players set @a[tag=tb_self] tb_menu 600
scoreboard players enable @a[tag=tb_self] tb_pick
tellraw @a[tag=tb_self] ["",{"text":"=== Pockets of ","color":"gold","bold":true},{"selector":"@s","color":"gold","bold":true},{"text":" ===","color":"gold","bold":true}]
function thieving_bird:menu_lines
tellraw @a[tag=tb_self] {"text":"Click one item to steal it. The menu closes in 30 seconds or when you walk 20 blocks away.","color":"gray","italic":true}
title @s actionbar {"text":"Someone is rifling through your pockets!","color":"red"}
playsound minecraft:entity.parrot.imitate.pillager player @a ~ ~ ~ 1 1.5
