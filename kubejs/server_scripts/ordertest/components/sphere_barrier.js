// priority: 500
// The wall: members can't leave, nobody else can enter, and nothing is shot through it.
(function () {
  global.OrderTest.component('sphere_barrier', {
    defaults: {
      pullBackTo: 1.5,
      pushOutTo: 1,
      wallThickness: 0.5,
      lostDistance: 8,
      pushMobs: true,
      projectileBand: 1.5,
      // Fastest projectile step per tick to look for; crossbow bolts move about 3.2 blocks.
      maxProjectileStep: 5,
      destroyProjectiles: ['minecraft:snowball', 'minecraft:egg', 'minecraft:ender_pearl', 'minecraft:fireball',
        'minecraft:small_fireball', 'minecraft:dragon_fireball', 'minecraft:wither_skull', 'minecraft:potion',
        'minecraft:experience_bottle', 'minecraft:llama_spit', 'minecraft:shulker_bullet', 'minecraft:firework_rocket',
        'minecraft:fishing_bobber'],
      stopProjectiles: ['minecraft:arrow', 'minecraft:spectral_arrow', 'minecraft:trident'],
      ignoreTypes: ['minecraft:armor_stand', 'minecraft:marker', 'minecraft:item', 'minecraft:experience_orb']
    },
    tick: function (ctx) {
      const o = ctx.options
      const r = ctx.radius
      const pullBackTo = Math.min(Math.max(o.pullBackTo, o.wallThickness + 0.5), r / 2)
      ctx.members().forEach(entity => {
        if (!ctx.inSameDimension(entity) || ctx.distance(entity) > r + o.lostDistance) {
          ctx.teleport(entity, ctx.x, ctx.y, ctx.z)
        } else if (ctx.distance(entity) > r - o.wallThickness) {
          ctx.placeAtDistance(entity, r - pullBackTo)
        }
      })
      ctx.entitiesWithin(r + o.projectileBand + o.maxProjectileStep).forEach(entity => {
        if (ctx.isMember(entity)) return
        const type = String(entity.getEncodeId())
        const destroy = o.destroyProjectiles.indexOf(type) >= 0
        if (destroy || o.stopProjectiles.indexOf(type) >= 0) {
          if (!meetsWall(ctx, entity, o.projectileBand)) return
          if (destroy) entity.discard()
          else { entity.setMotionX(0); entity.setMotionY(0); entity.setMotionZ(0) }
          return
        }
        if (ctx.distance(entity) > r || o.ignoreTypes.indexOf(type) >= 0) return
        if (entity.isPlayer()) {
          if (!entity.isSpectator()) ctx.placeAtDistance(entity, r + o.pushOutTo)
        } else if (o.pushMobs && entity.isLiving()) {
          ctx.placeAtDistance(entity, r + o.pushOutTo)
        }
      })
    }
  })

  // True when a projectile is in the wall now or its next step crosses or lands in it, so fast shots can't
  // jump the wall between two ticks.
  function meetsWall(ctx, entity, band) {
    const r = ctx.radius
    const now = ctx.distance(entity)
    const next = ctx.distanceTo(entity.getX() + entity.motionX, entity.getY() + entity.motionY, entity.getZ() + entity.motionZ)
    const inBand = d => d >= r - band && d <= r + band
    return inBand(now) || inBand(next) || (now < r) !== (next < r)
  }
})()
