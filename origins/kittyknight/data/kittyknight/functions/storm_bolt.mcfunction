summon marker ~ ~ ~ {Tags:["kk_sm"]}
spreadplayers ~ ~ 0 13 false @e[type=marker,tag=kk_sm,limit=1]
execute as @e[type=marker,tag=kk_sm] at @s unless entity @a[distance=..4] run summon minecraft:lightning_bolt ~ ~ ~
kill @e[type=marker,tag=kk_sm]
