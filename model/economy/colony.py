from model.economy.market import Market


class Colony:
    """mega class to represent a colonized world"""

    def __init__(self, planet, owner, name):
        self.planet = planet  # Reference to which planet it is on
        self.owner = owner  # Owning nation
        self.name = name  # Name of colonized world
        self.national_market = owner.national_market

        self.pops = []
        self.total_population = 0
        self.buildings = []
        self.jobs = []
        self.job_offers = []  # Job Board

        self.construction_queue = []

        self.stability = 100
        self.unemployed = 0
        self.local_bank = None
        self.local_market = Market()

    def run_local_economy(self):
        """This method aggregates all logic for the monthly economy tick"""
        # --- Step 1: Labor Market ---
        self.run_job_board()
        application_pool = []
        for pop in self.pops:
            applications = pop.evaluate_job_market(self.job_offers)
            application_pool.extend(applications)

        if not application_pool:
            return

        for job_offer in self.job_offers:
            job = job_offer["job"]
            applicants = [app for app in application_pool if app["job_offer"]["job"] == job]
            job.hire_pops(applicants)

        # --- Step 2: Production and Wages ---
        for building in self.buildings:
            building.operate()
        # --- Step 3: Consumption and Pop Needs ---
        for pop in self.pops:
            pop.purchase_needs()
        # --- Step 4: Update Market Prices ---
        for good in self.local_market.goods:
            pass

    def run_job_board(self):
        """Aggregates all job vacancies on the planet."""
        job_board = []
        for building in self.buildings:
            for job in building.jobs:
                if job.vacancies > 0:
                    job_offer = {
                        "job": building.job,
                        "employer_name": building.name,
                        "wage": building.job.wage,
                        "vacancies": building.job.vacancies,
                        "qualifications": building.job.qualifications
                    }
                    job_board.append(job_offer)
        self.job_offers = job_board

    def setup_capital(self):
        print(f"capital deployed on planet {self.planet.name}. Nation color is {self.owner.color}")
        self.buildings = []


class Building:
    """A building on a colony, which can produce goods and services, employ pops, and generate profit"""

    def __init__(self, name, construction_cost, construction_time, upkeep, inputs, outputs, jobs=None, levels=0,
                 colony=None):
        self.name = name,
        self.construction_cost = construction_cost
        self.construction_time = construction_time
        self.upkeep = upkeep
        self.inputs = inputs
        self.outputs = outputs
        self.jobs = jobs
        self.levels = levels
        self.colony = colony

        self.revenue = 0
        self.expenses = 0
        self.profit = 0
        self.ownership = {"total": 0, "private": 0, "government": 0, "workers": 0}

    def add_level(self, funder):
        """Add a level of the building, owned by the funder"""
        self.levels += 1
        self.ownership[funder] += 1
        self.ownership["total"] += 1

    def operate(self):
        """Operate the building for a tick, processing goods, paying wages, and allocating profits."""
        # Reset for the tick
        self.revenue = 0
        self.expenses = 0
        self.profit = 0

        self.process_goods()
        self.pay_workers()
        self.allocate_profit()

    def process_goods(self):
        job_staffing = []
        for job in self.jobs:
            staffing = job.employees / job.max_quantity
            job_staffing.append(staffing)

        total_staffing = sum(job_staffing) / len(job_staffing)

        for good, quantity in self.inputs.items():
            total_inputs = quantity * total_staffing * self.levels
            self.expenses += self.colony.local_market.buy_good(good, total_inputs)

        for good, quantity in self.outputs.items():
            total_outputs = quantity * total_staffing * self.levels
            self.revenue += self.colony.local_market.sell_good(good, total_outputs)

    def pay_workers(self):
        for job in self.jobs:
            self.expenses += (job.wage * job.employees)

    def allocate_profit(self):
        self.profit = self.revenue - self.expenses
        if self.profit >= 0:
            dividends = self.profit
            pass


