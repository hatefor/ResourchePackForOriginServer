particle minecraft:portal ~ ~1 ~ 0.4 0.8 0.4 0.1 60
execute in minecraft:the_end run spreadplayers 0 0 1 14 false @s
execute unless predicate vsealkwt:in_end in minecraft:the_end run tp @s 0.5 80 0.5
effect give @s minecraft:slow_falling 6 0 true
effect give @s minecraft:resistance 4 4 true
particle minecraft:portal ~ ~1 ~ 0.4 0.8 0.4 0.1 60
playsound minecraft:entity.enderman.teleport player @a ~ ~ ~ 1 0.7
