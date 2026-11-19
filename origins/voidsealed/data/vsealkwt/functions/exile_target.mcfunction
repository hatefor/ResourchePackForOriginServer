scoreboard players set #hit vs_tmp 1
scoreboard players set @a[tag=vs_self] vs_ok 1
scoreboard players set @s vs_timer 200
scoreboard players set @s vs_kind 1
execute if score #mode vs_tmp matches 1 run function vsealkwt:go_end
execute if score #mode vs_tmp matches 2 run scoreboard players set @s vs_kind 2
execute if score #mode vs_tmp matches 2 run function vsealkwt:return_home
title @s actionbar {"text":"The void flings you away for 10 seconds...","color":"dark_purple","italic":true}
title @a[tag=vs_self] actionbar [{"text":"You cast ","color":"light_purple"},{"selector":"@s","color":"white"},{"text":" out of the dimension for 10 seconds","color":"light_purple"}]