class Job:
    def __init__(self, profession, max_quantity, employer, wage=10, qualifications=None):
        self.profession = profession
        self.max_quantity = max_quantity  # maximum number of jobs in this position
        self.employees = 0  # Total number of individuals
        self.vacancies = max_quantity
        self.assigned_pops = []  # list of pop objects assigned
        self.employer = employer  # parent building
        self.wage = wage
        self.qualifications = qualifications

    def adjust_wages(self):
        pass

    def hire_pops(self, applicants):
        """Hires Pops from the application pool until vacancies are filled."""
        # A list to store the Pops that successfully got a job
        hired_pops = []

        # Sort applicants by a simple criterion (e.g., highest wealth)
        applicants.sort(key=lambda x: x["pop_group"].wealth, reverse=True)

        # Iterate through applicants and hire until vacancies are filled
        for applicant in applicants:
            if self.vacancies > 0:
                pop_group = applicant["pop_group"]
                quantity_to_hire = min(self.vacancies, applicant["quantity_applying"])

                # Update the pop group's job status and quantity
                new_pop_group = pop_group.split(quantity_to_hire)
                new_pop_group.current_job = self
                new_pop_group.current_wage = self.wage

                self.vacancies -= quantity_to_hire
                hired_pops.append(new_pop_group)

        return hired_pops


class Pop:
    # Standard pop size for which needs are defined (like Victoria 3's 10,000, but here 100,000)
    POP_UNIT_SIZE = 10_000_000

    def __init__(self, colony, size, current_job=None):
        self.colony = colony
        self.size = size
        self.current_job = current_job

        self.wage = current_job.wage if current_job else 10
        self.wealth = 1.0
        self.needs = {}

    def update(self):
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
            "Food": 5 + (self.wealth * 0.08) ** 0.3,  # Base food need with a wealth factor
            "Consumer Goods": 2 + (self.wealth * 0.05) ** 0.5,  # Base clothing and other durable goods need with a wealth factor
            "Housing": 3 + (self.wealth * 0.06) ** 0.7,  # Base housing need with a wealth factor
            # Quality of life needs. Linear-ish growth
            "Consumer Goods": max(0, (self.wealth - 50) * 0.02),  # Consumer goods increases linearly
            "Services": 1 + (self.wealth * 0.015) ** 1.05,
            "Amenities": max(0, (self.wealth - 80) * 0.012) ** 1.1,
            # Luxury needs. exponential growth
            # high quality services, amenities, transportation, clothing, food, housing, etc.
            "Luxury Goods": max(0, int(self.wealth * 0.1)),
        }
        self.needs = consumption

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

############################################################################
#now the actual buildings and jobs for the colony
############################################################################

# With the help of chatgpt, I have come up with a formula for balancing capital and labor intensity:

# For a building:
# total_investment = construction_cost + (upkeep * N_ticks) + (sum(input_goods.values()) * N_ticks)
# labor_investment = jobs * wage * N_ticks

# Capital-to-labor ratio (K/L)
# capital_intensity = total_investment / max(labor_investment, 1)

# Profit per tick (simplified)
# profit_per_tick = (output_value - input_cost - upkeep - total_wages)

# Gonna initially aim for 5 million workers per building level
# Also Gonna initially aim to just copy Stellaris, and add my own flavor as we go.
# When in doubt, use Labor Theory of Value
# Stellaris Buildings:
    # Tier 1: upkeep 2, time 360, minerals 400
    # Tier 2: upkeep 5 + 1 rare, time 480, minerals 600 + 50 rare
    # Tier 3: upkeep 8 + 2 rare, time 600, minerals 800 + 100 rare

    # districts: upkeep 1, time 240, minerals 300

#input and output goods should be a list of dictionaries
# Remember to convert upkeep cost from energy credits to construction points later

