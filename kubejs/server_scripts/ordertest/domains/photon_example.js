// A domain that uses Photon effects. Make each effect with /photon_editor in the dev client and export it as
// resourcepack/assets/ordertest/fx/<name>.fx; tools/validate.py warns about any listed here that don't exist yet.
global.OrderTest.domain('Photon Example', {
  radius: 15,
  duration: 30,
  cooldown: 60,
  extraComponents: [
    ['photon_fx', {
      open: 'ordertest:domain_open',
      loop: 'ordertest:domain_loop',
      close: 'ordertest:domain_close',
      memberLoop: 'ordertest:member_aura',
      target: 'others'
    }]
  ]
})
