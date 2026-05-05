from dataclasses import dataclass

@dataclass
class ResourceSlot:
    name: str
    quantity: float = 0.0
    max_capacity: float = 1000.0
    base_price: float = 10.0
    current_price: float = 10.0

class Colony:
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        
        # The "Filing Cabinet" of Resources (Dictionary of Dataclasses)
        self.stockpile = {
            "Food": ResourceSlot("Food", base_price=1.0),
            "Energy": ResourceSlot("Energy", base_price=1.0),
            "Minerals": ResourceSlot("Minerals", base_price=1.0),
            "Alloys": ResourceSlot("Alloys", base_price=10.0),
            "Consumer Goods": ResourceSlot("Consumer Goods", base_price=5.0)
        }

        # The Lists (Standardized Forms)
        self.buildings = {}  # Now a Dict per your Victoria 3 plan!
        self.pops = []       # Stays a list for diversity
        self.construction_queue = [] 
        
        # Essential Meta-Data
        self.stability = 100