effect give @s minecraft:resistance 8 4 true
effect give @s minecraft:slow_falling 8 0 true
execute at @s run particle minecraft:reverse_portal ~ ~1 ~ 0.4 0.8 0.4 0.15 60
title @s times 20 80 30
title @s subtitle {"text":"Larry's Apostle brought you here.","color":"dark_red","italic":true}
title @s title {"text":"The Gilded Expanse","color":"gold","bold":true}
tellraw @s {"text":"A hand of blackstone closes around you. You are a guest of the realm.","color":"dark_red","italic":true}
tellraw @s [{"text":"[Leave the realm]","color":"gold","bold":true,"clickEvent":{"action":"run_command","value":"/trigger larry_leave"},"hoverEvent":{"action":"show_text","contents":"Return to where you came from"}},{"text":"  or type /trigger larry_leave at any time","color":"gray"}]
