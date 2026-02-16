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
from model.world.solar_system import SolarSystem

def generate_lifeless_galaxy(universe):
    #TODO: This will later be refactored into a more flexible system for custom galaxy generation.
    num_stars = 1000
    galaxy_size = 6000  # Max radius from center
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
            radius=radius,
        )

        stars.append(star)
        sys_id = universe.register_solar_system(star)
        fill_system_with_planets(universe, sys_id)

def fill_system_with_planets(universe, solar_system_id):
    