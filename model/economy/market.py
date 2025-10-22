class Market:
    def __init__(self, members=None):
        self.members = members
        self.goods = {}  # name: Good instance

    def add_good(self, good):
        self.goods[good.name] = good

    def update_prices(self):
        """Adjust prices based on supply and demand."""
        k = 1.5  # Elasticity of prices
        price_min = 0.1
        price_max = 4.0

        for good in self.goods.values():
            if good.supply + good.demand == 0:
                sdr = 1.0
            else:
                sdr = good.supply / good.demand

            new_price = good.base_price * (sdr ** -k)
            good.current_price = max(price_min * good.base_price, min(new_price, price_max * good.base_price))

    def reset_market_data(self):
        """Reset supply and demand for the monthly tick"""
        for good in self.goods.values():
            good.supply = 0
            good.demand = 0

    def buy_good(self, name, quantity):
        good = self.goods[name]
        if not good:
            raise ValueError(f"Good '{name}' not found in market.")
        good.demand += quantity
        return good.current_price * quantity

    def sell_good(self, name, quantity):
        good = self.goods[name]
        if not good:
            raise ValueError(f"Good '{name}' not found in market.")
        good.supply += quantity
        return good.current_price * quantity
    
    def _setup_default_goods(self):
        # Basic Goods
        self.add_good(Good(name="Food", category="Basic", base_price=20))
        self.add_good(Good(name="Energy", category="Basic", base_price=20))
        self.add_good(Good(name="Minerals", category="Basic", base_price=30))
        # Manufactured Goods
        self.add_good(Good(name="Alloys", category="Manufactured", base_price=100))
        self.add_good(Good(name="Consumer Goods", category="Manufactured", base_price=50))
        self.add_good(Good(name="Robotics", category="Manufactured", base_price=160))
        # Luxury Goods
        self.add_good(Good(name="Luxury Goods", category="Luxury", base_price=200))
        # Government
        self.add_good(Good(name="Unity", category="Government", base_price=55))
        # Services
        self.add_good(Good(name="Amenities", category="Services", base_price=17))
        self.add_good(Good(name="Healthcare", category="Services", base_price=30))
        # Strategic Resources
        self.add_good(Good(name="Strategic Resources", category="Strategic", base_price=210))

    # Goods should have tiers within each category that represent value or how advanced they are.
    # Eg. cheap/basic - standard/middle - luxury/advanced

    # Goods could be categorized based on applications: Foods, consumer goods, tools, services, 
    # Housing, Education(?), Healthcare, Entertainment, energy(?), leisure, transportation etc.


class Good:
    def __init__(self, name, category, base_price):
        self.name = name
        self.category = category
        self.base_price = base_price
        self.current_price = base_price
        self.supply = 0
        self.demand = 0
