execute anchored eyes positioned ^ ^ ^1.5 run summon marker ~ ~ ~ {Tags:["kk_orb","kk_new"]}
execute anchored eyes positioned ^ ^ ^1.5 run tp @e[type=marker,tag=kk_new,limit=1,sort=nearest] ~ ~ ~ ~ ~
tag @e[type=marker,tag=kk_new] remove kk_new
playsound minecraft:entity.evoker.cast_spell player @a ~ ~ ~ 1 2
