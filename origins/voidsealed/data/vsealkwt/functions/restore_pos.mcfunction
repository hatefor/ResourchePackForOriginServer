scoreboard players operation #x vs_tmp = @s vs_x
scoreboard players operation #y vs_tmp = @s vs_y
scoreboard players operation #z vs_tmp = @s vs_z
scoreboard players set #xn vs_tmp 0
scoreboard players set #zn vs_tmp 0
execute if score #x vs_tmp matches ..-1 run scoreboard players set #xn vs_tmp 1
execute if score #x vs_tmp matches ..-1 run scoreboard players operation #x vs_tmp *= #-1 vs_tmp
execute if score #z vs_tmp matches ..-1 run scoreboard players set #zn vs_tmp 1
execute if score #z vs_tmp matches ..-1 run scoreboard players operation #z vs_tmp *= #-1 vs_tmp
execute if score @s vs_dim matches 0 in minecraft:overworld run tp @s 0 -64 0
execute if score @s vs_dim matches 1 in minecraft:the_nether run tp @s 0 -64 0
execute if score #x vs_tmp matches 67108864.. if score #xn vs_tmp matches 0 run tp @s ~16777216 ~ ~
execute if score #x vs_tmp matches 67108864.. if score #xn vs_tmp matches 1 run tp @s ~-16777216 ~ ~
execute if score #x vs_tmp matches 67108864.. run scoreboard players remove #x vs_tmp 67108864
execute if score #x vs_tmp matches 33554432.. if score #xn vs_tmp matches 0 run tp @s ~8388608 ~ ~
execute if score #x vs_tmp matches 33554432.. if score #xn vs_tmp matches 1 run tp @s ~-8388608 ~ ~
execute if score #x vs_tmp matches 33554432.. run scoreboard players remove #x vs_tmp 33554432
execute if score #x vs_tmp matches 16777216.. if score #xn vs_tmp matches 0 run tp @s ~4194304 ~ ~
execute if score #x vs_tmp matches 16777216.. if score #xn vs_tmp matches 1 run tp @s ~-4194304 ~ ~
execute if score #x vs_tmp matches 16777216.. run scoreboard players remove #x vs_tmp 16777216
execute if score #x vs_tmp matches 8388608.. if score #xn vs_tmp matches 0 run tp @s ~2097152 ~ ~
execute if score #x vs_tmp matches 8388608.. if score #xn vs_tmp matches 1 run tp @s ~-2097152 ~ ~
execute if score #x vs_tmp matches 8388608.. run scoreboard players remove #x vs_tmp 8388608
execute if score #x vs_tmp matches 4194304.. if score #xn vs_tmp matches 0 run tp @s ~1048576 ~ ~
execute if score #x vs_tmp matches 4194304.. if score #xn vs_tmp matches 1 run tp @s ~-1048576 ~ ~
execute if score #x vs_tmp matches 4194304.. run scoreboard players remove #x vs_tmp 4194304
execute if score #x vs_tmp matches 2097152.. if score #xn vs_tmp matches 0 run tp @s ~524288 ~ ~
execute if score #x vs_tmp matches 2097152.. if score #xn vs_tmp matches 1 run tp @s ~-524288 ~ ~
execute if score #x vs_tmp matches 2097152.. run scoreboard players remove #x vs_tmp 2097152
execute if score #x vs_tmp matches 1048576.. if score #xn vs_tmp matches 0 run tp @s ~262144 ~ ~
execute if score #x vs_tmp matches 1048576.. if score #xn vs_tmp matches 1 run tp @s ~-262144 ~ ~
execute if score #x vs_tmp matches 1048576.. run scoreboard players remove #x vs_tmp 1048576
execute if score #x vs_tmp matches 524288.. if score #xn vs_tmp matches 0 run tp @s ~131072 ~ ~
execute if score #x vs_tmp matches 524288.. if score #xn vs_tmp matches 1 run tp @s ~-131072 ~ ~
execute if score #x vs_tmp matches 524288.. run scoreboard players remove #x vs_tmp 524288
execute if score #x vs_tmp matches 262144.. if score #xn vs_tmp matches 0 run tp @s ~65536 ~ ~
execute if score #x vs_tmp matches 262144.. if score #xn vs_tmp matches 1 run tp @s ~-65536 ~ ~
execute if score #x vs_tmp matches 262144.. run scoreboard players remove #x vs_tmp 262144
execute if score #x vs_tmp matches 131072.. if score #xn vs_tmp matches 0 run tp @s ~32768 ~ ~
execute if score #x vs_tmp matches 131072.. if score #xn vs_tmp matches 1 run tp @s ~-32768 ~ ~
execute if score #x vs_tmp matches 131072.. run scoreboard players remove #x vs_tmp 131072
execute if score #x vs_tmp matches 65536.. if score #xn vs_tmp matches 0 run tp @s ~16384 ~ ~
execute if score #x vs_tmp matches 65536.. if score #xn vs_tmp matches 1 run tp @s ~-16384 ~ ~
execute if score #x vs_tmp matches 65536.. run scoreboard players remove #x vs_tmp 65536
execute if score #x vs_tmp matches 32768.. if score #xn vs_tmp matches 0 run tp @s ~8192 ~ ~
execute if score #x vs_tmp matches 32768.. if score #xn vs_tmp matches 1 run tp @s ~-8192 ~ ~
execute if score #x vs_tmp matches 32768.. run scoreboard players remove #x vs_tmp 32768
execute if score #x vs_tmp matches 16384.. if score #xn vs_tmp matches 0 run tp @s ~4096 ~ ~
execute if score #x vs_tmp matches 16384.. if score #xn vs_tmp matches 1 run tp @s ~-4096 ~ ~
execute if score #x vs_tmp matches 16384.. run scoreboard players remove #x vs_tmp 16384
execute if score #x vs_tmp matches 8192.. if score #xn vs_tmp matches 0 run tp @s ~2048 ~ ~
execute if score #x vs_tmp matches 8192.. if score #xn vs_tmp matches 1 run tp @s ~-2048 ~ ~
execute if score #x vs_tmp matches 8192.. run scoreboard players remove #x vs_tmp 8192
execute if score #x vs_tmp matches 4096.. if score #xn vs_tmp matches 0 run tp @s ~1024 ~ ~
execute if score #x vs_tmp matches 4096.. if score #xn vs_tmp matches 1 run tp @s ~-1024 ~ ~
execute if score #x vs_tmp matches 4096.. run scoreboard players remove #x vs_tmp 4096
execute if score #x vs_tmp matches 2048.. if score #xn vs_tmp matches 0 run tp @s ~512 ~ ~
execute if score #x vs_tmp matches 2048.. if score #xn vs_tmp matches 1 run tp @s ~-512 ~ ~
execute if score #x vs_tmp matches 2048.. run scoreboard players remove #x vs_tmp 2048
execute if score #x vs_tmp matches 1024.. if score #xn vs_tmp matches 0 run tp @s ~256 ~ ~
execute if score #x vs_tmp matches 1024.. if score #xn vs_tmp matches 1 run tp @s ~-256 ~ ~
execute if score #x vs_tmp matches 1024.. run scoreboard players remove #x vs_tmp 1024
execute if score #x vs_tmp matches 512.. if score #xn vs_tmp matches 0 run tp @s ~128 ~ ~
execute if score #x vs_tmp matches 512.. if score #xn vs_tmp matches 1 run tp @s ~-128 ~ ~
execute if score #x vs_tmp matches 512.. run scoreboard players remove #x vs_tmp 512
execute if score #x vs_tmp matches 256.. if score #xn vs_tmp matches 0 run tp @s ~64 ~ ~
execute if score #x vs_tmp matches 256.. if score #xn vs_tmp matches 1 run tp @s ~-64 ~ ~
execute if score #x vs_tmp matches 256.. run scoreboard players remove #x vs_tmp 256
execute if score #x vs_tmp matches 128.. if score #xn vs_tmp matches 0 run tp @s ~32 ~ ~
execute if score #x vs_tmp matches 128.. if score #xn vs_tmp matches 1 run tp @s ~-32 ~ ~
execute if score #x vs_tmp matches 128.. run scoreboard players remove #x vs_tmp 128
execute if score #x vs_tmp matches 64.. if score #xn vs_tmp matches 0 run tp @s ~16 ~ ~
execute if score #x vs_tmp matches 64.. if score #xn vs_tmp matches 1 run tp @s ~-16 ~ ~
execute if score #x vs_tmp matches 64.. run scoreboard players remove #x vs_tmp 64
execute if score #x vs_tmp matches 32.. if score #xn vs_tmp matches 0 run tp @s ~8 ~ ~
execute if score #x vs_tmp matches 32.. if score #xn vs_tmp matches 1 run tp @s ~-8 ~ ~
execute if score #x vs_tmp matches 32.. run scoreboard players remove #x vs_tmp 32
execute if score #x vs_tmp matches 16.. if score #xn vs_tmp matches 0 run tp @s ~4 ~ ~
execute if score #x vs_tmp matches 16.. if score #xn vs_tmp matches 1 run tp @s ~-4 ~ ~
execute if score #x vs_tmp matches 16.. run scoreboard players remove #x vs_tmp 16
execute if score #x vs_tmp matches 8.. if score #xn vs_tmp matches 0 run tp @s ~2 ~ ~
execute if score #x vs_tmp matches 8.. if score #xn vs_tmp matches 1 run tp @s ~-2 ~ ~
execute if score #x vs_tmp matches 8.. run scoreboard players remove #x vs_tmp 8
execute if score #x vs_tmp matches 4.. if score #xn vs_tmp matches 0 run tp @s ~1 ~ ~
execute if score #x vs_tmp matches 4.. if score #xn vs_tmp matches 1 run tp @s ~-1 ~ ~
execute if score #x vs_tmp matches 4.. run scoreboard players remove #x vs_tmp 4
execute if score #x vs_tmp matches 2.. if score #xn vs_tmp matches 0 run tp @s ~0.5 ~ ~
execute if score #x vs_tmp matches 2.. if score #xn vs_tmp matches 1 run tp @s ~-0.5 ~ ~
execute if score #x vs_tmp matches 2.. run scoreboard players remove #x vs_tmp 2
execute if score #x vs_tmp matches 1.. if score #xn vs_tmp matches 0 run tp @s ~0.25 ~ ~
execute if score #x vs_tmp matches 1.. if score #xn vs_tmp matches 1 run tp @s ~-0.25 ~ ~
execute if score #x vs_tmp matches 1.. run scoreboard players remove #x vs_tmp 1
execute if score #z vs_tmp matches 67108864.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~16777216
execute if score #z vs_tmp matches 67108864.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-16777216
execute if score #z vs_tmp matches 67108864.. run scoreboard players remove #z vs_tmp 67108864
execute if score #z vs_tmp matches 33554432.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~8388608
execute if score #z vs_tmp matches 33554432.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-8388608
execute if score #z vs_tmp matches 33554432.. run scoreboard players remove #z vs_tmp 33554432
execute if score #z vs_tmp matches 16777216.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~4194304
execute if score #z vs_tmp matches 16777216.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-4194304
execute if score #z vs_tmp matches 16777216.. run scoreboard players remove #z vs_tmp 16777216
execute if score #z vs_tmp matches 8388608.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~2097152
execute if score #z vs_tmp matches 8388608.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-2097152
execute if score #z vs_tmp matches 8388608.. run scoreboard players remove #z vs_tmp 8388608
execute if score #z vs_tmp matches 4194304.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~1048576
execute if score #z vs_tmp matches 4194304.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-1048576
execute if score #z vs_tmp matches 4194304.. run scoreboard players remove #z vs_tmp 4194304
execute if score #z vs_tmp matches 2097152.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~524288
execute if score #z vs_tmp matches 2097152.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-524288
execute if score #z vs_tmp matches 2097152.. run scoreboard players remove #z vs_tmp 2097152
execute if score #z vs_tmp matches 1048576.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~262144
execute if score #z vs_tmp matches 1048576.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-262144
execute if score #z vs_tmp matches 1048576.. run scoreboard players remove #z vs_tmp 1048576
execute if score #z vs_tmp matches 524288.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~131072
execute if score #z vs_tmp matches 524288.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-131072
execute if score #z vs_tmp matches 524288.. run scoreboard players remove #z vs_tmp 524288
execute if score #z vs_tmp matches 262144.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~65536
execute if score #z vs_tmp matches 262144.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-65536
execute if score #z vs_tmp matches 262144.. run scoreboard players remove #z vs_tmp 262144
execute if score #z vs_tmp matches 131072.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~32768
execute if score #z vs_tmp matches 131072.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-32768
execute if score #z vs_tmp matches 131072.. run scoreboard players remove #z vs_tmp 131072
execute if score #z vs_tmp matches 65536.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~16384
execute if score #z vs_tmp matches 65536.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-16384
execute if score #z vs_tmp matches 65536.. run scoreboard players remove #z vs_tmp 65536
execute if score #z vs_tmp matches 32768.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~8192
execute if score #z vs_tmp matches 32768.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-8192
execute if score #z vs_tmp matches 32768.. run scoreboard players remove #z vs_tmp 32768
execute if score #z vs_tmp matches 16384.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~4096
execute if score #z vs_tmp matches 16384.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-4096
execute if score #z vs_tmp matches 16384.. run scoreboard players remove #z vs_tmp 16384
execute if score #z vs_tmp matches 8192.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~2048
execute if score #z vs_tmp matches 8192.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-2048
execute if score #z vs_tmp matches 8192.. run scoreboard players remove #z vs_tmp 8192
execute if score #z vs_tmp matches 4096.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~1024
execute if score #z vs_tmp matches 4096.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-1024
execute if score #z vs_tmp matches 4096.. run scoreboard players remove #z vs_tmp 4096
execute if score #z vs_tmp matches 2048.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~512
execute if score #z vs_tmp matches 2048.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-512
execute if score #z vs_tmp matches 2048.. run scoreboard players remove #z vs_tmp 2048
execute if score #z vs_tmp matches 1024.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~256
execute if score #z vs_tmp matches 1024.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-256
execute if score #z vs_tmp matches 1024.. run scoreboard players remove #z vs_tmp 1024
execute if score #z vs_tmp matches 512.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~128
execute if score #z vs_tmp matches 512.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-128
execute if score #z vs_tmp matches 512.. run scoreboard players remove #z vs_tmp 512
execute if score #z vs_tmp matches 256.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~64
execute if score #z vs_tmp matches 256.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-64
execute if score #z vs_tmp matches 256.. run scoreboard players remove #z vs_tmp 256
execute if score #z vs_tmp matches 128.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~32
execute if score #z vs_tmp matches 128.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-32
execute if score #z vs_tmp matches 128.. run scoreboard players remove #z vs_tmp 128
execute if score #z vs_tmp matches 64.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~16
execute if score #z vs_tmp matches 64.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-16
execute if score #z vs_tmp matches 64.. run scoreboard players remove #z vs_tmp 64
execute if score #z vs_tmp matches 32.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~8
execute if score #z vs_tmp matches 32.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-8
execute if score #z vs_tmp matches 32.. run scoreboard players remove #z vs_tmp 32
execute if score #z vs_tmp matches 16.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~4
execute if score #z vs_tmp matches 16.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-4
execute if score #z vs_tmp matches 16.. run scoreboard players remove #z vs_tmp 16
execute if score #z vs_tmp matches 8.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~2
execute if score #z vs_tmp matches 8.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-2
execute if score #z vs_tmp matches 8.. run scoreboard players remove #z vs_tmp 8
execute if score #z vs_tmp matches 4.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~1
execute if score #z vs_tmp matches 4.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-1
execute if score #z vs_tmp matches 4.. run scoreboard players remove #z vs_tmp 4
execute if score #z vs_tmp matches 2.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~0.5
execute if score #z vs_tmp matches 2.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-0.5
execute if score #z vs_tmp matches 2.. run scoreboard players remove #z vs_tmp 2
execute if score #z vs_tmp matches 1.. if score #zn vs_tmp matches 0 run tp @s ~ ~ ~0.25
execute if score #z vs_tmp matches 1.. if score #zn vs_tmp matches 1 run tp @s ~ ~ ~-0.25
execute if score #z vs_tmp matches 1.. run scoreboard players remove #z vs_tmp 1
execute if score #y vs_tmp matches 2048.. run tp @s ~ ~512 ~
execute if score #y vs_tmp matches 2048.. run scoreboard players remove #y vs_tmp 2048
execute if score #y vs_tmp matches 1024.. run tp @s ~ ~256 ~
execute if score #y vs_tmp matches 1024.. run scoreboard players remove #y vs_tmp 1024
execute if score #y vs_tmp matches 512.. run tp @s ~ ~128 ~
execute if score #y vs_tmp matches 512.. run scoreboard players remove #y vs_tmp 512
execute if score #y vs_tmp matches 256.. run tp @s ~ ~64 ~
execute if score #y vs_tmp matches 256.. run scoreboard players remove #y vs_tmp 256
execute if score #y vs_tmp matches 128.. run tp @s ~ ~32 ~
execute if score #y vs_tmp matches 128.. run scoreboard players remove #y vs_tmp 128
execute if score #y vs_tmp matches 64.. run tp @s ~ ~16 ~
execute if score #y vs_tmp matches 64.. run scoreboard players remove #y vs_tmp 64
execute if score #y vs_tmp matches 32.. run tp @s ~ ~8 ~
execute if score #y vs_tmp matches 32.. run scoreboard players remove #y vs_tmp 32
execute if score #y vs_tmp matches 16.. run tp @s ~ ~4 ~
execute if score #y vs_tmp matches 16.. run scoreboard players remove #y vs_tmp 16
execute if score #y vs_tmp matches 8.. run tp @s ~ ~2 ~
execute if score #y vs_tmp matches 8.. run scoreboard players remove #y vs_tmp 8
execute if score #y vs_tmp matches 4.. run tp @s ~ ~1 ~
execute if score #y vs_tmp matches 4.. run scoreboard players remove #y vs_tmp 4
execute if score #y vs_tmp matches 2.. run tp @s ~ ~0.5 ~
execute if score #y vs_tmp matches 2.. run scoreboard players remove #y vs_tmp 2
execute if score #y vs_tmp matches 1.. run tp @s ~ ~0.25 ~
execute if score #y vs_tmp matches 1.. run scoreboard players remove #y vs_tmp 1
effect give @s minecraft:slow_falling 6 0 true
effect give @s minecraft:resistance 4 4 true
particle minecraft:reverse_portal ~ ~1 ~ 0.4 0.8 0.4 0.1 60
playsound minecraft:entity.enderman.teleport player @a ~ ~ ~ 1 0.7
