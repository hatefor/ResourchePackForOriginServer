execute rotated ~ 0 positioned ^ ^ ^12 run summon marker ~ ~ ~ {Tags:["kk_bolt"]}
execute rotated ~ 0 positioned ^ ^ ^12 run particle minecraft:electric_spark ~ ~0.2 ~ 1 0.1 1 0.1 60
playsound minecraft:block.beacon.charge player @a ~ ~ ~ 1 2
schedule function kittyknight:bolt_warn 10t append
schedule function kittyknight:bolt_strike 20t append
