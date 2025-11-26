import random
import math
import arcade


class SolarSystem:
    """Container for all celestial bodies in a system (star, planets, moons, asteroids, etc.)"""

    def __init__(self, name, owner=None):
        self.name = name
        self.owner = owner
        self.solar_system_size = 0  # Can be set later based on bodies
        self.bodies = self._generate_bodies()

    def change_owner(self, new_owner):
        """Change the owner of the solar system."""
        self.owner = new_owner

    def _generate_bodies(self):
        bodies = []

        # --- Generate the star ---
        # Realistic star generation.
        star_type = random.choice(["O", "B", "A", "F", "G", "K", "M"])
        # Realistic star size range based on type
        star_size_range = {
            "O": (360, 480),
            "B": (300, 360),
            "A": (240, 300),
            "F": (192, 240),
            "G": (152, 192),
            "K": (112, 152),
            "M": (72, 112),
        }
        star = Star(
            name=f"{self.name} Star",
            star_type=star_type,
            radius=0,  # At system center
            size=random.randint(*star_size_range[star_type]),
            color=None,  # Will be set by Star class based on type
            angle=0,
            speed=0,
            parent=None
        )
        bodies.append(star)

        # --- Generate planets ---
        num_planets = random.randint(4, 10)  # Random number of planets
        solar_system_size = (600 * ((num_planets + 1) ** 1.8)) + (star.size * 4)
        self.solar_system_size = solar_system_size
        for i in range(num_planets):
            orbital_radius = 600 * ((i + 1) ** 1.8) + star.size * 4 # Exponential spacing. Orbital radius is distance from star. v1 is 600 * (1.5 ** i)
            distance_ratio = orbital_radius / solar_system_size
            planet_type = self.determine_planet_type(distance_ratio) # "rocky", "gas", or "icy"
            size = self.determine_planet_size(planet_type)
            color = None  # Let Planet class pick based on type, or randomize here
            speed = 2 / orbital_radius * 0.5
            angle = random.uniform(0, 2 * math.pi)
            name = f"{self.name} Planet {i + 1}"
            planet = Planet(
                name=name,
                radius=orbital_radius,
                size=size,
                color=color,
                angle=angle,
                speed=speed,
                parent=star,
                planet_type=planet_type
            )
            bodies.append(planet)

            # --- Optionally make the planet habitable ---
            if planet_type == "rocky" and random.random() < 0.1:
                planet.habitable = True
                planet.climate = random.choice(["continental", "ice", "desert", "ocean"])

            # --- Optionally generate moons for some planets ---
            if planet_type == "rocky" and random.random() < 0.4:
                num_moons = random.randint(1, 2)
                for m in range(num_moons):
                    moon_radius = planet.size + 100 * (m + 1)
                    moon_angle = random.uniform(0, 2 * math.pi)
                    moon = Moon(
                        name=f"{planet.name} Moon {m + 1}",
                        radius=moon_radius,
                        size=self.determine_planet_size("moon"),
                        color=(180, 180, 180),
                        angle=moon_angle,
                        speed=random.uniform(0.001, 0.003),
                        parent=planet
                    )
                    bodies.append(moon)

            # --- Optionally generate moons for gas giants ---
            if planet_type == "gas" and random.random() < 0.8:
                num_moons = random.randint(1, 4)
                for m in range(num_moons):
                    moon_radius = 100 * (m + 1) + planet.size * 4
                    moon_angle = random.uniform(0, 2 * math.pi)
                    moon = Moon(
                        name=f"{planet.name} Moon {m + 1}",
                        radius=moon_radius,
                        size=self.determine_planet_size("moon"),
                        color=(180, 180, 180),
                        angle=moon_angle,
                        speed=random.uniform(0.001, 0.003),
                        parent=planet
                    )
                    bodies.append(moon)

        # --- Optionally generate asteroids ---
        for _ in range(random.randint(10, 20)):
            belt_radius = random.uniform(1500, 3000)
            belt_angle = random.uniform(0, 2 * math.pi)
            asteroid = Asteroid(
                name=f"{self.name} Asteroid",
                radius=belt_radius,
                size=random.randint(4, 8),
                color=(120, 120, 120),
                angle=belt_angle,
                speed=random.uniform(0.0005, 0.0015),
                parent=star
            )
            # bodies.append(asteroid)

        return bodies

    def assign_capital(self, nation):
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

    def determine_planet_type(self, distance_ratio):
        x = distance_ratio
        weights = [
            max(0, 1.0 - x * 2),  # Rocky more likely closer in
            max(0, 2 ** (-((x-0.6) ** 2) / 0.03)),  # Gas more likely farther out
            max(0, x - 0.5)  # Icy dominant in outer regions
        ]
        return random.choices(["rocky", "gas", "icy"], weights=weights, k=1)[0]
    
    def determine_planet_size(self, planet_type):
        if planet_type == "rocky":
            return random.randint(24, 36)
        elif planet_type == "gas":
            return random.randint(40, 60)
        elif planet_type == "icy":
            return random.randint(18, 28)
        elif planet_type == "moon":
            return random.randint(12, 20)
        else:
            return 20  # Default size

    def on_update(self, time_delta):
        for body in self.bodies:
            body.update_orbit(time_delta)

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
    def __init__(self, name, body_type, radius, size, color, angle, speed, parent=None, **kwargs):
        self.name = name
        self.body_type = body_type # "star", "planet", "moon", "asteroid"
        self.radius = radius  # Distance from parent (or system center for stars). Orbital radius.
        self.size = size # Physical size or radius of the body (just for rendering for now, but could be used for gravity and land size later)
        self.color = color or (255, 255, 255) # Default white
        self.angle = angle # Current angle in orbital path (radians)
        self.speed = speed # Orbital speed (normal speed, not radians per time unit)
        self.parent = parent  # Another CelestialBody or None which this body orbits around
        self.rect = None  # For mouse collision/highlight
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update_orbit(self, time_delta):
        self.angle += self.speed * time_delta 
        self.angle %= 2 * math.pi

    def get_position(self):
        """Return world position relative to system center."""
        if self.parent is None:
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

    def __init__(self, name, star_type, radius, size, color=None, angle=0, speed=0, parent=None, **kwargs):
        color = color or self.STAR_COLORS.get(star_type, (255, 255, 255))
        super().__init__(name, "star", radius, size, color, angle, speed, parent, star_type=star_type, **kwargs)
        self.star_type = star_type

    def get_position(self):
        return (0, 0)  # Always at system center

    #def draw(self, screen, camera, parent_pos):
        # Custom star drawing (glow, etc.) can go here
        #world_x, world_y = self.get_position()
        #screen_x, screen_y = camera.apply(world_x, world_y)
        #arcade.draw_circle_filled((int(screen_x), int(screen_y)), int(self.size * camera.zoom), self.color)


class Planet(CelestialBody):
    def __init__(self, name, radius, size, color, angle, speed, parent, resources=None, planet_type="rocky", habitable=False,
                 climate=None, colony=None, **kwargs):
        color = color or ((100, 200, 255) if planet_type == "rocky" else (200, 200, 100))
        super().__init__(name, "planet", radius, size, color, angle, speed, parent, planet_type=planet_type, **kwargs)
        self.planet_type = planet_type # "rocky", "gas", "icy"
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

solar_system = SolarSystem("Test System")
print(f"Solar System Size: {solar_system.solar_system_size}")