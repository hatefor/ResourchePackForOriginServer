// The Domain Caster's domain. Its effects are this folder's effects.py, released as ordertest:domain_caster/<name>.
global.OrderTest.domain('Photon Example', {
  radius: 15,
  duration: 30,
  cooldown: 60,
  extraComponents: [
    ['photon_fx', {
      open: 'ordertest:domain_caster/domain_open',
      loop: 'ordertest:domain_caster/domain_loop',
      close: 'ordertest:domain_caster/domain_close',
      memberLoop: 'ordertest:domain_caster/member_aura',
      target: 'others'
    }]
  ]
})
