scoreboard players set #clock larry_clock 0
execute as @a[tag=larry_guest] at @s if predicate larry:in_realm run effect give @s minecraft:weakness 3 0 true
execute as @a[tag=larry_guest] at @s if predicate larry:in_realm run effect give @s minecraft:darkness 6 0 true
execute as @a[tag=larry_guest] at @s unless predicate larry:in_realm run tag @s remove larry_guest
