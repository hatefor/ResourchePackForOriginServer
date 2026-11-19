scoreboard players enable @s qs_progress
function justaddon:calc
execute if score #all qs_tmp matches 4 run scoreboard players enable @s evo
execute if score #all qs_tmp matches 4 unless entity @s[tag=qs_ready] run function justaddon:ready_msg
execute if score #all qs_tmp matches 4 run tag @s add qs_ready
execute unless score #all qs_tmp matches 4 run tag @s remove qs_ready
execute unless score #all qs_tmp matches 4 run scoreboard players reset @s evo
