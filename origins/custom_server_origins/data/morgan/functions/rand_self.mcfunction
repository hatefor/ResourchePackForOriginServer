summon minecraft:marker ~ ~ ~ {Tags:["morgan_rng"]}
execute store result score #r morgan_rng run data get entity @e[type=minecraft:marker,tag=morgan_rng,limit=1] UUID[0]
kill @e[type=minecraft:marker,tag=morgan_rng]
scoreboard players set #n morgan_rng 31
scoreboard players operation #r morgan_rng %= #n morgan_rng
execute if score #r morgan_rng matches 0 run effect give @s minecraft:speed 20 2
execute if score #r morgan_rng matches 1 run effect give @s minecraft:slowness 20 2
execute if score #r morgan_rng matches 2 run effect give @s minecraft:haste 20 2
execute if score #r morgan_rng matches 3 run effect give @s minecraft:mining_fatigue 20 2
execute if score #r morgan_rng matches 4 run effect give @s minecraft:strength 20 2
execute if score #r morgan_rng matches 5 run effect give @s minecraft:instant_health 1 2
execute if score #r morgan_rng matches 6 run effect give @s minecraft:jump_boost 20 2
execute if score #r morgan_rng matches 7 run effect give @s minecraft:nausea 20 2
execute if score #r morgan_rng matches 8 run effect give @s minecraft:regeneration 20 2
execute if score #r morgan_rng matches 9 run effect give @s minecraft:resistance 20 2
execute if score #r morgan_rng matches 10 run effect give @s minecraft:fire_resistance 20 2
execute if score #r morgan_rng matches 11 run effect give @s minecraft:water_breathing 20 2
execute if score #r morgan_rng matches 12 run effect give @s minecraft:invisibility 20 2
execute if score #r morgan_rng matches 13 run effect give @s minecraft:blindness 20 2
execute if score #r morgan_rng matches 14 run effect give @s minecraft:night_vision 20 2
execute if score #r morgan_rng matches 15 run effect give @s minecraft:hunger 20 2
execute if score #r morgan_rng matches 16 run effect give @s minecraft:weakness 20 2
execute if score #r morgan_rng matches 17 run effect give @s minecraft:poison 20 2
execute if score #r morgan_rng matches 18 run effect give @s minecraft:health_boost 20 2
execute if score #r morgan_rng matches 19 run effect give @s minecraft:absorption 20 2
execute if score #r morgan_rng matches 20 run effect give @s minecraft:saturation 1 2
execute if score #r morgan_rng matches 21 run effect give @s minecraft:glowing 20 2
execute if score #r morgan_rng matches 22 run effect give @s minecraft:luck 20 2
execute if score #r morgan_rng matches 23 run effect give @s minecraft:unluck 20 2
execute if score #r morgan_rng matches 24 run effect give @s minecraft:slow_falling 20 2
execute if score #r morgan_rng matches 25 run effect give @s minecraft:conduit_power 20 2
execute if score #r morgan_rng matches 26 run effect give @s minecraft:dolphins_grace 20 2
execute if score #r morgan_rng matches 27 run effect give @s minecraft:darkness 20 2
execute if score #r morgan_rng matches 28 run effect give @s minecraft:levitation 20 2
execute if score #r morgan_rng matches 29 run effect give @s minecraft:wither 20 2
execute if score #r morgan_rng matches 30 run effect give @s minecraft:instant_damage 1 2
