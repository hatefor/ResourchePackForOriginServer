scoreboard players set #hit larry_tmp 1
execute if score #mode larry_tmp matches 1 run function larry:gaze_hit
execute if score #mode larry_tmp matches 2 at @s run function larry:snare_hit
