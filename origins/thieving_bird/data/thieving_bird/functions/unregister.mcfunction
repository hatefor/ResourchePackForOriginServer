attribute @s minecraft:generic.movement_speed modifier remove 5b9e7d14-0b3a-4a00-8f00-00000000a001
attribute @s minecraft:generic.attack_damage modifier remove 5b9e7d14-0b3a-4a00-8f00-00000000a002
tag @s remove tb_user
scoreboard players set @s tb_hoard 0
function thieving_bird:fate_clear
tag @s remove tb_shield_main
