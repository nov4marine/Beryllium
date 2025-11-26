class Market:
    def __init__(self, members=None):
        self.members = members
        self.goods = {}  # name: Good instance
        self._setup_default_goods()

    def add_good(self, good):
        self.goods[good.name] = good

    def update_prices(self):
        """Adjust prices based on supply and demand."""
        k = 1.5  # Elasticity of prices
        price_min = 0.1
        price_max = 4.0

        for good in self.goods.values():
            if good.demand == 0 or good.supply == 0:
                sdr = 1.0
            else:
                sdr = good.supply / good.demand
                print(f"Good: {good.name}, Supply: {good.supply}, Demand: {good.demand}, SDR: {sdr:.2f}")

            new_price = good.base_price * (sdr ** -k)
            good.current_price = max(price_min * good.base_price, min(new_price, price_max * good.base_price))

    def log_data(self):
        """Log current market data for analysis and display."""
        data_snapshot = {}
        for good in self.goods.values():
            data_snapshot[good.name] = {
                "price": good.current_price,
                "supply": good.supply,
                "demand": good.demand
            }
        return data_snapshot

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
        total_cost = good.current_price * quantity
        return total_cost

    def sell_good(self, name, quantity):
        good = self.goods[name]
        if not good:
            raise ValueError(f"Good '{name}' not found in market.")
        good.supply += quantity
        total_revenue = good.current_price * quantity
        return total_revenue
    
    def get_current_price(self, good):
        if good in self.goods:
            return self.goods[good].current_price
        else:
            raise ValueError(f"Good '{good}' not found in market.")
        
    def get_base_price(self, good):
        if good in self.goods:
            return self.goods[good].base_price
        else:
            raise ValueError(f"Good '{good}' not found in market.")
        
    def get_expensive_goods(self, number=5):
        """Return a list of the n most expensive goods in the market."""
        sorted_goods = sorted(self.goods.values(), key=lambda g: g.current_price, reverse=True)
        return sorted_goods[:number]
    
    def get_cheap_goods(self, number=5):
        """Return a list of the n cheapest goods in the market."""
        sorted_goods = sorted(self.goods.values(), key=lambda g: g.current_price)
        return sorted_goods[:number]
        
    def on_monthly_update(self):
        self.reset_market_data()
        self.update_prices()
    
    def _setup_default_goods(self):
        # Basic Goods
        self.add_good(Good(name="Food", category="Basic", base_price=20))
        self.add_good(Good(name="Energy", category="Basic", base_price=20))
        self.add_good(Good(name="Minerals", category="Basic", base_price=30))
        # Manufactured Goods
        self.add_good(Good(name="Alloys", category="Manufactured", base_price=100))
        self.add_good(Good(name="Consumer Goods", category="Manufactured", base_price=50))
        self.add_good(Good(name="Robotics", category="Manufactured", base_price=160))
        self.add_good(Good(name="Housing", category="Manufactured", base_price=60))
        # Luxury Goods
        self.add_good(Good(name="Luxury Goods", category="Luxury", base_price=200))
        # Government
        self.add_good(Good(name="Unity", category="Government", base_price=55))
        self.add_good(Good(name="Research", category="Government", base_price=75))
        self.add_good(Good(name="Stability", category="Government", base_price=150))
        # Services
        self.add_good(Good(name="Services", category="Services", base_price=20))
        self.add_good(Good(name="Amenities", category="Services", base_price=17))
        self.add_good(Good(name="Healthcare", category="Services", base_price=30))
        self.add_good(Good(name="Education", category="Services", base_price=20))
        self.add_good(Good(name="Transportation", category="Services", base_price=40))
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

class NationalMarket(Market):
    def __init__(self, nation):
        super().__init__(members=[nation])
        self.nation = nation

    def synchronize_markets(self):
        # 1. Aggregate supply and demand from all colonies
        total_supply = {}
        total_demand = {}
        for colony in self.colonies:
            for good, market_good in colony.local_market.goods.items():
                total_supply[good] = total_supply.get(good, 0) + market_good.supply
                total_demand[good] = total_demand.get(good, 0) + market_good.demand

        # 2. Set national market supply/demand
        for good in self.national_market.goods:
            self.national_market.goods[good].supply = total_supply.get(good, 0)
            self.national_market.goods[good].demand = total_demand.get(good, 0)

        # 3. Calculate new prices (implement your price formula here)
        self.national_market.update_prices()

        # 4. Push prices back to all colonies
        for colony in self.colonies:
            for good in colony.local_market.goods:
                colony.local_market.goods[good].current_price = self.national_market.goods[good].current_price