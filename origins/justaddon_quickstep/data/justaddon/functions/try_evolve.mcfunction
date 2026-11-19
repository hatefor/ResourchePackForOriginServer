function justaddon:progress
execute if score #all qs_tmp matches 4 run tellraw @s {"text": "✦ Every trial is complete. The light answers...", "color": "yellow", "bold": true}
execute if score #all qs_tmp matches 4 run function justaddon:ascend
