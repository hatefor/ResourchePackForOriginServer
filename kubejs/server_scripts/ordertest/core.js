// priority: 1000
// Order test domain engine. A domain is a list of components; every behaviour (who is caught, the wall,
// visuals, effects) is a component registered with OrderTest.component and can be swapped by dropping in
// a script. Running domains are plain data in global.OrderTestState, so /reload replaces the code under
// them without closing anything.
(function () {
  const UUIDClass = Java.loadClass('java.util.UUID')

  const KEY_NAME = 'ordertest_domain_name'
  const KEY_MEMBER_OF = 'ordertest_member_of'
  const KEY_COOLDOWNS = 'ordertest_cooldowns'
  const KEY_NEXT_ID = 'ordertest_next_id'
  const TAG_INSIDE = 'ot_inside'
  const TAG_OWNER = 'ot_domain_owner'
  const TAG_NAME_PREFIX = 'ot_in_'
  const POWER_SOURCE_PREFIX = 'ordertest:domain_'
  const ADMIN_PERMISSION = 2
  const TICKS_PER_SECOND = 20
  const MS_PER_SECOND = 1000
  const CAST_PHRASE = /^\s*domain\s+expansion[\s:,!.-]+(.+)$/i
  const TRAILING_PUNCTUATION = /[\s.!?]+$/
  const DEFAULT_NAME = 'Domain'
  const COORDINATE_DECIMALS = 3

  const DEFAULTS = {
    radius: 15,
    duration: 30,
    cooldown: 60,
    gap: 2,
    components: [
      'catch_radius',
      'sphere_barrier',
      'display_shell',
      'meridian_particles',
      'announce_title',
      'countdown_actionbar',
      'sounds',
      'mcfunction_hooks'
    ]
  }

  if (!global.OrderTestState) global.OrderTestState = { active: {} }
  const state = global.OrderTestState
  const warned = {}

  const api = {
    defaults: DEFAULTS,
    components: {},
    domains: {},
    powers: {},
    origins: {},
    state: state,
    tags: { inside: TAG_INSIDE, owner: TAG_OWNER, namePrefix: TAG_NAME_PREFIX },
    component: function (id, spec) { api.components[id] = spec },
    domain: function (name, spec) { api.domains[keyOf(name)] = Object.assign({ name: name }, spec) },
    power: function (id, json) { api.powers[id] = json },
    origin: function (id, spec) { api.origins[id] = spec },
    open: function (server, caster, name) { return openDomain(server, caster, name) },
    close: function (server, domain) { closeDomain(server, domain) },
    domainOf: function (entity) { return domainOf(entity) },
    ownedBy: function (entity) { return ownedBy(entity) },
    contextFor: function (server, domain) { return makeContext(server, domain) },
    registeredName: function (player) { return registeredName(player) },
    slug: function (name) { return slugOf(name) },
    fmt: function (number) { return fmt(number) }
  }
  global.OrderTest = api

  function keyOf(name) { return String(name).replace(TRAILING_PUNCTUATION, '').trim().toLowerCase() }

  function slugOf(name) {
    const key = keyOf(name)
    const slug = key.replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '')
    if (slug) return slug
    let hash = 0
    for (let i = 0; i < key.length; i++) hash = (hash * 31 + key.charCodeAt(i)) % 1000000007
    return key.length ? 'u' + hash : 'domain'
  }

  // Commands reject exponent notation, which a plain number can print near zero. NaN would make the command
  // fail silently, so it throws and callAll names the component that produced it.
  function fmt(number) {
    const value = Number(number)
    if (!isFinite(value)) throw new Error('not a finite number: ' + number)
    return value.toFixed(COORDINATE_DECIMALS)
  }

  // KubeJS renames UUID getters: getStringUUID() is stringUuid, getUUID() is getUuid().
  function uuidOf(entity) { return String(entity.stringUuid) }

  function dimensionOf(entity) { return String(entity.level.getDimension()) }

  function warnOnce(key, message) {
    if (warned[key]) return
    warned[key] = true
    console.warn('[ordertest] ' + message)
  }

  function registeredName(player) {
    const name = String(player.persistentData.getString(KEY_NAME))
    return name.length > 0 ? name : null
  }

  function domainOf(entity) {
    const uuid = uuidOf(entity)
    let found = null
    Object.keys(state.active).forEach(id => {
      if (state.active[id].members.indexOf(uuid) >= 0) found = state.active[id]
    })
    return found
  }

  function ownedBy(entity) {
    const uuid = uuidOf(entity)
    let found = null
    Object.keys(state.active).forEach(id => { if (state.active[id].owner === uuid) found = state.active[id] })
    return found
  }

  function findEntity(server, uuid) {
    const id = UUIDClass.fromString(uuid)
    const player = server.getPlayerList().getPlayer(id)
    if (player) return player
    let found = null
    server.getAllLevels().forEach(level => {
      if (!found) {
        const entity = level.getEntity(id)
        if (entity) found = entity
      }
    })
    return found
  }

  function nextDomainId(server) {
    const id = Math.max(1, server.persistentData.getInt(KEY_NEXT_ID))
    server.persistentData.putInt(KEY_NEXT_ID, id + 1)
    return id
  }

  function cooldownSecondsLeft(server, uuid) {
    const until = server.persistentData.getCompound(KEY_COOLDOWNS).getLong(uuid)
    const left = until - Date.now()
    return left > 0 ? Math.ceil(left / MS_PER_SECOND) : 0
  }

  function setCooldown(server, uuid, seconds) {
    const cooldowns = server.persistentData.getCompound(KEY_COOLDOWNS)
    if (seconds > 0) cooldowns.putLong(uuid, Date.now() + seconds * MS_PER_SECOND)
    else cooldowns.remove(uuid)
    server.persistentData.put(KEY_COOLDOWNS, cooldowns)
  }

  function resolveComponents(custom) {
    const removed = custom.removeComponents || []
    const list = (custom.components || DEFAULTS.components).concat(custom.extraComponents || [])
    const overrides = custom.options || {}
    const resolved = []
    list.forEach(entry => {
      const id = typeof entry === 'string' ? entry : entry[0]
      if (removed.indexOf(id) >= 0) return
      const component = api.components[id]
      if (!component) {
        warnOnce('missing:' + id, 'Domain "' + custom.name + '" uses unknown component ' + id)
        return
      }
      const options = Object.assign({}, component.defaults || {}, overrides[id] || {},
        typeof entry === 'string' ? {} : (entry[1] || {}))
      resolved.push({ id: id, options: options })
    })
    return resolved
  }

  function resolveSpec(name) {
    const custom = api.domains[keyOf(name)] || { name: name }
    return {
      name: custom.name,
      radius: custom.radius || DEFAULTS.radius,
      duration: custom.duration || DEFAULTS.duration,
      cooldown: custom.cooldown === undefined ? DEFAULTS.cooldown : custom.cooldown,
      components: resolveComponents(custom)
    }
  }

  // One broken component is logged and skipped so the others, and cleanup, still run.
  function callAll(server, domain, hook, ctx, entity) {
    domain.components.forEach(entry => {
      const component = api.components[entry.id]
      if (!component) {
        warnOnce('gone:' + entry.id, 'Component ' + entry.id + ' was removed while a domain used it')
        return
      }
      if (!component[hook]) return
      ctx.options = entry.options
      ctx.store = domain.data[entry.id] || (domain.data[entry.id] = {})
      try {
        component[hook](ctx, entity)
      } catch (error) {
        warnOnce('threw:' + entry.id + ':' + hook, 'Component ' + entry.id + ' failed in ' + hook + ' of domain ' +
          domain.name + ': ' + error)
      }
    })
  }

  function makeContext(server, domain) {
    const level = server.getLevel(domain.dim)
    let memberCache = null
    const ctx = {
      id: domain.id,
      name: domain.name,
      slug: domain.slug,
      owner: domain.owner,
      dim: domain.dim,
      x: domain.x,
      y: domain.y,
      z: domain.z,
      radius: domain.radius,
      age: domain.age,
      ticksLeft: domain.ticksLeft,
      durationTicks: domain.durationTicks,
      server: server,
      level: level,
      options: {},
      store: {},
      nameTag: TAG_NAME_PREFIX + domain.slug,
      powerSource: POWER_SOURCE_PREFIX + domain.id,
      uuid: uuidOf,
      fmt: fmt,
      run: function (command) { return server.runCommandSilent(command) },
      runAtCenter: function (command) {
        return server.runCommandSilent('execute in ' + domain.dim + ' positioned ' + fmt(domain.x) + ' ' + fmt(domain.y) +
          ' ' + fmt(domain.z) + ' run ' + command)
      },
      runAs: function (entity, command) {
        return server.runCommandSilent('execute as ' + uuidOf(entity) + ' at @s run ' + command)
      },
      ownerEntity: function () { return domain.owner ? findEntity(server, domain.owner) : null },
      isOwner: function (entity) { return uuidOf(entity) === domain.owner },
      isMember: function (entity) { return domain.members.indexOf(uuidOf(entity)) >= 0 },
      inSameDimension: function (entity) { return dimensionOf(entity) === domain.dim },
      distanceTo: function (x, y, z) {
        const dx = x - domain.x, dy = y - domain.y, dz = z - domain.z
        return Math.sqrt(dx * dx + dy * dy + dz * dz)
      },
      distance: function (entity) { return ctx.distanceTo(entity.getX(), entity.getY(), entity.getZ()) },
      entitiesWithin: function (range) {
        const box = AABB.of(domain.x - range, domain.y - range, domain.z - range,
          domain.x + range, domain.y + range, domain.z + range)
        const result = []
        level.getEntitiesWithin(box).forEach(entity => { if (ctx.distance(entity) <= range) result.push(entity) })
        return result
      },
      teleport: function (entity, x, y, z) {
        server.runCommandSilent('execute in ' + domain.dim + ' run tp ' + uuidOf(entity) + ' ' + fmt(x) + ' ' + fmt(y) +
          ' ' + fmt(z))
      },
      // Moves an entity onto the sphere of the given distance. It keeps its height when the sphere reaches that
      // height, so walkers are moved sideways along the ground instead of into it.
      placeAtDistance: function (entity, distance) {
        let dx = entity.getX() - domain.x
        const dy = entity.getY() - domain.y
        let dz = entity.getZ() - domain.z
        let flat = Math.sqrt(dx * dx + dz * dz)
        if (flat < 0.001) { dx = 1; dz = 0; flat = 1 }
        if (Math.abs(dy) < distance) {
          const across = Math.sqrt(distance * distance - dy * dy)
          ctx.teleport(entity, domain.x + dx / flat * across, entity.getY(), domain.z + dz / flat * across)
          return
        }
        const length = Math.sqrt(dx * dx + dy * dy + dz * dz)
        ctx.teleport(entity, domain.x + dx / length * distance, domain.y + dy / length * distance,
          domain.z + dz / length * distance)
      },
      members: function () {
        if (memberCache) return memberCache
        memberCache = []
        domain.members.slice().forEach(uuid => {
          const entity = findEntity(server, uuid)
          if (!entity) {
            // Offline players stay members and are pulled back when they return; vanished mobs are dropped.
            if (domain.players.indexOf(uuid) < 0) domain.members.splice(domain.members.indexOf(uuid), 1)
            return
          }
          if (!entity.isAlive()) {
            removeMember(server, domain, ctx, entity)
            return
          }
          memberCache.push(entity)
        })
        return memberCache
      },
      addMember: function (entity) {
        if (domainOf(entity)) return false
        domain.members.push(uuidOf(entity))
        if (entity.isPlayer()) domain.players.push(uuidOf(entity))
        entity.addTag(TAG_INSIDE)
        entity.addTag(ctx.nameTag)
        entity.persistentData.putInt(KEY_MEMBER_OF, domain.id)
        memberCache = null
        callAll(server, domain, 'enter', ctx, entity)
        return true
      },
      removeMember: function (entity) {
        removeMember(server, domain, ctx, entity)
        memberCache = null
      },
      close: function () { domain.ticksLeft = 0 }
    }
    return ctx
  }

  function removeMember(server, domain, ctx, entity) {
    const index = domain.members.indexOf(uuidOf(entity))
    if (index < 0) return
    callAll(server, domain, 'exit', ctx, entity)
    domain.members.splice(index, 1)
    const playerIndex = domain.players.indexOf(uuidOf(entity))
    if (playerIndex >= 0) domain.players.splice(playerIndex, 1)
    releaseEntity(entity, domain.slug)
  }

  function releaseEntity(entity, slug) {
    entity.removeTag(TAG_INSIDE)
    entity.removeTag(TAG_NAME_PREFIX + slug)
    entity.persistentData.remove(KEY_MEMBER_OF)
  }

  function openDomain(server, caster, name) {
    if (ownedBy(caster)) return { ok: false, reason: 'Your domain is already open.' }
    const seconds = cooldownSecondsLeft(server, uuidOf(caster))
    if (seconds > 0) return { ok: false, reason: 'Your domain is ready again in ' + seconds + ' seconds.' }
    if (domainOf(caster)) return { ok: false, reason: "You can't open a domain while you are inside one." }
    const spec = resolveSpec(name || DEFAULT_NAME)
    const dim = dimensionOf(caster)
    let tooClose = false
    Object.keys(state.active).forEach(id => {
      const other = state.active[id]
      if (other.dim !== dim) return
      const dx = other.x - caster.getX(), dy = other.y - caster.getY(), dz = other.z - caster.getZ()
      if (Math.sqrt(dx * dx + dy * dy + dz * dz) < other.radius + spec.radius + DEFAULTS.gap) tooClose = true
    })
    if (tooClose) return { ok: false, reason: "Another domain is too close so yours can't open here." }

    const domain = {
      id: nextDomainId(server),
      name: spec.name,
      slug: slugOf(spec.name),
      owner: uuidOf(caster),
      dim: dim,
      x: caster.getX(),
      y: caster.getY(),
      z: caster.getZ(),
      radius: spec.radius,
      durationTicks: spec.duration * TICKS_PER_SECOND,
      ticksLeft: spec.duration * TICKS_PER_SECOND,
      cooldown: spec.cooldown,
      age: 0,
      members: [],
      players: [],
      components: spec.components,
      data: {}
    }
    state.active[domain.id] = domain
    caster.addTag(TAG_OWNER)
    const ctx = makeContext(server, domain)
    ctx.addMember(caster)
    callAll(server, domain, 'open', ctx)
    return { ok: true, domain: domain }
  }

  function closeDomain(server, domain) {
    if (!state.active[domain.id]) return
    const ctx = makeContext(server, domain)
    callAll(server, domain, 'close', ctx)
    ctx.members().forEach(entity => removeMember(server, domain, ctx, entity))
    setCooldown(server, domain.owner, domain.cooldown)
    const owner = ctx.ownerEntity()
    if (owner) owner.removeTag(TAG_OWNER)
    delete state.active[domain.id]
  }

  function tickDomain(server, domain) {
    domain.age++
    domain.ticksLeft--
    const ctx = makeContext(server, domain)
    callAll(server, domain, 'tick', ctx)
    ctx.members().forEach(entity => callAll(server, domain, 'memberTick', ctx, entity))
    if (domain.ticksLeft <= 0) closeDomain(server, domain)
  }

  // A player who was inside a domain that is gone (closed while offline, or a restart) loses its tags and the
  // Origins powers it granted under its source. Other effects lapse on their own.
  function cleanUpStaleMembership(server, player) {
    const staleId = player.persistentData.getInt(KEY_MEMBER_OF)
    const current = domainOf(player)
    if (staleId > 0 && !(current && current.id === staleId)) {
      server.runCommandSilent('power revokeall ' + uuidOf(player) + ' ' + POWER_SOURCE_PREFIX + staleId)
      player.persistentData.remove(KEY_MEMBER_OF)
    }
    if (!current) player.removeTag(TAG_INSIDE)
    if (!ownedBy(player)) player.removeTag(TAG_OWNER)
    const keep = current ? TAG_NAME_PREFIX + current.slug : null
    const stale = []
    player.getTags().forEach(tag => {
      const name = String(tag)
      if (name.indexOf(TAG_NAME_PREFIX) === 0 && name !== keep) stale.push(name)
    })
    stale.forEach(tag => player.removeTag(tag))
  }

  function castOwn(server, player) {
    const name = registeredName(player)
    if (!name) {
      player.tell(Text.gray('You have no domain yet so ask an admin to give you one.'))
      return 0
    }
    const result = openDomain(server, player, name)
    if (!result.ok) player.tell(Text.gray(result.reason))
    return result.ok ? 1 : 0
  }

  ServerEvents.tick(event => {
    const server = event.server
    Object.keys(state.active).forEach(id => {
      const domain = state.active[id]
      if (!domain) return
      try {
        tickDomain(server, domain)
      } catch (error) {
        console.error('[ordertest] Domain ' + domain.name + ' failed in the engine and was closed: ' + error)
        try { closeDomain(server, domain) } catch (ignored) { delete state.active[id] }
      }
    })
  })

  PlayerEvents.chat(event => {
    const match = CAST_PHRASE.exec(String(event.message))
    if (!match) return
    const player = event.player
    const own = registeredName(player)
    if (!own) {
      player.tell(Text.gray('You have no domain yet so ask an admin to give you one.'))
      return
    }
    if (keyOf(match[1]) !== keyOf(own)) {
      player.tell(Text.gray('That is not the name of your domain.'))
      return
    }
    const server = event.server
    const uuid = player.getUuid()
    server.scheduleInTicks(1, () => {
      const current = server.getPlayerList().getPlayer(uuid)
      if (current && current.isAlive()) castOwn(server, current)
    })
  })

  PlayerEvents.loggedIn(event => cleanUpStaleMembership(event.server, event.player))

  ServerEvents.highPriorityData(event => {
    Object.keys(api.powers).forEach(id => {
      const parts = id.split(':')
      event.addJson(parts[0] + ':powers/' + parts[1], api.powers[id])
    })
    const layers = {}
    Object.keys(api.origins).forEach(id => {
      const spec = api.origins[id]
      const parts = id.split(':')
      const json = Object.assign({}, spec)
      delete json.layer
      event.addJson(parts[0] + ':origins/' + parts[1], json)
      const layer = spec.layer || 'origins:origin'
      if (!layers[layer]) layers[layer] = []
      layers[layer].push(id)
    })
    Object.keys(layers).forEach(layer => {
      const parts = layer.split(':')
      event.addJson(parts[0] + ':origin_layers/' + parts[1], { replace: false, origins: layers[layer] })
    })
  })

  ServerEvents.commandRegistry(event => {
    const Commands = event.commands
    const Arguments = event.arguments
    const admin = source => source.hasPermission(ADMIN_PERMISSION)
    const say = (ctx, text) => ctx.source.sendSystemMessage(Text.of(text))
    // Brigadier hides script errors behind "An unexpected error occurred", so log them first.
    const safe = run => ctx => {
      try {
        return run(ctx)
      } catch (error) {
        console.error('[ordertest] /domain failed: ' + error)
        throw error
      }
    }
    const ownerArg = ctx => ownedBy(Arguments.ENTITY.getResult(ctx, 'owner'))

    function openFor(ctx, entity, name) {
      const result = openDomain(ctx.source.server, entity, name)
      say(ctx, result.ok ? 'Opened ' + result.domain.name + ' (id ' + result.domain.id + ').' : result.reason)
      return result.ok ? 1 : 0
    }

    event.register(Commands.literal('domain')
      .then(Commands.literal('cast').executes(safe(ctx =>
        castOwn(ctx.source.server, ctx.source.getPlayerOrException()))))
      .then(Commands.literal('name').executes(safe(ctx => {
        const name = registeredName(ctx.source.getPlayerOrException())
        say(ctx, name ? 'Your domain is ' + name + '.' : 'You have no domain yet.')
        return 1
      })))
      .then(Commands.literal('register').requires(admin)
        .then(Commands.argument('player', Arguments.PLAYER.create(event))
          .then(Commands.argument('name', Arguments.GREEDY_STRING.create(event)).executes(safe(ctx => {
            const player = Arguments.PLAYER.getResult(ctx, 'player')
            const name = String(Arguments.GREEDY_STRING.getResult(ctx, 'name')).replace(TRAILING_PUNCTUATION, '').trim()
            player.persistentData.putString(KEY_NAME, name)
            say(ctx, player.getName().getString() + ' now owns the domain ' + name + '.')
            return 1
          })))))
      .then(Commands.literal('clear').requires(admin)
        .then(Commands.argument('player', Arguments.PLAYER.create(event)).executes(safe(ctx => {
          const player = Arguments.PLAYER.getResult(ctx, 'player')
          player.persistentData.remove(KEY_NAME)
          setCooldown(ctx.source.server, uuidOf(player), 0)
          say(ctx, player.getName().getString() + ' no longer has a domain.')
          return 1
        }))))
      .then(Commands.literal('open').requires(admin)
        .then(Commands.argument('caster', Arguments.ENTITY.create(event))
          .executes(safe(ctx => {
            const caster = Arguments.ENTITY.getResult(ctx, 'caster')
            return openFor(ctx, caster, caster.isPlayer() ? registeredName(caster) : null)
          }))
          .then(Commands.argument('name', Arguments.GREEDY_STRING.create(event)).executes(safe(ctx =>
            openFor(ctx, Arguments.ENTITY.getResult(ctx, 'caster'), String(Arguments.GREEDY_STRING.getResult(ctx, 'name'))))))))
      .then(Commands.literal('close').requires(admin)
        .then(Commands.argument('owner', Arguments.ENTITY.create(event)).executes(safe(ctx => {
          const domain = ownerArg(ctx)
          if (!domain) { say(ctx, 'That entity has no open domain.'); return 0 }
          closeDomain(ctx.source.server, domain)
          say(ctx, 'Closed ' + domain.name + '.')
          return 1
        }))))
      .then(Commands.literal('closeall').requires(admin).executes(safe(ctx => {
        const ids = Object.keys(state.active)
        ids.forEach(id => closeDomain(ctx.source.server, state.active[id]))
        say(ctx, 'Closed ' + ids.length + ' domains.')
        return ids.length
      })))
      .then(Commands.literal('time').requires(admin)
        .then(Commands.argument('owner', Arguments.ENTITY.create(event))
          .then(Commands.argument('seconds', Arguments.INTEGER.create(event)).executes(safe(ctx => {
            const domain = ownerArg(ctx)
            if (!domain) { say(ctx, 'That entity has no open domain.'); return 0 }
            const seconds = Arguments.INTEGER.getResult(ctx, 'seconds')
            domain.ticksLeft = seconds * TICKS_PER_SECOND
            say(ctx, domain.name + ' now closes in ' + seconds + ' seconds.')
            return 1
          })))))
      .then(Commands.literal('list').requires(admin).executes(safe(ctx => {
        const ids = Object.keys(state.active)
        if (ids.length === 0) say(ctx, 'No domains are open.')
        ids.forEach(id => {
          const d = state.active[id]
          say(ctx, d.id + ' ' + d.name + ' at ' + Math.floor(d.x) + ' ' + Math.floor(d.y) + ' ' + Math.floor(d.z) +
            ' with ' + d.members.length + ' inside and ' + Math.ceil(d.ticksLeft / TICKS_PER_SECOND) + ' s left.')
        })
        return ids.length
      })))
      .then(Commands.literal('components').requires(admin).executes(safe(ctx => {
        say(ctx, 'Components: ' + Object.keys(api.components).sort().join(' '))
        say(ctx, 'Domains: ' + Object.keys(api.domains).map(k => api.domains[k].name).sort().join(', '))
        return 1
      })))
    )
  })
})()
