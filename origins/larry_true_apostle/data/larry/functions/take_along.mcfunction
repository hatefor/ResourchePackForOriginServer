tag @s add larry_src
tag @e[distance=..16,tag=!larry_src,type=!#larry:no_carry] add larry_carry
execute unless entity @e[tag=larry_carry,limit=1] run title @s actionbar {"text":"Nothing is close enough to take along.","color":"gray"}
execute if entity @e[tag=larry_carry,limit=1] run function larry:take_along_go
tag @e[tag=larry_carry] remove larry_carry
execute in larry:realm run tag @e[tag=larry_carry] remove larry_carry
tag @s remove larry_src
