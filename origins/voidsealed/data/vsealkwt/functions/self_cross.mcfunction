scoreboard players set @s vs_ok 1
execute if score #mode vs_tmp matches 1 run function vsealkwt:go_end
execute if score #mode vs_tmp matches 2 run function vsealkwt:return_home
