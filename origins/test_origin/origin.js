// The Test Origin origin, written in JS and injected as Origins JSON on every /reload. Its passive power is plain
// datapack JSON in this folder's data/, which the tools merge into the shipped datapack.
global.OrderTest.origin('ordertest:test_origin', {
  name: 'Test Origin',
  description: 'Describe what this origin does in one plain sentence.',
  icon: { item: 'minecraft:amethyst_shard' },
  impact: 1,
  order: 300,
  powers: ['ordertest:test_origin/night_eyes'],
  layer: 'origins:origin'
})
