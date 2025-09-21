import arcade.color
from model.economy.colony import Colony
from model.economy.market import Market


class Nation:
    def __init__(self, name):
        self.name = name
        self.color = arcade.color.BLUE
        self.population = 10000000
        self.gdp = 1000
        self.gdp_per_capita = 0
        self.standard_of_living = 0
        self.radicals = 0
        self.loyalists = 0

        self.planets = []  # List of all colonized worlds under control of this nation
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

    def update_economy(self):
        for colony in self.planets:
            colony.run_local_economy()

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
