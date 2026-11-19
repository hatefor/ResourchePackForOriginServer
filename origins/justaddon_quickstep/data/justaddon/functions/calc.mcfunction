execute store result score #lv qs_tmp run experience query @s levels
execute store result score #y qs_tmp run data get entity @s Pos[1]
scoreboard players set #cap300 qs_tmp 300
scoreboard players set #cap40 qs_tmp 40
scoreboard players set #cap383 qs_tmp 383
scoreboard players set #ten qs_tmp 10
scoreboard players set #zero qs_tmp 0
scoreboard players operation #fk qs_tmp = @s qs_kills
scoreboard players operation #fk qs_tmp < #cap300 qs_tmp
scoreboard players operation #fk qs_tmp *= #ten qs_tmp
scoreboard players operation #fk qs_tmp /= #cap300 qs_tmp
scoreboard players operation #fx qs_tmp = #lv qs_tmp
scoreboard players operation #fx qs_tmp < #cap40 qs_tmp
scoreboard players operation #fx qs_tmp *= #ten qs_tmp
scoreboard players operation #fx qs_tmp /= #cap40 qs_tmp
scoreboard players operation #fh qs_tmp = #y qs_tmp
scoreboard players add #fh qs_tmp 64
scoreboard players operation #fh qs_tmp > #zero qs_tmp
scoreboard players operation #fh qs_tmp < #cap383 qs_tmp
scoreboard players operation #fh qs_tmp *= #ten qs_tmp
scoreboard players operation #fh qs_tmp /= #cap383 qs_tmp
scoreboard players set #all qs_tmp 0
execute if score #fk qs_tmp matches 10 run scoreboard players add #all qs_tmp 1
execute if score #fx qs_tmp matches 10 run scoreboard players add #all qs_tmp 1
execute if score #fh qs_tmp matches 10 run scoreboard players add #all qs_tmp 1
scoreboard players set #star qs_tmp 0
execute if entity @s[nbt={Inventory:[{id:"minecraft:nether_star"}]}] run scoreboard players set #star qs_tmp 1
scoreboard players operation #all qs_tmp += #star qs_tmp
