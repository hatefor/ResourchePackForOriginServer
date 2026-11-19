particle minecraft:reverse_portal ~ ~1 ~ 0.4 0.8 0.4 0.15 60
particle minecraft:soul_fire_flame ~ ~0.2 ~ 0.4 0.1 0.4 0.05 30
playsound minecraft:block.respawn_anchor.deplete player @a ~ ~ ~ 1 0.5
execute in larry:realm run spreadplayers 0 0 1 12 false @s
execute unless predicate larry:in_realm in larry:realm run tp @s 0.5 100 0.5
execute if predicate larry:in_realm run function larry:arrive_ok
execute unless predicate larry:in_realm run function larry:arrive_fail
