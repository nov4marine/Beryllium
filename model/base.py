import itertools

_id_counter = itertools.count(1)

def get_unique_id():
    return next(_id_counter)

# ------ Catalog Class ------

# This file defines the Catalog for your game economy.
# The Catalog is just a place to store all the types of goods and buildings in your game.
# You can add new goods and buildings here, and then use them anywhere in your game.

# uhhh, chat GPT seems to have had a stroke here. This file is basically empty for now, might become 
# Some sort of defines for goods techs buildings etc later.

# UPDATE! Actually we are gonna add all the classes that need to be shared with Godot here. "object": id mappings for things like buildings, units, resources, etc.
# This way we can serialize them easily and Godot can know what to do with them.
# This might technically be redundant with other code that already serializes, but at a minimum this will be a single source of truth for all class mappings,
# and will make it easier to add new types of things later. It also centralizes and in the future could replace the existing serialization code.

class Catalog:
    def __init__(self):
        self.galaxy = {}         # {id: galaxy_obj}
        self.galaxy_stars = {}   # {id: galaxy_star_obj}
        self.solar_systems = {}  # {id: system_obj}
        self.celestial_bodies = {} # {id: body_obj}
        
        self.nations = {}        # {id: nation_obj}
        self.fleets = {}         # {id: fleet_obj}
        self.colonies = {}       # {id: colony_obj}
        self.buildings = {}   # Add this
        self.pops = {}        # And this
        self.jobs = {}        # And this

    # --- Registration ---
    def register(self, obj):
        """Register any object with an 'id' and a catalog_type attribute."""
        if hasattr(obj, "catalog_type") and hasattr(obj, "id"):
            getattr(self, obj.catalog_type)[obj.id] = obj

    # --- Retrieval ---
    def get(self, catalog_type, obj_id):
        """Retrieve an object by type and id."""
        return getattr(self, catalog_type).get(obj_id)

    # --- Example: Query all colonies for a nation ---
    def get_colonies_by_nation(self, nation_id):
        return [colony for colony in self.colonies.values() if colony.nation_id == nation_id]
    
catalog = Catalog()
