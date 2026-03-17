import arcade.color
from model.economy.colony import Colony
from model.economy.market import Market

class Nation:
    def __init__(self, name):
        self.name = name
        self.color = arcade.color.BLUE
        self.population = 1200000 # 1.2 million initial population, buildings each 10k, for 120 buildings
        self.gdp = 10000
        self.gdp_per_capita = 0
        self.standard_of_living = 0
        self.radicals = 0
        self.loyalists = 0

        self.planets = []  # List of all colonized worlds under control of this nation
        self.colonies = []  # List of all colonies on planets
        self.solar_systems = []  # List of all owned solar systems
        self.capital = None

        self.bureaucracy = 0
        self.authority = 0
        self.treasury = 1000

        self.national_market = Market()

    def initialize_nation(self):
        if self.capital is None:
            print("Horus error: nation capital is None")
            return
        else:
            print("deploying capital...")
            self.capital.colony = Colony(self.capital, self, self.capital.name)
            capital_colony = self.capital.colony
            self.capital = capital_colony
            self.capital.setup_capital()
            self.colonies.append(self.capital)

    def setup_capital(self, planet):
        """TODO: Currently unsed template for future refactoring of capital setup logic."""
        self.capital = planet
        colony = Colony(planet, self, planet.name)
        colony.setup_capital()
        self.colonies.append(colony)
        self.planets.append(planet)

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

    def update_economy(self):
        for planet in self.planets:
            if planet.colony is not None:
                colony = planet.colony
                colony.on_monthly_update()
        self.synchronize_markets()

    def colonize(self, planet):
        planet.colony = Colony(planet, self, planet.name)

    def on_monthly_update(self):
        """The monthly update loop for the nation."""
        pass
        self.update_economy()
        self.gdp_per_capita = self.gdp / self.population if self.population > 0 else 0

    def on_daily_update(self):
        """The daily update loop for the nation."""
        pass

class NationStub:
    "refactor in progress"
    def __init__(self, name, color="red"):
        self.uid = None # Set by Universe.register
        self.name = name
        self.color = color
        self.capital_id = None
        self.treasury = 1000
        

    # --- THE QUERIES ---
    # These properties look like lists, but they are live 'Census' searches.
    
    @property
    def systems(self, universe):
        """Get every system I own."""
        return [s for s in universe.solar_systems.values() if s.owner_id == self.uid]

    @property
    def colonies(self, universe):
        """Get every colony I own."""
        return [c for c in universe.colonies.values() if c.owner_id == self.uid]

    @property
    def total_population(self, universe):
        """A social-science metric calculated on the fly."""
        return sum(c.population(universe) for c in self.colonies(universe))