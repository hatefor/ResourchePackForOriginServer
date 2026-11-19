tag @s add morgan_self
scoreboard players set #found morgan_rng 0
scoreboard players set #steps morgan_rng 60
execute anchored eyes positioned ^ ^ ^ run function morgan:stare_step
tag @s remove morgan_self
