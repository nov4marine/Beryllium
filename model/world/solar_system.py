import random
import math


class SolarSystem:
    """Container for all celestial bodies in a system (star, planets, moons, asteroids, etc.)"""

    def __init__(self, name, galaxy_x, galaxy_y, uid=None, owner=None, registry=None):
        self.name = name
        self.owner = owner
        self.galaxy_x = galaxy_x
        self.galaxy_y = galaxy_y
        self.uid = uid
        self.solar_system_size = 0  # Can be set later based on bodies
        self.registry = registry

    @property
    def bodies(self):
        bodies = self.registry.get_celestials_within_starsystem(self.uid)
        return bodies

    def pick_homeworld_candidate(self):
        terrestrial_worlds = [p for p in self.bodies if p.planet_type and p.planet_type == "rocky"]
        chosen_candidate = random.choice(terrestrial_worlds)
        return chosen_candidate


    def assign_capital(self, nation):
        """Deprecated in favor of pick_homeworld_candidate()"""
        planets = [i for i in self.bodies if i.parent is not None]
        if not planets:
            raise Exception(f"No planets found in system {self.name}")
        planet = random.choice(planets)
        print(planet)

        # Set planet as habitable and assign properties
        planet.type = "rocky"
        # planet.habitable = True
        #planet.name = nation.homeworld["planet_name"]
        #planet.climate = nation.homeworld["climate"]
        #self.name = nation.homeworld["system_name"]
        nation.planets.append(planet)
        nation.capital = planet
        nation.initialize_nation()

    def on_daily_update(self):
        for body in self.bodies:
            body.update_orbit()

    def get_star(self):
        return next((b for b in self.bodies if b.body_type == "star"), None)

    def get_planets(self):
        return [b for b in self.bodies if b.body_type == "planet"]

    def get_moons(self):
        return [b for b in self.bodies if b.body_type == "moon"]

    def get_asteroids(self):
        return [b for b in self.bodies if b.body_type == "asteroid"]

    @staticmethod
    def assign_capital_system(galaxy, nation):
        """
        Assigns a random SolarSystem and planet as the nation's homeworld.
        Modifies the planet to be habitable and sets its properties.
        Returns (planet, system_name).
        currently deprecated in favor of SolarSystem.assign_capital
        """
        # Pick a random SolarSystem that is not already owned
        unowned_systems = [s for s in galaxy.solar_systems.values() if s.owner is None]
        if not unowned_systems:
            raise Exception("No unowned solar systems available for capital assignment.")
        system = random.choice(unowned_systems)
        system.owner = nation

        # Prefer rocky planets, fallback to any planet
        rocky_planets = [p for p in system.get_planets() if getattr(p, "type", None) == "rocky"]
        if rocky_planets:
            planet = random.choice(rocky_planets)
        else:
            planets = system.get_planets()
            if not planets:
                raise Exception(f"No planets found in system {system.name}")
            planet = random.choice(planets)

        # Set planet as habitable and assign properties
        planet.habitable = True
        planet.type = "rocky"
        planet.name = nation.homeworld["homeworld"]["planet"]
        planet.climate = nation.homeworld["homeworld"]["climate"]
        planet.color = (0, 255, 255)  # Optional: visually mark as habitable

        return planet, system.name


# --- Celestial Body Classes ---

class CelestialBody:
    def __init__(self, name, body_type, radius, size, color, angle, speed, registry=None, solar_system_id=None,
                 parent_id=None, **kwargs):
        self.name = name
        self.body_type = body_type  # "star", "planet", "moon", "asteroid"
        self.radius = radius  # Distance from parent (or system center for stars). Orbital radius.
        self.size = size  # Physical size or radius of the body (just for rendering for now, but could be used for gravity and land size later)
        self.color = color or (255, 255, 255)  # Default white
        self.angle = angle  # Current angle in orbital path (radians)
        self.speed = speed  # Orbital speed (normal speed, not radians per time unit)
        self.registry = registry
        self.solar_system_id = solar_system_id  # Reference to the solar system that this lives in
        self.parent_id = parent_id  # Another CelestialBody or None which this body orbits around
        self.rect = None  # For mouse collision/highlight
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def parent(self):
        parent = self.registry.celestial_bodies.get(self.parent_id)
        return parent

    @property
    def solar_system(self):
        system = self.registry.solar_systems.get(self.solar_system_id)
        return system

    def update_orbit(self):
        self.angle += self.speed
        self.angle %= 2 * math.pi

    def get_position(self):
        """Return world position relative to system center."""
        if self.parent_id is None:
            return (0, 0)
        parent_x, parent_y = self.parent.get_position()
        x = parent_x + math.cos(self.angle) * self.radius
        y = parent_y + math.sin(self.angle) * self.radius
        return (x, y)


class Star(CelestialBody):
    STAR_COLORS = {
        "O": (155, 176, 255),
        "B": (170, 191, 255),
        "A": (202, 215, 255),
        "F": (248, 247, 255),
        "G": (255, 244, 234),
        "K": (255, 210, 161),
        "M": (255, 204, 111),
    }

    def __init__(self, name, star_type, radius, size, color=None, angle=0, speed=0, solar_system_id=None, parent=None,
                 **kwargs):
        color = color or self.STAR_COLORS.get(star_type, (255, 255, 255))
        super().__init__(name, "star", radius, size, color, angle, speed, solar_system_id, parent, star_type=star_type,
                         **kwargs)
        self.star_type = star_type

    def get_position(self):
        return (0, 0)  # Always at system center

    #def draw(self, screen, camera, parent_pos):
    # Custom star drawing (glow, etc.) can go here
    #world_x, world_y = self.get_position()
    #screen_x, screen_y = camera.apply(world_x, world_y)
    #arcade.draw_circle_filled((int(screen_x), int(screen_y)), int(self.size * camera.zoom), self.color)


class Planet(CelestialBody):
    def __init__(self, name, radius, size, color, angle, speed, parent, resources=None, planet_type="rocky",
                 habitable=False,
                 climate=None, colony=None, **kwargs):
        color = color or ((100, 200, 255) if planet_type == "rocky" else (200, 200, 100))
        super().__init__(name, "planet", radius, size, color, angle, speed, parent, planet_type=planet_type, **kwargs)
        self.planet_type = planet_type  # "rocky", "gas", "icy"
        self.habitable = habitable
        self.climate = climate
        self.colony = colony
        self.resources = resources
        # Probably a dictionary of resources and their amounts. will create a function for procedural generation of resources later


class Moon(Planet):
    def __init__(self, name, radius, size, color, angle, speed, parent, **kwargs):
        super().__init__(
            name=name,
            radius=radius,
            size=size,
            color=color,
            angle=angle,
            speed=speed,
            parent=parent,
            planet_type="moon",
            **kwargs
        )


class Asteroid(CelestialBody):
    def __init__(self, name, radius, size, color, angle, speed, parent, **kwargs):
        super().__init__(
            name=name,
            body_type="asteroid",
            radius=radius,
            size=size,
            color=color,
            angle=angle,
            speed=speed,
            parent=parent,
            **kwargs
        )