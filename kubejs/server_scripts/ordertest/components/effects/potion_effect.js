// priority: 500
// Keeps a potion effect on members while they are inside. target: 'others', 'owner' or 'all'.
// The effect is short and refreshed, so it lapses on its own after leaving. clearOnExit also removes the same
// effect from any other source, so it is off by default.
(function () {
  global.OrderTest.component('potion_effect', {
    defaults: {
      effect: 'minecraft:slowness',
      amplifier: 0,
      target: 'others',
      everyTicks: 20,
      extraSeconds: 1,
      hideParticles: true,
      clearOnExit: false
    },
    memberTick: function (ctx, entity) {
      const o = ctx.options
      if ((ctx.age - 1) % Math.max(1, o.everyTicks) !== 0) return
      if (!entity.isLiving() || !matchesTarget(ctx, entity, o.target)) return
      const seconds = Math.ceil(o.everyTicks / 20) + o.extraSeconds
      ctx.run('effect give ' + ctx.uuid(entity) + ' ' + o.effect + ' ' + seconds + ' ' + o.amplifier + ' ' + o.hideParticles)
    },
    exit: function (ctx, entity) {
      const o = ctx.options
      if (o.clearOnExit && entity.isLiving() && matchesTarget(ctx, entity, o.target)) {
        ctx.run('effect clear ' + ctx.uuid(entity) + ' ' + o.effect)
      }
    }
  })

  function matchesTarget(ctx, entity, target) {
    if (target === 'all') return true
    return target === 'owner' ? ctx.isOwner(entity) : !ctx.isOwner(entity)
  }
})()