class MineralExtractor(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Miner", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Mineral Extractor",
            construction_cost=300,
            construction_time=240,
            upkeep=1,
            inputs={},
            outputs={"Minerals": 4},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class EnergyPlant(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Engineer", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Energy Plant",
            construction_cost=300,
            construction_time=240,
            upkeep=1,
            inputs={},
            outputs={"Energy": 6},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class Farm(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Farmer", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Farm",
            construction_cost=300,
            construction_time=240,
            upkeep=1,
            inputs={},
            outputs={"Food": 5},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class CityDistrict(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Urban Worker", max_quantity=10000000, employer=self)]
        super().__init__(
            name="City District",
            construction_cost=300,
            construction_time=240,
            upkeep=1,
            inputs={},
            outputs={"Housing": 5},
            jobs=jobs,
            levels=0,
            colony=colony
        )

# Now some tier 2 buildings

class ResearchLab(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Scientist", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Research Lab",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={"Consumer Goods": 2},
            outputs={"Research": 10},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class Factory(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Factory Worker", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Factory",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={"Minerals": 6,},
            outputs={"Consumer Goods": 6},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class AlloyFoundry(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Metallurgist", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Alloy Foundry",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={"Minerals": 6},
            outputs={"Alloys": 3},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class AdministrationCenter(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Administrator", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Administration Center",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={"Consumer Goods": 2},
            outputs={"Stability": 5, "Unity": 4},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class HoloTheater(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Entertainer", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Holo-Theater",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={"Consumer Goods": 1},
            outputs={"Amenities": 10},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class HydroponicsFarm(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Hydroponic Farmer", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Hydroponics Farm",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={"Energy": 4},
            outputs={"Food": 6},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class HealthClinic(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Doctor", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Health Clinic",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={"Consumer Goods": 1},
            outputs={"Health Services": 10}, # in stellaris, output is 4 amenities, 5% growth, and 2.5% habitability
            jobs=jobs,
            levels=0,
            colony=colony
        )

class Spaceport(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Dockworker", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Spaceport",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={"Alloys": 2, "Energy": 2},
            outputs={"Trade": 10},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class RoboticsFactory(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Robotics Engineer", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Robotics Factory",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={"Alloys": 2},
            outputs={"Robots": 2},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class EnforcementCenter(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Law Enforcer", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Enforcement Center",
            construction_cost=400,
            construction_time=360,
            upkeep=2,
            inputs={},
            outputs={"Stability": 10},
            # In Stellaris, each enforcer produces 1 stability, -25 crime, and 2 defense army
            jobs=jobs,
            levels=0,
            colony=colony
        )

# Special Resource Buildings

class Refinery(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Refinery Worker", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Refinery",
            construction_cost=500,
            construction_time=480,
            upkeep=3,
            inputs={"Rare Minerals": 10},
            outputs={"Exotic Goods": 2},
            jobs=jobs,
            levels=0,
            colony=colony
        )

class Harvester(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Harvester Operator", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Harvester",
            construction_cost=200,
            construction_time=360,
            upkeep=1,
            inputs={},
            outputs={"Exotic Goods": 2},
            jobs=jobs,
            levels=0,
            colony=colony
        )

# Specialized Buildings

class ResearchInstitute(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Senior Scientist", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Research Institute",
            construction_cost=600,
            construction_time=480,
            upkeep=5,
            inputs={"Exotic Goods": 1, "Consumer Goods": 2},
            outputs={"Research": 1.15}, # 15% multiplier. rn is just 1.15 points 
            jobs=jobs,
            levels=0,
            colony=colony
        )

# Military Buildings

class Shipyard(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Shipbuilder", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Shipyard",
            construction_cost=500,
            construction_time=480,
            upkeep=3,
            inputs={"Alloys": 4, "Energy": 2},
            outputs={"Warships": 1}, # in stellaris, each shipyard produces 1 ship per month
            jobs=jobs,
            levels=0,
            colony=colony
        )

class NavalBase(Building):
    def __init__(self, colony):
        jobs = [Job(profession="Naval Officer", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Naval Base",
            construction_cost=600,
            construction_time=600,
            upkeep=4,
            inputs={"Alloys": 2, "Energy": 2},
            outputs={"Fleet Capacity": 10}, # in stellaris, each naval base produces 10 fleet capacity
            jobs=jobs,
            levels=0,
            colony=colony
        )
