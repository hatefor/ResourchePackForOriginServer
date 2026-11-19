execute if score @s vs_kind matches 1 if predicate vsealkwt:in_end run function vsealkwt:return_home
execute if score @s vs_kind matches 2 unless predicate vsealkwt:in_end run function vsealkwt:to_end
scoreboard players set @s vs_kind 0
title @s actionbar {"text":"The void lets go of you","color":"dark_purple","italic":true}
