"""The Photon Example domain's effects, authored for radius 15 (photon_fx scales them with the domain's radius).

Positions and directions are Function-shape expressions Photon evaluates on each client. A uniform random
direction is u = 2*randomB-1 (height) and 2*PI*randomA (angle); randomA..E keep one value per particle across
all six expressions, so the same letters give a consistent point and direction.
"""
import fx

RADIUS = 15
VIOLET = (0.75, 0.45, 1.0)
GOLD = (1.0, 0.8, 0.35)

U = "(2*randomB-1)"
RING = f"sqrt(1-{U}*{U})"
DIR_X = f"{RING}*cos(2*PI*randomA)"
DIR_Y = U
DIR_Z = f"{RING}*sin(2*PI*randomA)"


def _fade(rgb, start_alpha=1.0):
    r, g, b = rgb
    return [(0.0, 1.0, 1.0, 1.0, start_alpha), (0.25, r, g, b, start_alpha), (1.0, r, g, b, 0.0)]


def domain_open():
    """A shell of light thrown from the centre out to the wall, once."""
    doc = fx.FxDocument()
    burst = doc.particles("open_shell")
    burst.looping(False).duration(30).emission_rate(0).burst(time=0, count=700).max_particles(700)
    burst.shape_function(speed_x=DIR_X, speed_y=DIR_Y, speed_z=DIR_Z)
    burst.lifetime(20).speed(RADIUS).size(0.45).color_over_lifetime(_fade(VIOLET)).lights()
    return doc


def domain_loop():
    """A curtain rising around the inside of the wall while the domain is open."""
    doc = fx.FxDocument()
    curtain = doc.particles("wall_curtain")
    curtain.looping(True).duration(100).emission_rate(8).max_particles(480)
    curtain.shape_function(x=f"{RADIUS - 1}*cos(2*PI*(randomA+t))", y="0", z=f"{RADIUS - 1}*sin(2*PI*(randomA+t))",
                           speed_y="1")
    curtain.lifetime(50).speed(3).size(0.3).color_over_lifetime(_fade(VIOLET, 0.8)).lights()
    return doc


def domain_close():
    """Light pulled from the wall into the centre, once."""
    doc = fx.FxDocument()
    implode = doc.particles("close_implode")
    implode.looping(False).duration(30).emission_rate(0).burst(time=0, count=600).max_particles(600)
    implode.shape_function(x=f"{RADIUS}*{DIR_X}", y=f"{RADIUS}*{DIR_Y}", z=f"{RADIUS}*{DIR_Z}",
                           speed_x=f"-{DIR_X}", speed_y=f"-{DIR_Y}", speed_z=f"-{DIR_Z}")
    implode.lifetime(20).speed(RADIUS).size(0.4).color_over_lifetime(_fade(GOLD)).lights()
    return doc


def member_aura():
    """A small ring of motes at the feet of everyone caught."""
    doc = fx.FxDocument()
    ring = doc.particles("member_ring")
    ring.looping(True).duration(40).emission_rate(1.5).max_particles(60)
    ring.shape_function(x="0.6*cos(2*PI*randomA)", y="0.1", z="0.6*sin(2*PI*randomA)", speed_y="1")
    ring.lifetime(25).speed(0.6).size(0.15).color_over_lifetime(_fade(VIOLET, 0.9)).lights()
    return doc


EFFECTS = {
    "domain_open": domain_open,
    "domain_loop": domain_loop,
    "domain_close": domain_close,
    "member_aura": member_aura,
}
