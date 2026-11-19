scoreboard players set #steps tb_tmp 0
scoreboard players set #done tb_tmp 0
particle minecraft:portal ~ ~1 ~ 0.3 0.6 0.3 0.5 40
playsound minecraft:entity.enderman.teleport player @a ~ ~ ~ 1 1.5
execute anchored eyes positioned ^ ^ ^ run function thieving_bird:blink_step
