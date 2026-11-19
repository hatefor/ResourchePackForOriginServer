// The Test Origin domain. Give it to a player with /domain register <player> Test Origin.
global.OrderTest.domain('Test Origin', {
  radius: 12,
  duration: 20,
  cooldown: 30,
  extraComponents: [
    ['photon_fx', { open: 'ordertest:test_origin/burst' }]
  ],
  options: {
    display_shell: { block: 'minecraft:purple_concrete' }
  }
})
