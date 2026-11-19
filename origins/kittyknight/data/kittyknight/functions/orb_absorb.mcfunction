particle minecraft:flash ~ ~ ~ 0 0 0 0 1
particle minecraft:electric_spark ~ ~ ~ 0.5 0.5 0.5 0.4 60
playsound minecraft:entity.lightning_bolt.impact player @a ~ ~ ~ 0.6 2
scoreboard players set @p[tag=kk_self] kk_gain 1
kill @s
