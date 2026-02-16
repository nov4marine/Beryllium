import scipy.spatial
import networkx as nx
import random
import math
import os
from model.world.solar_system import SolarSystem



class Galaxy:
    def __init__(self, galaxy_size=6000, num_stars=1000):
        """THE HEART OF THE GALAXY GENERATION ALGORITHM BY HORUS LUPERCAL"""
        self.galaxy_size = galaxy_size # Maximum radius from center
        self.num_stars = num_stars

        # Step 1: Generate stars, and their respective solar systems
        self.galaxy_stars = self._generate_galaxy_stars(num_stars, galaxy_size)
        self.solar_systems = [s.solar_system for s in self.galaxy_stars]
        # Step 3: Generate hyperlanes
        self.hyperlanes = self.generate_prim_hyperlanes()

    def _generate_galaxy_stars(self, num_stars, galaxy_size):
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

            star = GalaxyStar(
                name=name,
                x=x,
                y=y,
                color=color,
                radius=radius,
                solar_system=SolarSystem(name=name),
            )
            stars.append(star)
        return stars

    def generate_delaunay_hyperlanes(self, max_connections=3):
        points = [(star.x, star.y) for star in self.galaxy_stars]
        tri = scipy.spatial.Delaunay(points)
        G = nx.Graph()
        star_connections = {point: [] for point in points}

        for simplex in tri.simplices:
            for i in range(3):
                start = points[simplex[i]]
                end = points[simplex[(i + 1) % 3]]
                distance = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)
                G.add_edge(start, end, weight=distance)

        mst_edges = list(nx.minimum_spanning_edges(G, algorithm="kruskal", data=False))
        for start, end in mst_edges:
            star_connections[start].append(end)
            star_connections[end].append(start)

        for simplex in tri.simplices:
            for i in range(3):
                start = points[simplex[i]]
                end = points[simplex[(i + 1) % 3]]
                if len(star_connections[start]) < max_connections and len(star_connections[end]) < max_connections:
                    star_connections[start].append(end)
                    star_connections[end].append(start)

        # Convert to GalaxyStar objects
        pos_to_star = {(star.x, star.y): star for star in self.galaxy_stars}
        hyperlanes = []
        for start in star_connections:
            for end in star_connections[start]:
                hyperlanes.append((pos_to_star[start], pos_to_star[end]))
        return hyperlanes

    def generate_prim_hyperlanes(self):
        points = [(star.x, star.y) for star in self.galaxy_stars]
        G = nx.Graph()
        for i, start in enumerate(points):
            for j, end in enumerate(points):
                if i == j:
                    continue
                distance = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)
                G.add_edge(start, end, weight=distance)
        mst = nx.minimum_spanning_tree(G, algorithm="prim", weight="weight")
        pos_to_star = {(star.x, star.y): star for star in self.galaxy_stars}
        hyperlanes = []
        for start, end in mst.edges:
            hyperlanes.append((pos_to_star[start], pos_to_star[end]))
        return hyperlanes

    def draw_sovereignty_voronoi(self, screen, camera):
        """Draw semi-transparent sovereignty regions using Voronoi polygons."""
        points = [(star.x, star.y) for star in self.galaxy_stars]
        if len(points) < 3:
            return  # Voronoi needs at least 3 points

        vor = scipy.spatial.Voronoi(points)
        # Map points to stars for color lookup
        pos_to_star = {(star.x, star.y): star for star in self.galaxy_stars}

        for point_idx, region_idx in enumerate(vor.point_region):
            region = vor.regions[region_idx]
            if -1 in region or len(region) == 0:
                continue  # Skip infinite regions

            polygon = [vor.vertices[i] for i in region]
            star = self.galaxy_stars[point_idx]
            # Choose color: use star.owner.color if available, else default
            if hasattr(star, "owner") and star.owner is not None:
                color = star.owner.color
            else:
                color = (120, 120, 120)  # Neutral/unclaimed

            # Make it semi-transparent
            overlay_color = (*color, 60)

            # Transform polygon points to screen coordinates
            screen_poly = [camera.apply(x, y) for x, y in polygon]

            # Draw the polygon on a temporary surface for alpha blending
            min_x = min(p[0] for p in screen_poly)
            min_y = min(p[1] for p in screen_poly)
            max_x = max(p[0] for p in screen_poly)
            max_y = max(p[1] for p in screen_poly)
            surf_w = int(max_x - min_x)
            surf_h = int(max_y - min_y)
            if surf_w < 1 or surf_h < 1:
                continue

    def deploy_nations(self, nations):
        # Select potential starting systems
        unowned_systems = [s for s in self.solar_systems if s.owner is None]

        if len(unowned_systems) < len(nations):
            print("Not enough unowned systems to place all empires.")
            return

        # Choose starting systems that are far apart
        # This is a simplified approach, a more complex version might use a
        # distance metric or a grid system.
        starting_systems = random.sample(unowned_systems, len(nations))

        for i, nation in enumerate(nations):
            system = starting_systems[i]
            system.owner = nation
            nation.solar_systems.append(system)
            print(f"Nation {nation.name} deployed to system {system.name}. Consequently, system owner is now {system.owner}")
            system.assign_capital(nation)

    def on_update(self, time_delta):
        for system in self.solar_systems:
            system.on_update(time_delta)  

    def on_live_update(self):
        pass
        #for system in self.solar_systems:
            #system.on_live_update()

    def on_daily_update(self):
        pass
        #for system in self.solar_systems:
            #system.on_daily_update()

    def on_monthly_update(self):
        pass
        #for system in self.solar_systems:
            #system.on_monthly_update()

class GalaxyStar:
    def __init__(self, name, x, y, color, radius, solar_system):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.solar_system = solar_system

    @property
    def owner(self):
        return self.solar_system.owner
