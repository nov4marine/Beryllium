"""
This module contains generator functions that are responsible for creating and registering
the world and all its entities.
Including but not limited to:
- Galaxy generation (star systems, planets)
- Nation generation (AI empires, player nation)
- Colony generation (assigning planets to nations, creating colonies)
- Building generation (creating buildings on colonies)
- Job generation (creating jobs within buildings)
- Pop generation (creating population units and assigning them to jobs)
etc.

All generator functions should use the central Universe to register the entities they create.

TODO: Pull all generation code out of the model and into this module.
- Galaxy
- Star Systems
- Planets
- Nations
- Colonies
- Buildings
- Jobs
- Pops
- Ships
"""

import scipy.spatial
import networkx as nx
import random
import math
import os
from model.world.solar_system import SolarSystem, Star, Planet, Moon
from model.economy.colony import Colony
from model.politics.nation import Nation

def generate_lifeless_galaxy(universe):
    #TODO: This will later be refactored into a more flexible system for custom galaxy generation.
    num_stars = 1000
    galaxy_size = 6000  # Max radius from center
    star_uids = []
    star_colors = [
        (255, 255, 0), (255, 0, 0), (0, 255, 0),
        (0, 0, 255), (255, 255, 255)
    ]
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

        # Assign random attributes to the star
        radius = random.randint(20, 30)
        color = random.choice(star_colors)
        name = f"star {i + 1}"

        star = SolarSystem(
            name=name,
            galaxy_x=x,
            galaxy_y=y,
            # Will probably get rid of color and radius, and have the solar system
            # itself handle them.
            color=color,
            radius=radius, # TODO: star radius, must be changed to size of system
        )

        stars.append(star)
        sys_id = universe.register_solar_system(star)
        star_uids.append(sys_id)
        fill_system_with_planets(universe, sys_id)
        
    return star_uids

def fill_system_with_planets(universe, solar_system_id):
    system = universe.get_solar_system[solar_system_id]

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
        name=f"{system.name} Star",
        star_type=star_type,
        radius=0,  # At system center (0,0), so radius is not relevant for orbital calculations
        size=random.randint(*star_size_range[star_type]),
        color=None,  # Will be set by Star class based on type
        angle=0,
        speed=0,
        parent=None
    )
    bodies.append(star)
    star_id = universe.register_celestial_body(star, solar_system_id, parent_id=None)

    # --- Generate planets ---
    num_planets = random.randint(4, 10)  # Random number of planets
    solar_system_size = (600 * ((num_planets + 1) ** 1.8)) + (star.size * 4)
    system.solar_system_size = solar_system_size
    for i in range(num_planets):
        orbital_radius = 600 * ((i + 1) ** 1.8) + star.size * 4 # Exponential spacing. Orbital radius is distance from star. v1 is 600 * (1.5 ** i)
        distance_ratio = orbital_radius / solar_system_size
        planet_type = _determine_planet_type(distance_ratio) # "rocky", "gas", or "icy"
        size = _determine_planet_size(planet_type)
        color = None  # Let Planet class pick based on type, or randomize here
        speed = 2 / orbital_radius * 0.5
        angle = random.uniform(0, 2 * math.pi)
        name = f"{system.name} Planet {i + 1}"
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
        planet_id = universe.register_celestial_body(planet, solar_system_id = solar_system_id, parent_id=star_id)

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
                    parent=planet
                )
                bodies.append(moon)
                moon_id = universe.register_celestial_body(moon, solar_system_id=solar_system_id, parent_id=planet_id)

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
                    parent=planet
                )
                bodies.append(moon)
                moon_id = universe.register_celestial_body(moon, solar_system_id=solar_system_id, parent_id=planet_id)

# Dynamic Entity Creation and Registration
# Which means living things like nations, colonies, buildings, jobs, and pops.
def spawn_homeworld_colony(universe, nation_id, planet_id):
    # 1. Create the colony
    new_colony = Colony(name="New Terra")
    new_colony.owner_id = nation_id  # The 'Fingerprint'
    
    # Register it in the warehouse
    col_id = universe.register_colony(new_colony, planet_id)
    
    # We DON'T do: nation.colony_ids.append(col_id)
    # The Nation will find this colony automatically via its property!

def create_nation(universe, name):
    new_nation = Nation(name)
    nation_id = universe.register_nation(new_nation)
    return nation_id

def create_colony(universe, nation_id, planet_id):
    new_colony = Colony(name="New Terra")
    new_colony.owner_id = nation_id  # The 'Fingerprint'
    
    # Register it in the warehouse
    col_id = universe.register_colony(new_colony, planet_id)
    
    # We DON'T do: nation.colony_ids.append(col_id)
    # The Nation will find this colony automatically via its property!

# TODO: get the template below working. 
def spawn_colony_with_pops(universe, planet_id):
    pass
    # 1. Create the colony
    new_colony = None#Colony(name="New Hope")
    colony_id = universe.register_colony(new_colony, planet_id)

    # 2. Create the pops and 'inject' the universe
    for _ in range(3):
        # We hand the pop the universe it belongs to
        new_pop = None#Pop(universe_reference=universe)
        universe.register_pop(new_pop, colony_id=colony_id)

# Helper functions for planet generation
def _determine_planet_type(distance_ratio):
    x = distance_ratio
    weights = [
        max(0, 1.0 - x * 2),  # Rocky more likely closer in
        max(0, 2 ** (-((x-0.6) ** 2) / 0.03)),  # Gas more likely farther out
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
