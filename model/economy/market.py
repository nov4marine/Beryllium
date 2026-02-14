"""
Docstring for model.economy.market
"""

class Inventory:
    def __init__(self, capacity_volume):
        self.capacity_volume = capacity_volume # Does nothing right now 
        self.contents = {}
        # {resource: {"quantity": int, "capacity": int, "category": str}}

    def get_amount(self, resource):
        quantity = self.contents.get(resource, {"quantity": 0})["quantity"]
        capacity = self.contents.get(resource, {"capacity": 0})["capacity"]
        return {"quantity": quantity, "capacity": capacity}
    
    def update_capacity(self, resource, new_capacity):
        if resource not in self.contents:
            self.contents[resource] = {"quantity": 0, "capacity": 0}
        self.contents[resource]["capacity"] = new_capacity

    def add(self, resource, quantity):
        space_needed = quantity
        current_amount = self.contents.get(resource, {"quantity": 0})["quantity"]
        capacity = self.contents.get(resource, {"capacity": 0})["capacity"]
        if current_amount + space_needed <= capacity:
            if resource not in self.contents:
                self.contents[resource] = {"quantity": 0, "capacity": 0}
            self.contents[resource]["quantity"] += quantity
            return True
        else:
            print(f"Not enough space to add {quantity} of {resource}. Current: {current_amount}, Capacity: {capacity}")
            return False

    def remove(self, resource, quantity):
        current = self.get_amount(resource)["quantity"]
        if current >= quantity:
            self.contents[resource]["quantity"] -= quantity
            return True
        else:
            print(f"Not enough {resource} to remove. Current: {current}, Tried to remove: {quantity}")
            return False
        
    def summary(self):
        table = []
        for res, data in self.contents.items():
            table.append({
                "resource": res,
                "quantity": data["quantity"],
                "capacity": data["capacity"]
            })
        return table
    
    
class Market:
    def __init__(self, inventory):
        self.inventory = inventory
        #Configuration for each resource: (target_fill, min_price_mult, max_price_mult, base_price)
        self.market_configs = {} 
        self.price_history = {}  # resource -> list of past prices for graphing
        self.buy_reservations = {} # Ships coming to SELL to us (filling our stock)
        self.sell_reservations = {} # Ships coming to BUY from us (draining our stock)

        self.table = {} # For publishing market data to UI or other systems
        self.buy_offers = {}
        self.sell_offers = {}


    def set_config(self, resource, target = 0.5, min_mult=0.5, max_mult=2.0, base_price=10.0):
        self.market_configs[resource] = {
            "target": target,
            "min_mult": min_mult,
            "max_mult": max_mult,
            "base_price": base_price,
        }
        if resource not in self.price_history:
            self.price_history[resource] = []

    def get_price(self, resource):
        config = self.market_configs.get(resource)
        if not config:
            return None # Default if not managed
        
        current = self.inventory.get_amount(resource)["quantity"]
        cap = self.inventory.get_amount(resource)["capacity"]

        # Ratio of current stock vs what the station wants (clamped 0 to 1)
        #fill_ratio = min(current / (config["target"] * cap), 1.0)
        # Will reuse target logic later if wanted
        fill_ratio = current / cap if cap > 0 else 0
        
        # Price drops as inventory reaches target
        mult = config["max_mult"] - (fill_ratio * (config["max_mult"] - config["min_mult"]))
        return round(config["base_price"] * mult, 2)

    def publish_market_data(self):
        """The full 'State' of the market, probably for gui"""
        table = {}
        for res in self.market_configs:
            config = self.market_configs[res]
            price = self.get_price(res) # Ensure price is updated based on current stock
            current_amount = self.inventory.get_amount(res)["quantity"]
            capacity = self.inventory.get_amount(res)["capacity"]

            table[res] = {
                "price": price,
                "current_amount": current_amount,
                "capacity": capacity,
            }

        self.table = table

    def publish_offers(self):
        """publish price and quantity for buy/sell offers based on current market state and reservations."""
        buy_offers = {}
        sell_offers = {}
        for res in self.market_configs:
            price = self.get_price(res)
            effective_amount = self.get_effective_amount(res)
            capacity = self.inventory.get_amount(res)["capacity"]

            buy_offers[res] = {
                "price": price,
                "quantity": max(0, effective_amount) # We can only buy if we have stock to sell
            }
            sell_offers[res] = {
                "price": price,
                "quantity": max(0, capacity - effective_amount) # We can only sell if we have space to buy
            }
        self.buy_offers = buy_offers
        self.sell_offers = sell_offers

    def record_tick_history(self):
        for res in self.market_configs:
            price = self.get_price(res)
            self.price_history[res].append(price)
            # Keep only last 24 months
            if len(self.price_history[res]) > 24:
                self.price_history[res].pop(0)

    def get_effective_amount(self, resource):
        """Calculates 'Virtual' stock including ships currently in flight."""
        current = self.inventory.get_amount(resource)["quantity"]
        incoming = self.buy_reservations.get(resource, 0)
        outgoing = self.sell_reservations.get(resource, 0)
        # Price is calculated based on what the stock WILL be
        return current + incoming - outgoing

    def reserve_trade(self, resource, qty, is_buying_from_market):
        if is_buying_from_market:
            self.sell_reservations[resource] = self.sell_reservations.get(resource, 0) + qty
        else:
            self.buy_reservations[resource] = self.buy_reservations.get(resource, 0) + qty

    def execute_trade(self, resource, qty, is_buying_from_market):
        if is_buying_from_market:
            # Player is buying from market, so we remove from inventory
            success = self.inventory.remove(resource, qty)
            if success:
                self.sell_reservations[resource] -= qty
                
        else:
            # Player is selling to market, so we add to inventory
            success = self.inventory.add(resource, qty)
            if success:
                self.buy_reservations[resource] -= qty