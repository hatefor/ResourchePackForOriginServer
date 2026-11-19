// priority: 500
// A sweeping particle dome: meridians of the sphere rotate around the centre.
(function () {
  // Rhino leaves the Math constants (PI, E) undefined; acos(-1) is pi everywhere.
  const PI = Math.acos(-1)

  global.OrderTest.component('meridian_particles', {
    defaults: {
      particle: 'minecraft:dust 0.2 0.0 0.3 2.5',
      meridians: 4,
      pitches: [-80, -55, -30, -10, 10],
      degreesPerTick: 6,
      spread: '0 0 0',
      speed: 0,
      countPerPoint: 1,
      // 'force' ignores players' particle setting and widens the send radius from 32 to 512 blocks.
      viewMode: 'normal'
    },
    tick: function (ctx) {
      const o = ctx.options
      const base = ctx.age * o.degreesPerTick
      // Rhino rejects a const declared inside a for loop body, so each meridian is its own call.
      for (let m = 0; m < o.meridians; m++) drawMeridian(ctx, o, (base + m * 360 / o.meridians) * PI / 180)
    }
  })

  function drawMeridian(ctx, o, yaw) {
    o.pitches.forEach(pitchDegrees => {
      const pitch = pitchDegrees * PI / 180
      const x = ctx.x - Math.sin(yaw) * Math.cos(pitch) * ctx.radius
      const y = ctx.y - Math.sin(pitch) * ctx.radius
      const z = ctx.z + Math.cos(yaw) * Math.cos(pitch) * ctx.radius
      ctx.run('execute in ' + ctx.dim + ' run particle ' + o.particle + ' ' + ctx.fmt(x) + ' ' + ctx.fmt(y) + ' ' +
        ctx.fmt(z) + ' ' + o.spread + ' ' + o.speed + ' ' + o.countPerPoint + ' ' + o.viewMode)
    })
  }
})()
