// priority: 500
// Sound and a particle burst at the centre when the domain opens and closes.
(function () {
  global.OrderTest.component('sounds', {
    defaults: {
      openSound: 'minecraft:block.end_portal.spawn',
      closeSound: 'minecraft:block.beacon.deactivate',
      volume: 1.5,
      pitch: 0.6,
      hearingRange: 64,
      burst: 'minecraft:reverse_portal',
      burstSpread: '3 2 3',
      burstSpeed: 0.2,
      openBurstCount: 400,
      closeBurstCount: 200
    },
    open: function (ctx) { play(ctx, ctx.options.openSound, ctx.options.openBurstCount) },
    close: function (ctx) { play(ctx, ctx.options.closeSound, ctx.options.closeBurstCount) }
  })

  function play(ctx, sound, count) {
    const o = ctx.options
    ctx.runAtCenter('playsound ' + sound + ' master @a[distance=..' + o.hearingRange + '] ~ ~ ~ ' + o.volume + ' ' + o.pitch)
    ctx.runAtCenter('particle ' + o.burst + ' ~ ~1 ~ ' + o.burstSpread + ' ' + o.burstSpeed + ' ' + count + ' force')
  }
})()
