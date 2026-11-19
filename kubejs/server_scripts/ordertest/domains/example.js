// A domain definition. The name matches what a player registers (/domain register <player> Example) and types
// ("Domain expansion Example"). Anything left out uses OrderTest.defaults. Names without a definition get the
// default components.
//   components:        replace the default list entirely
//   extraComponents:   add to the default list; [id, options] pairs, the same id may appear twice
//   removeComponents:  drop default components by id
//   options:           override a component's options without listing it
global.OrderTest.domain('Example', {
  radius: 12,
  duration: 20,
  cooldown: 30,
  extraComponents: [
    ['potion_effect', { effect: 'minecraft:glowing', target: 'others' }]
  ],
  options: {
    display_shell: { block: 'minecraft:yellow_concrete' },
    meridian_particles: { particle: 'minecraft:dust 0.9 0.7 0.1 2.0' }
  }
})
