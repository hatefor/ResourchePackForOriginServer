scoreboard players add #clock larry_clock 1
execute as @a if predicate larry:in_realm run scoreboard players enable @s larry_leave
execute as @a[scores={larry_leave=1..}] run function larry:leave_self
execute if score #clock larry_clock matches 20.. run function larry:second
