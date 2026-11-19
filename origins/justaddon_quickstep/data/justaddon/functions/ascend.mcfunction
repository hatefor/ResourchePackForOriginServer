scoreboard players set #b qs_tmp 0
origin set @s origins:origin justaddon:being_of_light
execute store result score #b qs_tmp run origin has @s origins:origin justaddon:being_of_light
execute if score #b qs_tmp matches 1.. run function justaddon:ascend_fx
execute unless score #b qs_tmp matches 1.. run tellraw @s {"text": "✘ Ascension failed: the Being of Light origin did not load, so nothing was consumed. Check latest.log for 'justaddon'.", "color": "red"}
