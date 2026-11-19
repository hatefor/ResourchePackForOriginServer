scoreboard players set #found morgan_rng 1
effect give @e[dx=0,dy=0,dz=0,tag=!morgan_self,type=!minecraft:item,type=!minecraft:marker,type=!minecraft:area_effect_cloud,type=!minecraft:experience_orb,sort=nearest,limit=1] minecraft:wither 10 1
particle minecraft:smoke ~ ~ ~ 0.3 0.5 0.3 0.05 30 force
playsound minecraft:entity.wither.ambient master @a ~ ~ ~ 0.6 1.4
