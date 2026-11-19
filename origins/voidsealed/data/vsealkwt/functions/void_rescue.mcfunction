execute if predicate vsealkwt:in_end run function vsealkwt:to_end
execute unless predicate vsealkwt:in_end in minecraft:overworld run spreadplayers ~ ~ 1 100 false @s
execute unless predicate vsealkwt:in_end unless predicate vsealkwt:in_overworld run function vsealkwt:spawn_fallback
