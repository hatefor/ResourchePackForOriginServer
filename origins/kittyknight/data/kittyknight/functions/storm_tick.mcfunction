scoreboard players remove @s kk_storm 1
scoreboard players operation #t kk_tmp = @s kk_storm
scoreboard players operation #t kk_tmp %= #six kk_tmp
execute if score #t kk_tmp matches 0 run function kittyknight:storm_bolt
particle minecraft:electric_spark ~ ~1 ~ 0.4 0.8 0.4 0.3 6
