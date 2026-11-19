item modify entity @s weapon.mainhand morgan:take_one
effect give @s minecraft:absorption 30 1 true
effect give @s minecraft:regeneration 3 1 true
execute at @s run particle minecraft:happy_villager ~ ~1 ~ 0.4 0.6 0.4 0.1 30 force
execute at @s run playsound minecraft:entity.slime.squish master @a ~ ~ ~ 1 1
