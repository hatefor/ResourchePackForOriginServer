// priority: 500
// Grants an Origins power to members while they are inside, under a source owned by this domain, so it never
// touches the same power granted any other way. target: 'others', 'owner' or 'all'.
(function () {
  global.OrderTest.component('origins_power', {
    defaults: { power: null, target: 'all' },
    enter: function (ctx, entity) {
      if (applies(ctx, entity)) ctx.run('power grant ' + ctx.uuid(entity) + ' ' + ctx.options.power + ' ' + ctx.powerSource)
    },
    exit: function (ctx, entity) {
      if (applies(ctx, entity)) ctx.run('power revoke ' + ctx.uuid(entity) + ' ' + ctx.options.power + ' ' + ctx.powerSource)
    }
  })

  function applies(ctx, entity) {
    const target = ctx.options.target
    if (!ctx.options.power || !entity.isLiving()) return false
    if (target === 'all') return true
    return target === 'owner' ? ctx.isOwner(entity) : !ctx.isOwner(entity)
  }
})()
