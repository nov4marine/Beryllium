import scipy.spatial
import networkx as nx
import random
import math
import os


class Galaxy:
    def __init__(self, galaxy_size=6000, num_stars=1000, solar_system_uids=None, universe=None):
        """THE HEART OF THE GALAXY GENERATION ALGORITHM BY HORUS LUPERCAL
        The Galaxy class now stores only UIDs for solar systems.
        To access the actual SolarSystem objects, use the solar_systems property,
        which looks them up in the Universe table.
        """

        self.galaxy_size = galaxy_size # Maximum radius from center
        self.num_stars = num_stars
        self.solar_system_uids = solar_system_uids if solar_system_uids is not None else []
        self.universe = universe

        # Step 3: Generate hyperlanes
        self.hyperlanes = self.generate_prim_hyperlanes()

    @property
    def solar_systems(self):
        return [self.universe.get_solar_system(uid) for uid in self.solar_system_uids]

    def generate_delaunay_hyperlanes(self, max_connections=3):
        points = [(star.galaxy_x, star.galaxy_y) for star in self.solar_systems]
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
        pos_to_star = {(star.galaxy_x, star.galaxy_y): star for star in self.solar_systems}
        hyperlanes = []
        for start in star_connections:
            for end in star_connections[start]:
                hyperlanes.append((pos_to_star[start], pos_to_star[end]))
        return hyperlanes

    def generate_prim_hyperlanes(self):
        points = [(star.galaxy_x, star.galaxy_y) for star in self.solar_systems]
        G = nx.Graph()
        for i, start in enumerate(points):
            for j, end in enumerate(points):
                if i == j:
                    continue
                distance = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)
                G.add_edge(start, end, weight=distance)
        mst = nx.minimum_spanning_tree(G, algorithm="prim", weight="weight")
        pos_to_star = {(star.galaxy_x, star.galaxy_y): star for star in self.solar_systems}
        hyperlanes = []
        for start, end in mst.edges:
            hyperlanes.append((pos_to_star[start], pos_to_star[end]))
        return hyperlanes

    def draw_sovereignty_voronoi(self, screen, camera):
        """Draw semi-transparent sovereignty regions using Voronoi polygons."""
        points = [(star.galaxy_x, star.galaxy_y) for star in self.solar_systems]
        if len(points) < 3:
            return  # Voronoi needs at least 3 points

        vor = scipy.spatial.Voronoi(points)
        # Map points to stars for color lookup
        pos_to_star = {(star.galaxy_x, star.galaxy_y): star for star in self.solar_systems}

        for point_idx, region_idx in enumerate(vor.point_region):
            region = vor.regions[region_idx]
            if -1 in region or len(region) == 0:
                continue  # Skip infinite regions

            polygon = [vor.vertices[i] for i in region]
            star = self.solar_systems[point_idx]
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

    def get_starting_systems(self, number_of_nations):
        # Select potential starting systems
        unowned_systems = [s for s in self.solar_systems if s.owner is None]

        if len(unowned_systems) < number_of_nations:
            print("Not enough unowned systems to place all empires.")
            return

        # Choose starting systems that are far apart
        # This is a simplified approach, a more complex version might use a
        # distance metric or a grid system.
        starting_systems = random.sample(unowned_systems, number_of_nations)

        # return the actual SolarSystem objects for the chosen UIDs that are unowned
        return starting_systems
    
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
