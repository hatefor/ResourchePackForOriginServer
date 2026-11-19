// priority: 500
// Shows "Domain Expansion" and the domain's name to everyone caught when it opens.
(function () {
  global.OrderTest.component('announce_title', {
    defaults: {
      title: 'Domain Expansion',
      titleColor: 'gray',
      nameColor: 'dark_purple'
    },
    open: function (ctx) {
      const o = ctx.options
      const title = JSON.stringify({ text: o.title, color: o.titleColor })
      const subtitle = JSON.stringify({ text: ctx.name, color: o.nameColor, bold: true })
      ctx.members().forEach(entity => {
        if (!entity.isPlayer()) return
        ctx.run('title ' + ctx.uuid(entity) + ' subtitle ' + subtitle)
        ctx.run('title ' + ctx.uuid(entity) + ' title ' + title)
      })
    }
  })
})()
