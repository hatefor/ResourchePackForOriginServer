scoreboard players set #q qs_tmp 0
scoreboard players set #a qs_tmp 0
execute store result score #q qs_tmp run origin has @s origins:origin justaddon:quickstep
execute if score #q qs_tmp matches 1.. run origin set @s origins:origin justaddon:quickstep_awakened
tag @s remove qs_quick
execute store result score #a qs_tmp run origin has @s origins:origin justaddon:quickstep_awakened
execute if score #a qs_tmp matches 1.. run tag @s add qs_quick
