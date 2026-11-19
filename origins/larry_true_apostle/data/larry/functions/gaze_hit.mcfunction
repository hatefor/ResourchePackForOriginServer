execute if score #amp larry_tmp matches 1 run effect give @s minecraft:wither 10 1
execute if score #amp larry_tmp matches 2 run effect give @s minecraft:wither 10 2
execute at @s run particle minecraft:soul ~ ~1 ~ 0.3 0.5 0.3 0.05 30
execute at @s run playsound minecraft:entity.wither.ambient hostile @a ~ ~ ~ 1 1.6
execute if entity @s[type=player] run title @s actionbar {"text":"You feel Larry's eyes burning into you...","color":"dark_red"}
