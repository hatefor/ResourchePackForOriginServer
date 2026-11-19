// An Origins origin written in JS. The core injects these as datapack JSON on every /reload, so editing this
// file and running /reload changes the origin. Power and origin JSON use the normal Origins 1.10 format.
global.OrderTest.power('ordertest:cast_domain', {
  type: 'origins:active_self',
  name: 'Domain Expansion',
  description: 'Press your primary ability key to open your own domain.',
  cooldown: 20,
  hud_render: { should_render: false },
  key: { key: 'key.origins.primary_active', continuous: false },
  entity_action: { type: 'origins:execute_command', command: 'domain cast' }
})

global.OrderTest.origin('ordertest:domain_caster', {
  name: 'Domain Caster',
  description: 'Opens a domain that nobody outside can enter and nobody inside can leave.',
  icon: { item: 'minecraft:ender_eye' },
  impact: 1,
  order: 200,
  powers: ['ordertest:cast_domain'],
  layer: 'origins:origin'
})
