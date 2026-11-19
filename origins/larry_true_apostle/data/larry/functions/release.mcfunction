tag @s add larry_src
execute as @a[tag=larry_guest,tag=!larry_src] at @s if predicate larry:in_realm run function larry:send_home
tag @s remove larry_src
