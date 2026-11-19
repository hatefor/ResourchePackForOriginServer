execute in minecraft:overworld run spreadplayers 0 0 1 32 false @s
execute unless predicate vsealkwt:in_overworld in minecraft:overworld run tp @s 0.5 100 0.5
effect give @s minecraft:slow_falling 6 0 true
effect give @s minecraft:resistance 4 4 true
title @s actionbar {"text":"No saved spot to return to, so the void drops you near the world spawn","color":"gray","italic":true}
