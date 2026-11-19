// priority: 500
// Bridge to the datapack: runs the #ordertest:domain/<hook> function tags so mcfunction effects can plug in.
// open/close run as the owner (or the server) at the centre; enter/tick/exit run as and at each member.
(function () {
  global.OrderTest.component('mcfunction_hooks', {
    defaults: { tagPrefix: '#ordertest:domain/' },
    open: function (ctx) { atCenter(ctx, 'open') },
    close: function (ctx) { atCenter(ctx, 'close') },
    enter: function (ctx, entity) { ctx.runAs(entity, 'function ' + ctx.options.tagPrefix + 'enter') },
    memberTick: function (ctx, entity) { ctx.runAs(entity, 'function ' + ctx.options.tagPrefix + 'tick') },
    exit: function (ctx, entity) { ctx.runAs(entity, 'function ' + ctx.options.tagPrefix + 'exit') }
  })

  function atCenter(ctx, hook) {
    const owner = ctx.ownerEntity()
    const as = owner ? 'as ' + ctx.uuid(owner) + ' ' : ''
    ctx.run('execute ' + as + 'in ' + ctx.dim + ' positioned ' + ctx.fmt(ctx.x) + ' ' + ctx.fmt(ctx.y) + ' ' +
      ctx.fmt(ctx.z) + ' run function ' + ctx.options.tagPrefix + hook)
  }
})()
