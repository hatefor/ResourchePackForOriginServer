// priority: 500
// The visible wall: thin opaque block display panels spread evenly over the sphere, each facing the centre, so
// nobody can see in or out. It builds from the bottom up when the domain opens and is removed when it closes.
// An overlap of 1.5 or more leaves no gaps from any viewpoint (checked by ray casting the layout); panels sit at
// three slightly different depths so overlapping ones don't flicker.
(function () {
  // Rhino leaves the Math constants (PI, E) undefined; acos(-1) is pi everywhere.
  const PI = Math.acos(-1)
  const SHELL_TAG = 'ot_shell'
  const SHELL_ID_PREFIX = 'ot_shell_'
  const GOLDEN_ANGLE = PI * (3 - Math.sqrt(5))
  const SWEEP_EVERY_TICKS = 200

  global.OrderTest.component('display_shell', {
    defaults: {
      block: 'minecraft:black_concrete',
      spacing: 2.5,
      overlap: 1.6,
      thickness: 0.05,
      depthLayers: 3,
      depthStep: 0.02,
      buildTicks: 20,
      fullBright: true,
      viewRange: 2.0
    },
    tick: function (ctx) {
      const o = ctx.options
      const s = ctx.store
      if (s.total === undefined) {
        s.total = Math.max(1, Math.ceil(4 * PI * ctx.radius * ctx.radius / (o.spacing * o.spacing)))
        s.built = 0
      }
      if (s.built >= s.total) return
      const batch = Math.ceil(s.total / Math.max(1, o.buildTicks))
      const panel = Math.sqrt(4 * PI * ctx.radius * ctx.radius / s.total) * o.overlap
      for (let n = 0; n < batch && s.built < s.total; n++) {
        spawnPanel(ctx, o, s.total - 1 - s.built, s.total, panel)
        s.built++
      }
    },
    close: function (ctx) {
      ctx.run('kill @e[type=minecraft:block_display,tag=' + SHELL_ID_PREFIX + ctx.id + ']')
    }
  })

  // Point i of n on a Fibonacci sphere; i = n - 1 is the bottom, so the dome rises as it builds.
  function spawnPanel(ctx, o, i, n, size) {
    const y = 1 - 2 * (i + 0.5) / n
    const ring = Math.sqrt(1 - y * y)
    const theta = GOLDEN_ANGLE * i
    const dx = Math.cos(theta) * ring
    const dz = Math.sin(theta) * ring
    const yaw = Math.atan2(-dx, dz) * 180 / PI
    const pitch = -Math.asin(y) * 180 / PI
    const half = size / 2
    const r = ctx.radius + (i % Math.max(1, o.depthLayers)) * o.depthStep
    const nbt = '{Tags:["' + SHELL_TAG + '","' + SHELL_ID_PREFIX + ctx.id + '"],Rotation:[' + ctx.fmt(yaw) + 'f,' +
      ctx.fmt(pitch) + 'f],block_state:{Name:"' + o.block + '"},transformation:{left_rotation:[0f,0f,0f,1f],' +
      'right_rotation:[0f,0f,0f,1f],translation:[' + ctx.fmt(-half) + 'f,' + ctx.fmt(-half) + 'f,0f],scale:[' +
      ctx.fmt(size) + 'f,' + ctx.fmt(size) + 'f,' + ctx.fmt(o.thickness) + 'f]},view_range:' + ctx.fmt(o.viewRange) + 'f' +
      (o.fullBright ? ',brightness:{sky:15,block:15}' : '') + '}'
    ctx.run('execute in ' + ctx.dim + ' run summon minecraft:block_display ' + ctx.fmt(ctx.x + dx * r) + ' ' +
      ctx.fmt(ctx.y + y * r) + ' ' + ctx.fmt(ctx.z + dz * r) + ' ' + nbt)
  }

  // Panels outlive their domain after a restart or when their chunk was unloaded at close; remove any whose
  // domain is no longer open.
  ServerEvents.tick(event => {
    if (event.server.getTickCount() % SWEEP_EVERY_TICKS !== 0) return
    const active = global.OrderTestState.active
    let selector = '@e[type=minecraft:block_display,tag=' + SHELL_TAG
    Object.keys(active).forEach(id => { selector += ',tag=!' + SHELL_ID_PREFIX + id })
    event.server.runCommandSilent('kill ' + selector + ']')
  })
})()
