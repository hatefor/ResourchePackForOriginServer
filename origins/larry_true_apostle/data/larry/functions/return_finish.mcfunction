execute as @a[tag=larry_leaving] at @s if loaded ~ ~ ~ run function larry:return_place
execute as @a[tag=larry_leaving] run scoreboard players add @s larry_wait 1
execute as @a[tag=larry_leaving,scores={larry_wait=60..}] run function larry:return_timeout
execute if entity @a[tag=larry_leaving] run schedule function larry:return_finish 3t replace
