# Runs as and at every entity inside any domain, every tick. Only acts inside a domain named "Example".
execute if entity @s[tag=ot_in_example,tag=!ot_domain_owner] run effect give @s minecraft:slowness 2 1 true
execute if entity @s[tag=ot_in_example,tag=ot_domain_owner] run effect give @s minecraft:strength 2 0 true
