// priority: 500
// Shows the seconds left on the action bar of everyone inside.
(function () {
  global.OrderTest.component('countdown_actionbar', {
    defaults: { everyTicks: 10, color: 'gray' },
    tick: function (ctx) {
      const o = ctx.options
      if (ctx.ticksLeft <= 0 || ctx.age % o.everyTicks !== 0) return
      const seconds = Math.ceil(ctx.ticksLeft / 20)
      const text = JSON.stringify({ text: ctx.name + ' closes in ' + seconds + ' seconds.', color: o.color })
      ctx.members().forEach(entity => {
        if (entity.isPlayer()) ctx.run('title ' + ctx.uuid(entity) + ' actionbar ' + text)
      })
    },
    exit: function (ctx, entity) {
      if (entity.isPlayer()) ctx.run('title ' + ctx.uuid(entity) + ' actionbar ""')
    }
  })
})()
