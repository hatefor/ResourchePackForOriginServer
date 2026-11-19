// priority: 500
// Who is caught when the domain opens: every player and living mob within the radius.
(function () {
  global.OrderTest.component('catch_radius', {
    defaults: {
      players: true,
      mobs: true,
      excludeTypes: ['minecraft:armor_stand']
    },
    open: function (ctx) {
      const o = ctx.options
      ctx.entitiesWithin(ctx.radius).forEach(entity => {
        if (entity.isPlayer()) {
          if (o.players && !entity.isSpectator()) ctx.addMember(entity)
          return
        }
        if (!o.mobs || !entity.isLiving()) return
        if (o.excludeTypes.indexOf(String(entity.getEncodeId())) >= 0) return
        ctx.addMember(entity)
      })
    }
  })
})()
