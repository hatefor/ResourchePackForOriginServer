tag @s add larry_src
scoreboard players set #steps larry_tmp 0
scoreboard players set #hit larry_tmp 0
scoreboard players set #mode larry_tmp 2
execute anchored eyes positioned ^ ^ ^ run function larry:ray_step
execute if score #hit larry_tmp matches 0 run title @s actionbar {"text":"No player in your gaze.","color":"dark_gray"}
tag @s remove larry_src
