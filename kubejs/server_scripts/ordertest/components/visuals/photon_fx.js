// priority: 500
// Plays Photon effects (resourcepack/assets/<ns>/fx/<name>.fx, sent to players in the server resource pack).
// Every option is an effect id like 'ordertest:domain_open', or null to skip it.
//   open / close        once at the centre        loop        at the centre while open, removed on close
//   enter / exit        once on a member          memberLoop  on members while inside, removed on exit
(function () {
  global.OrderTest.component('photon_fx', {
    defaults: {
      open: null,
      loop: null,
      close: null,
      enter: null,
      memberLoop: null,
      exit: null,
      target: 'all',
      centreOffset: [0, 0, 0],
      memberOffset: [0, 1, 0],
      rotation: [0, 0, 0],
      // The radius-15 default domain is scale 1; effects grow with the domain unless scaleWithRadius is off.
      scale: 1,
      scaleWithRadius: true,
      baseRadius: 15
    },
    open: function (ctx) {
      atCentre(ctx, ctx.options.open)
      atCentre(ctx, ctx.options.loop)
    },
    close: function (ctx) {
      const o = ctx.options
      if (o.loop) ctx.run('execute in ' + ctx.dim + ' run photon fx remove block ' + blockPos(ctx) + ' true ' + o.loop)
      atCentre(ctx, o.close)
    },
    enter: function (ctx, entity) {
      if (!applies(ctx, entity)) return
      onEntity(ctx, entity, ctx.options.enter)
      onEntity(ctx, entity, ctx.options.memberLoop)
    },
    exit: function (ctx, entity) {
      const o = ctx.options
      if (!applies(ctx, entity)) return
      if (o.memberLoop) ctx.run('photon fx remove entity ' + ctx.uuid(entity) + ' true ' + o.memberLoop)
      onEntity(ctx, entity, o.exit)
    }
  })

  function scaleOf(ctx) {
    const o = ctx.options
    const s = o.scaleWithRadius ? o.scale * ctx.radius / o.baseRadius : o.scale
    return ctx.fmt(s) + ' ' + ctx.fmt(s) + ' ' + ctx.fmt(s)
  }

  function vec(ctx, v) { return ctx.fmt(v[0]) + ' ' + ctx.fmt(v[1]) + ' ' + ctx.fmt(v[2]) }

  function blockPos(ctx) { return Math.floor(ctx.x) + ' ' + Math.floor(ctx.y) + ' ' + Math.floor(ctx.z) }

  // Photon places block effects at a block; the offset carries the centre's position inside that block.
  function atCentre(ctx, fx) {
    if (!fx) return
    const o = ctx.options
    const offset = [ctx.x - Math.floor(ctx.x) + o.centreOffset[0], ctx.y - Math.floor(ctx.y) + o.centreOffset[1],
      ctx.z - Math.floor(ctx.z) + o.centreOffset[2]]
    ctx.run('execute in ' + ctx.dim + ' run photon fx ' + fx + ' block ' + blockPos(ctx) + ' ' + vec(ctx, offset) + ' ' +
      vec(ctx, o.rotation) + ' ' + scaleOf(ctx) + ' 0 false true false')
  }

  function onEntity(ctx, entity, fx) {
    if (!fx) return
    const o = ctx.options
    ctx.run('photon fx ' + fx + ' entity ' + ctx.uuid(entity) + ' ' + vec(ctx, o.memberOffset) + ' ' + vec(ctx, o.rotation) +
      ' ' + ctx.fmt(o.scale) + ' ' + ctx.fmt(o.scale) + ' ' + ctx.fmt(o.scale) + ' 0 false true none')
  }

  function applies(ctx, entity) {
    const target = ctx.options.target
    if (target === 'all') return true
    return target === 'owner' ? ctx.isOwner(entity) : !ctx.isOwner(entity)
  }
})()
