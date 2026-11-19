tag @s add vs_self
scoreboard players set #hit vs_tmp 0
scoreboard players set #steps vs_tmp 0
scoreboard players set #mode vs_tmp 1
scoreboard players set #max vs_tmp 20
execute if predicate vsealkwt:in_end run scoreboard players set #mode vs_tmp 2
execute if predicate vsealkwt:in_end run scoreboard players set #max vs_tmp 400
execute anchored eyes positioned ^ ^ ^ run function vsealkwt:pray_step
execute if score #hit vs_tmp matches 0 run function vsealkwt:self_cross
tag @s remove vs_self
