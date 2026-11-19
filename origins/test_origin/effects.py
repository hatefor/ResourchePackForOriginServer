"""Test Origin effects, released as ordertest:test_origin/<effect>. Authored for radius 15; photon_fx scales them."""
import fx


def burst():
    """A ring of light thrown outward along the ground, once."""
    doc = fx.FxDocument()
    ring = doc.particles("burst_ring")
    ring.looping(False).duration(30).emission_rate(0).burst(time=0, count=300).max_particles(300)
    ring.shape_function(speed_x="cos(2*PI*randomA)", speed_y="0.1", speed_z="sin(2*PI*randomA)")
    ring.lifetime(20).speed(12).size(0.35).lights()
    ring.color_over_lifetime([(0.0, 1.0, 1.0, 1.0, 1.0), (1.0, 0.7, 0.4, 1.0, 0.0)])
    return doc


EFFECTS = {"burst": burst}
