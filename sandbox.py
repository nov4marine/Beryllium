class Pop:
    # Standard pop size for which needs are defined (like Victoria 3's 10,000)
    POP_UNIT_SIZE = 10_000

    def __init__(self, colony, size, current_job=None):
        self.colony = colony
        self.size = size
        self.current_job = current_job

        self.wage = current_job.wage if current_job else 10
        self.wealth = 1.0
        self.needs = {}

    def update(self):
        pass
        self.calculate_needs()
        self.fulfill_needs(self.colony.local_market)
        self.evaluate_job_market(self.colony.job_offers)

    def calculate_needs(self):
        """
        Calculate needs for a pop of POP_UNIT_SIZE, then scale when fulfilling needs.
        This makes balancing easier and matches Victoria 3's approach.
        """
        base_size = self.POP_UNIT_SIZE
        # Needs for a standard pop unit
        consumption = {
            # Core sustenance needs. Diminishing growth
            "Food": 5 + (self.wealth * 0.5) ** 0.3,  # Base food need with a wealth factor
            "Consumer Goods": 2 + (self.wealth * 0.5) ** 0.5,  # Base clothing and other durable goods need with a wealth factor
            "Housing": 3 + (self.wealth * 1) ** 1,  # Base housing need with a wealth factor
            # Quality of life needs. Linear-ish growth
            "Consumer Goods": max(0, (self.wealth * 0.5) * 1),  # Consumer goods increases linearly
            "Services": 1 + (self.wealth * 0.15) ** 1.5,
            "Amenities": self.wealth * 0.012 ** 1.5,
            # Luxury needs. exponential growth
            # high quality services, amenities, transportation, clothing, food, housing, etc.
            "Luxury Goods": max(0, int(self.wealth - 15) ** 2),  # Luxury goods need grows exponentially with wealth
        }
        self.needs = consumption

        AVERAGE_WEALTH_NEEDS_PARAMETERS = {
            # Average needs for average income/wealth levels
        # Good: [Base (Subsistence), Scaling Factor (alpha), Wealth Elasticity Exponent (beta), Price Elasticity (ei) (1 for now)]
        "Food":             [15.0, 0.30, 0.8],  # Necessity (beta < 1)
        "Housing":          [30.0, 0.30, 1.0],  # Strong Necessity
        "Consumer Goods":   [12.0, 0.30, 1.0],  # Base necessity component
        "Services":         [8.0,  0.015, 1.1], # Normal Good (beta ~ 1)
        "Education":        [2.0, 0.10, 0.7],  # Necessity
        "Energy":           [6.0, 0.20, 0.8],  # Necessity
        "Amenities":        [5,  0.10, 1.5],  # Luxury (beta > 1)
        "Healthcare":       [10,  0.10, 0.8],  # Necessity
        "Transportation":   [15,  0.15, 1.3],  # Luxury (No base need)
        "Luxury Goods":     [0.0,  0.15, 1.5],  # Strong Luxury (No base need)
        }

        NEEDS_PARAMETERS = {
            # Quantities this time, assuming base prices, rather than percentages
            "Food": 0.75,
            "Housing": 0.50,
            "Consumer Goods": 0.30,
            "Services": 0.40, 
            "Education": 0.10,
            "Energy": 0.30,
            "Amenities": 0.30,
            "Healthcare": 0.33,
            "Transportation": 0.35,
        }

        # subsistence_wealth/income = roughly 10 assuming base prices

        # Subsistence goods needed for basic survival in a Stellaris setting
        Subsistence_needs = {
            "Food": 4,
            "Housing": 4,
            "Consumer Goods": 1,
            "Energy": 1,
            "Healthcare": 1,
        }

        actual_needs_parameters = {
        # Good: [Base (Subsistence), Scaling Factor (alpha), Wealth Elasticity Exponent (beta), Price Elasticity (ei) (1 for now)]
            "Food": [4.0, 0.27, 0.8, 1.0],
            "Housing": [4.0, 0.27, 1.0, 1.0],
            "Consumer Goods": [1.0, 0.11, 1.0, 1.0],
            "Services": [1.0, 0.04, 1.1, 1.0],
            "Education": [0, 0.12, 0.7, 1.0],
            "Energy": [1.0, 0.12, 0.8, 1.0],
            "Amenities": [0, 0.02, 1.5, 1.0],
            "Healthcare": [1.0, 0.22, 0.8, 1.0],
            "Transportation": [0, 0.06, 1.2, 1.0],
            "Luxury Goods": [0, 0.01, 1.5, 1.0],
        }

        # I'm just now realizing all these numbers are assuming all goods/services are priced at 1 equally
        # Which I guess is fine since I accidentally used percentages of income anyway

        # scaling_factor = (consumption - subsistence) / (wealth ** beta)

    def fulfill_needs(self, market):
        # Scale needs by (actual size / pop unit size)
        scale = self.size / self.POP_UNIT_SIZE
        for good, quantity in self.needs.items():
            market.buy_good(good, quantity * scale)

    def evaluate_job_market(self, job_board):
        """Looks for a job and 'applies' if it meets criteria."""
        application_pool = []

        # Simple wage-based evaluation
        for job_offer in job_board:
            # Check if wage is significantly higher
            if job_offer["wage"] > self.wage * 1.2:
                application_pool.append({
                    "pop_group": self,
                    "quantity_applying": self.size,
                    "job_offer": job_offer
                })

        return application_pool

    def split(self, amount):
        """
        Splits 'amount' individuals from this pop and returns a new Pop instance.
        The current pop's size is reduced by 'amount'.
        """
        if amount > self.size:
            raise ValueError("Not enough individuals to split!")
        self.size -= amount
        new_pop = Pop(self.colony, amount)
        new_pop.wealth = self.wealth
        return new_pop
    
pop = Pop(colony=None, size=10_000)
pop.wealth = 100
pop.calculate_needs()
print(pop.needs)  # Display calculated needs
