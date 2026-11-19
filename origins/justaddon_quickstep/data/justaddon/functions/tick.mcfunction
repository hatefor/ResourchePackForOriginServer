scoreboard players add #timer qs_tmp 1
execute if score #timer qs_tmp matches 10.. run function justaddon:slow
execute as @a[scores={evo=1..}] run function justaddon:use_evo
execute as @a[scores={qs_progress=1..}] run function justaddon:use_progress
