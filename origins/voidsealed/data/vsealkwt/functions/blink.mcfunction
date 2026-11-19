scoreboard players set #steps vs_tmp 0
scoreboard players set #done vs_tmp 0
execute anchored eyes positioned ^ ^ ^ run function vsealkwt:blink_step
execute if score #done vs_tmp matches 0 run title @s actionbar {"text":"There is nothing to teleport to there","color":"gray"}
