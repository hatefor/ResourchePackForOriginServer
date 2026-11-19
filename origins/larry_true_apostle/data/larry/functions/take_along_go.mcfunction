execute as @a[tag=larry_carry] at @s run function larry:guest_mark
function larry:enter_realm
execute if predicate larry:in_realm as @e[tag=larry_carry] in larry:realm run function larry:carry_one
