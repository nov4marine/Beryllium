import math
import random

from model.world.solar_system import SolarSystem, Star, Planet, Moon, Asteroid
from model.politics.nation import NationStub
from model import *

from model.registry import Registry


class Architect:
    """Wrapper class (around registry) to handle creation and destruction of all objects in the registry"""
    def __init__(self, registry):
        self.registry = registry

    # ---- Individual function components for the procedural generation of the world ----

    def generate_galaxy_with_stars(self, num_stars=1000, galaxy_size=6000):
        # number of stars to generate
        # galaxy_size is the radius of the galaxy (farthest star generated, and used for rendering disk image)
        stars = []

        num_arms = 4
        arm_tightness = 3  # Lower = looser, higher = tighter spiral
        arm_spread = 0.25  # Lower = thinner arms, higher = fuzzier arms
        center_radius = galaxy_size * 0.15
        overall_rotation = math.pi / 4
        min_distance = 200

        for i in range(num_stars):
            while True:
                # Radial distance (ensuring it's outside the empty center)
                r = random.uniform(center_radius, galaxy_size)

                # Angle for the spiral arms
                arm_index = i % num_arms
                arm_angle = arm_index * (2 * math.pi / num_arms)
                # Add a small random offset to theta for spread
                theta_offset = random.gauss(0, arm_spread)
                theta = overall_rotation + arm_angle + arm_tightness * math.log(r + 1) + theta_offset

                # Convert polar to Cartesian
                x = r * math.cos(theta)
                y = r * math.sin(theta)

                # Check minimum distance to other stars
                too_close = False
                for star in stars:
                    distance = math.sqrt((x - star.x) ** 2 + (y - star.y) ** 2)
                    if distance < min_distance:
                        too_close = True
                        break

                # Add the star only if it's far enough from others
                if not too_close:
                    break

            name = f"star {i + 1}"

            star = SolarSystem(
                name=name,
                galaxy_x=x,
                galaxy_y=y,
            )
            stars.append(star)
            system_id = self.registry.register_solar_system(star)
            planets = self.generate_celestial_bodies(star)

    def generate_celestial_bodies(self, solar_system):
        bodies = []
        system_id = solar_system.uid

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
            name=f"{solar_system.name} Star",
            star_type=star_type,
            radius=0,  # At system center
            size=random.randint(*star_size_range[star_type]),
            color=None,  # Will be set by Star class based on type
            angle=0,
            speed=0,
            parent_id=None,
        )
        bodies.append(star)
        star_id = self.registry.register_celestial_body(solar_system_id=system_id)

        # --- Generate planets ---
        num_planets = random.randint(4, 10)  # Random number of planets
        solar_system_size = (600 * ((num_planets + 1) ** 1.8)) + (star.size * 4)
        solar_system.solar_system_size = solar_system_size
        for i in range(num_planets):
            orbital_radius = 600 * ((i + 1) ** 1.8) + star.size * 4
            # Exponential ^ spacing. Orbital radius is distance from star. v1 is 600 * (1.5 ** i)
            distance_ratio = orbital_radius / solar_system_size
            planet_type = _determine_planet_type(distance_ratio)  # "rocky", "gas", or "icy"
            size = _determine_planet_size(planet_type)
            color = None  # Let Planet class pick based on type, or randomize here
            speed = 2 / orbital_radius * 0.5
            angle = random.uniform(0, 2 * math.pi)
            name = f"{solar_system.name} Planet {i + 1}"
            planet = Planet(
                name=name,
                radius=orbital_radius,
                size=size,
                color=color,
                angle=angle,
                speed=speed,
                parent_id=star_id,
                planet_type=planet_type
            )
            bodies.append(planet)
            planet_id = self.registry.register_celestial_body(planet)

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
                        size=_determine_planet_size("moon"),
                        color=(180, 180, 180),
                        angle=moon_angle,
                        speed=random.uniform(0.001, 0.003),
                        parent_id=planet_id
                    )
                    bodies.append(moon)
                    self.registry.register_celestial_body(moon)

            # --- Optionally generate moons for gas giants ---
            if planet_type == "gas" and random.random() < 0.8:
                num_moons = random.randint(1, 4)
                for m in range(num_moons):
                    moon_radius = 100 * (m + 1) + planet.size * 4
                    moon_angle = random.uniform(0, 2 * math.pi)
                    moon = Moon(
                        name=f"{planet.name} Moon {m + 1}",
                        radius=moon_radius,
                        size=_determine_planet_size("moon"),
                        color=(180, 180, 180),
                        angle=moon_angle,
                        speed=random.uniform(0.001, 0.003),
                        parent_id=planet
                    )
                    bodies.append(moon)
                    self.registry.register_celestial_body(moon)

        # --- Optionally generate asteroids ---
        for _ in range(random.randint(10, 20)):
            belt_radius = random.uniform(1500, 3000)
            belt_angle = random.uniform(0, 2 * math.pi)
            asteroid = Asteroid(
                name=f"{solar_system.name} Asteroid",
                radius=belt_radius,
                size=random.randint(4, 8),
                color=(120, 120, 120),
                angle=belt_angle,
                speed=random.uniform(0.0005, 0.0015),
                parent_id=star
            )
            # bodies.append(asteroid)

        return bodies  # Optionally returns a list of objects of all celestial bodies in the solar system

    # --- Dynamic World Creation and Destruction. ---

    def build_nation(self, name):
        """Creates a Nation and registers it globally."""
        # We pass the registry to the Nation, so it can talk to its colonies later
        new_nation = NationStub(name)

        self.registry.register_nation(new_nation)
        return new_nation

    def build_colony(self, name, planet_id, nation_id):
        """Assembles a colony and files the paperwork globally."""
        # 1. Instantiate the Object
        new_colony = Colony(name, planet_id, nation_id)

        # 2. Register it globally
        colony_uid = self.registry.register_colony(new_colony, planet_id, nation_id)

        # 3. Link it to the Planet (The Physical Layer)
        planet = self.registry.get_planet(planet_id)
        planet.colony_id = colony_uid

        return new_colony

    def build_building(self, building_type, colony_id):
        print("not implemented yet")
        # self.registry.register_building(building_type, colony_id)
        pass

    def build_job(self, profession, employer_id, worker_id):
        new_job = Job(profession, employer_id, worker_id)
        self.registry.register_job(employer_id, worker_id)

    def build_pop(self):
        new_pop = Pop()
        pop_id = self.registry.register_pop()

        # 3. Create the Nations (The Players)
        une = builder.build_nation("United Nations of Earth", "UNE")
        cmr = builder.build_nation("Commonwealth of Mars", "CMR")

        # 4. Create the Geography
        # Let's say we have planets already defined in the Registry
        builder.build_colony("New London", planet_id="p_earth_01", nation_id="UNE")
        builder.build_colony("Dust City", planet_id="p_mars_01", nation_id="CMR")


# ---- Helper Functions ----

def _determine_planet_type(distance_ratio):
    x = distance_ratio
    weights = [
        max(0, 1.0 - x * 2),  # Rocky more likely closer in
        max(0, 2.0 ** (-((x - 0.6) ** 2) / 0.03)),  # Gas more likely farther out
        max(0, x - 0.5)  # Icy dominant in outer regions
    ]
    return random.choices(["rocky", "gas", "icy"], weights=weights, k=1)[0]


def _determine_planet_size(planet_type):
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
