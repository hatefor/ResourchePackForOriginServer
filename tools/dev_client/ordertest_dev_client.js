// Dev client only: copied into run/kubejs/client_scripts by `tools/testserver.py client-world`, never shipped.
// When run/kubejs/config/ordertest_dev.json exists (gradlew runClient -PquitAfter/-PjoinTimeout/-PdevCommands),
// it runs the given steps after joining (a /command, a chat line, "!wait <ticks>" or "!screenshot"), quits a set
// time after joining, and quits if the world is never reached. A plain runClient has no config file and stays open.
(function () {
  const CONFIG = 'kubejs/config/ordertest_dev.json'
  const TICKS_PER_SECOND = 20
  const FIRST_COMMAND_DELAY = 2 * TICKS_PER_SECOND
  const COMMAND_SPACING = 10

  let config = null
  try { config = JsonIO.read(CONFIG) } catch (ignored) { config = null }
  if (!config) return

  const joinTimeout = Number(config.joinTimeoutSeconds || 0) * TICKS_PER_SECOND
  const quitAfter = Number(config.quitAfterSeconds || 0) * TICKS_PER_SECOND
  const commands = []
  if (config.commands) config.commands.forEach(line => commands.push(String(line)))
  let ticks = 0
  let joinedAt = -1
  let sent = 0
  let nextAt = FIRST_COMMAND_DELAY
  let quitting = false

  // Writes Photon's own serialization of real emitters to run/photon_dump/, the ground truth tools/photon builds on.
  function photonDump() {
    const photon = 'com.lowdragmc.photon.client.'
    const FX = Java.loadClass(photon + 'fx.FX')
    const ParticleEmitter = Java.loadClass(photon + 'gameobject.emitter.particle.ParticleEmitter')
    const CompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag')
    const NumberFunction = Java.loadClass(photon + 'gameobject.emitter.data.number.NumberFunction')
    const Burst = Java.loadClass(photon + 'gameobject.emitter.data.EmissionSetting$Burst')
    const shapes = ['Sphere', 'Function', 'Circle', 'Box', 'Dot', 'Cylinder', 'Cone']
    const modules = ['lights', 'velocityOverLifetime', 'inheritVelocity', 'lifetimeByEmitterSpeed', 'forceOverLifetime',
      'colorOverLifetime', 'colorBySpeed', 'sizeOverLifetime', 'sizeBySpeed', 'rotationOverLifetime', 'rotationBySpeed',
      'noise', 'uvAnimation', 'trails', 'subEmitters', 'physics']
    const save = (name, objects) => {
      const fx = new FX()
      objects.forEach(o => fx.getMainFX().objects().add(o))
      const tag = new CompoundTag()
      tag.put('fx', fx.serializeNBT())
      tag.putInt('_version', 1)
      NBTIO.write('photon_dump/' + name + '.fx', tag)
      console.info('[ordertest-dev] photon dump ' + name)
    }
    save('particle_default', [new ParticleEmitter()])
    const all = new ParticleEmitter()
    modules.forEach(m => {
      try { all.config[m].setEnable(true) } catch (e) { console.warn('[ordertest-dev] no toggle ' + m + ': ' + e) }
    })
    save('particle_all_modules', [all])
    const burst = new ParticleEmitter()
    burst.config.emission.setEmissionRate(NumberFunction.constant(0))
    burst.config.emission.getBursts().add(new Burst())
    save('particle_burst', [burst])
    shapes.forEach(s => {
      const e = new ParticleEmitter()
      e.config.shape.setShape(new (Java.loadClass(photon + 'gameobject.emitter.data.shape.' + s))())
      save('shape_' + s.toLowerCase(), [e])
    })
    ;['beam.BeamEmitter', 'trail.TrailEmitter'].forEach(c => {
      try { save(c.split('.')[1].toLowerCase(), [new (Java.loadClass(photon + 'gameobject.emitter.' + c))()]) } catch (e) {
        console.warn('[ordertest-dev] could not dump ' + c + ': ' + e)
      }
    })
  }

  // Saves to run/screenshots/ so a scripted run can be checked by eye afterwards.
  function screenshot() {
    const Screenshot = Java.loadClass('net.minecraft.client.Screenshot')
    Screenshot.grab(Client.gameDirectory, Client.getMainRenderTarget(),
      message => console.info('[ordertest-dev] screenshot: ' + message.getString()))
  }

  function quit(reason) {
    if (quitting) return
    quitting = true
    console.info('[ordertest-dev] ' + reason)
    Client.stop()
  }

  ClientEvents.loggedIn(event => {
    if (joinedAt >= 0) return
    joinedAt = ticks
    console.info('[ordertest-dev] joined the world')
  })

  ClientEvents.tick(event => {
    ticks++
    if (joinedAt < 0) {
      if (joinTimeout > 0 && ticks > joinTimeout) quit('never reached the world within ' + config.joinTimeoutSeconds + ' s, quitting')
      return
    }
    const since = ticks - joinedAt
    if (sent < commands.length && since >= nextAt && Client.player) {
      const line = commands[sent++]
      nextAt = since + COMMAND_SPACING
      console.info('[ordertest-dev] step ' + line)
      if (line.indexOf('!wait ') === 0) nextAt = since + Number(line.substring(6))
      else if (line === '!screenshot') screenshot()
      else if (line === '!photon_dump') photonDump()
      else if (line.charAt(0) === '/') Client.player.connection.sendCommand(line.substring(1))
      else Client.player.connection.sendChat(line)
    }
    if (quitAfter > 0 && since > quitAfter) quit('quitting ' + config.quitAfterSeconds + ' s after joining')
  })
})()
