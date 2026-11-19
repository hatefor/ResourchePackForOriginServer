execute if predicate morgan:wood_tool run item modify entity @s weapon.mainhand morgan:wear_wood
execute if predicate morgan:stone_tool run item modify entity @s weapon.mainhand morgan:wear_stone
execute if predicate morgan:gold_tool run item modify entity @s weapon.mainhand morgan:wear_gold
execute if predicate morgan:iron_tool run item modify entity @s weapon.mainhand morgan:wear_iron
execute if predicate morgan:diamond_tool run item modify entity @s weapon.mainhand morgan:wear_diamond
execute if predicate morgan:netherite_tool run item modify entity @s weapon.mainhand morgan:wear_netherite
execute unless predicate morgan:known_tool run item modify entity @s weapon.mainhand morgan:extra_wear
