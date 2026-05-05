class Building: #1st Draft
    """A building on a colony, which can produce goods and services, employ pops, and generate profit"""

    def __init__(self, name, construction_cost, construction_time, upkeep, inputs, outputs, geography=None, jobs=None,
                 levels=0, colony=None):
        self.name = name
        self.construction_cost = construction_cost
        self.construction_time = construction_time
        self.geography = geography  # Urban or Rural
        self.upkeep = upkeep
        self.inputs = inputs
        self.outputs = outputs
        self.jobs = jobs
        self.levels = levels
        self.colony = colony

        self.revenue = 0.0
        self.expenses = 0.0
        self.profit = 0.0
        self.ownership = {"total": 0, "private": 0, "government": 0, "workers": 0}

        self.productivity = 0.0
        self.staffing = 0.0

        self.balance_sheet = {
            "revenue": {},
            "expenses": {},
        }

    def add_level(self, funder):
        """Add a level of the building, owned by the funder"""
        self.levels += 1
        self.ownership[funder] += 1
        self.ownership["total"] += 1

    def operate(self):
        """Operate the building for a tick, processing goods, paying wages, and allocating profits."""
        # Reset for the tick
        self.revenue = 0.0
        self.expenses = 0.0
        self.profit = 0.0

        self.process_goods()
        self.pay_workers()
        self.allocate_profit()
        self.calculate_productivity()

    def pay_workers(self):
        for job in self.jobs:
            self.balance_sheet["expenses"]["wages"] = (job.wage * job.employees)
            wages = job.wage * job.employees
            self.expenses += wages

    def allocate_profit(self):
        self.profit = self.revenue - self.expenses
        if self.profit >= 0:
            dividends = self.profit
            pass

    def calculate_productivity(self):
        total_employees = sum(job.employees for job in self.jobs)
        self.productivity = (self.profit + self.balance_sheet["expenses"].get("wages", 0)) / total_employees if total_employees > 0 else 0


class Job1:
    def __init__(self, profession, max_quantity, employer, wage=10, qualifications=None):
        self.profession = profession
        self.max_quantity = max_quantity  # maximum number of jobs in this position
        self.employees = 0  # Total number of individuals
        self.vacancies = max_quantity
        self.assigned_pops = []  # list of pop objects assigned
        self.employer = employer  # parent building
        self.wage = wage
        self.qualifications = qualifications
        self.openings = 0

        # Flags for labor market evaluation
        self.hiring = True  # whether the job is actively hiring

    def evaluate_labor_market(self):
        """
        Evaluate local labor market conditions to adjust hiring status and wages.
        """
        local_bls = self.employer.colony.local_bls
        unemployment_rate = local_bls.statistics.get("unemployment_rate", 0.0)

        # Adjust hiring status based on unemployment and vacancies
        if unemployment_rate > 0.05 and self.vacancies > 0:
            self.hiring = True
        elif self.vacancies <= 0:
            self.hiring = False

        # Adjust wages based on vacancies and unemployment
        if self.vacancies > (0.2 * self.max_quantity):
            # High vacancies, increase wage to attract workers
            self.wage *= 1.02  # Increase wage by 2%
        elif unemployment_rate > 0.05 and self.vacancies < 0:
            # Low unemployment, decrease wage cautiously
            self.wage *= 0.98  # Decrease wage by 2%

        # Ensure wage does not fall below a minimum threshold
        MIN_WAGE = 1
        if self.wage < MIN_WAGE:
            self.wage = MIN_WAGE

        # If hiring, only fill up to 5% of vacancies per month
        if self.hiring:
            max_hires = 0.05 * self.max_quantity
            openings = min(self.vacancies, max_hires)
            self.openings = openings

    def hire(self, pop):
        """Hire a pop into this job"""
        if pop.size > self.vacancies:
            raise ValueError("Not enough vacancies to hire this pop!")
        self.employees += pop.size
        self.vacancies -= pop.size
        self.openings -= pop.size
        self.assigned_pops.append(pop)
        pop.current_job = self

    def update_statistics(self):
        """Perform a few simple checks to make sure the job's internal data is consistent. Log and correct if not."""
        total_assigned = sum(pop.size for pop in self.assigned_pops)
        if total_assigned != self.employees:
            print(f"Warning: Job {self.profession} has inconsistent employee count! Assigned: {total_assigned}, Recorded: {self.employees}")
            self.employees = total_assigned
        
        for pop in self.assigned_pops:
            if pop.current_job != self:
                print(f"Warning: Pop in job {self.profession} has inconsistent job reference!")
                pop.current_job = self

        if self.employees + self.vacancies != self.max_quantity:
            print(f"Warning: Job {self.profession} has inconsistent vacancy count! Employees: {self.employees}, Vacancies: {self.vacancies}, Max: {self.max_quantity}")
            self.vacancies = self.max_quantity - self.employees



class Pop:
    def __init__(self, colony, size, current_job=None):
        self.colony = colony
        self.size = size
        self.current_job = current_job

        self.wage = current_job.wage if current_job else 5  # default wage if unemployed
        self.wealth = 100.0
        self.needs = {}

    def update_economy_tick(self):
        # Gross income from job
        self.wage = self.current_job.wage if self.current_job else 5  # default wage if unemployed
        gross_income = self.wage * self.size
        # Taxes and transfers
        taxes = self.calculate_taxes(gross_income)
        net_income = gross_income - taxes
        # Draw up budget
        self.calculate_needs()
        # Spend on needs
        expenses = self.fulfill_needs(self.colony.local_market)
        # Update wealth
        self.wealth += (net_income - expenses) / self.size

    def calculate_needs(self):
        NEEDS_PARAMETERS = {
            # Good: [Base (Subsistence), Scaling Factor (alpha), Wealth Elasticity Exponent (beta)]
            "Food": [0.2, 0.27, 0.8],
            "Housing": [0.06, 0.27, 1.0],
            "Consumer Goods": [0.02, 0.11, 1.0],
            #"Services": [0.05, 0.04, 1.1],
            #"Education": [0.0, 0.12, 0.7],
            "Energy": [0.05, 0.12, 0.8],
            "Amenities": [0, 0.02, 1.5],
            #"Healthcare": [0.03, 0.22, 0.8],
            #"Transportation": [0.0, 0.06, 1.2],
            #"Luxury Goods": [0.0, 0.01, 1.5],
        }
        # scaling_factor = (consumption - subsistence) / (wealth ** beta)

        consumption = {}
        for good, params in NEEDS_PARAMETERS.items():
            base_need, alpha, beta = params
            safe_wealth = max(self.wealth, 1)  # prevent negative and zero wealth, which apparently causes issues
            consumption[good] = base_need + (alpha * (safe_wealth ** beta))
        self.needs = consumption

    def fulfill_needs(self, market):
        scale = self.size
        expenses = 0
        for good, quantity in self.needs.items():
            cost = market.buy_good(good, (quantity * scale))
            expenses += cost
        return expenses

    def calculate_taxes(self, gross_income):
        TAX_RATE = 0.1  # 10% flat tax for simplicity
        taxes = gross_income * TAX_RATE
        return taxes

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
        self.colony.pops.append(new_pop)
        return new_pop


class LocalBLS:
    """
    Local Bureau of Labor Statistics for tracking all economic data in the colony.
    TODO: average wage should be broken down by profession, as well as aggregate.
    """

    def __init__(self, colony):
        self.colony = colony
        self.statistics = {
            "unemployment_rate": 0.0,
            "gdp": 0.0,
            "population": 0,
            "buildings": 0,
            "average_wage": 0.0,
            "job_vacancies": 0,
        }

    def update_statistics(self):
        """
        Refactored to use standard for loops for clarity instead of complex generator expressions.
        This performs the necessary aggregation from the Colony's object lists.
        """
        # --- Accumulators for Core Data ---
        total_population = 0
        total_employed = 0
        total_wages = 0
        total_vacancies = 0

        # 1. Tally Population
        for pop in self.colony.pops:
            total_population += pop.size

        # 2. Tally Jobs, Wages, and Vacancies across all Buildings
        # This iterates through every job in every building to aggregate the data.
        for building in self.colony.buildings:
            # Note: Must handle case where building.jobs is None or empty list
            if building.jobs:
                for job in building.jobs:
                    # Number of employed Pops for this job
                    employed_in_job = job.max_quantity - job.vacancies

                    # Accumulate totals
                    total_employed += employed_in_job
                    total_vacancies += job.vacancies

                    # Wage Bill: Wage * Number of Employed
                    total_wages += job.wage * employed_in_job

        # --- Calculate Derived Statistics ---

        # Unemployment
        unemployed_pops = total_population - total_employed
        unemployment_rate = unemployed_pops / total_population if total_population > 0 else 0.0

        # Average Wage
        average_wage = total_wages / total_employed if total_employed > 0 else 0.0

        # --- Write Results to Dictionary ---
        self.statistics["planet_name"] = self.colony.name
        self.statistics["population"] = total_population
        self.statistics["unemployment_rate"] = unemployment_rate
        self.statistics["average_wage"] = average_wage
        self.statistics["job_vacancies"] = total_vacancies
        self.statistics["buildings"] = len(self.colony.buildings)
        # GDP calculation can be added here based on production data
        # gdp per capita
        # profession breakdowns

        # Publish statistics to colony
        self.colony.population = total_population


    def update_statistics_dense(self):
        """A denser version using sum() with generator expressions for brevity. Not currently used, since clarity is preferred."""
        total_population = sum(pop.size for pop in self.colony.pops)
        total_employed = sum(
            job.max_quantity - job.vacancies for building in self.colony.buildings for job in building.jobs)
        total_wages = sum(job.wage * (job.max_quantity - job.vacancies) for building in self.colony.buildings for job in
                          building.jobs)
        total_vacancies = sum(job.vacancies for building in self.colony.buildings for job in building.jobs)

        self.statistics["population"] = total_population
        self.statistics["unemployment_rate"] = (
                                                           total_population - total_employed) / total_population if total_population > 0 else 0.0
        self.statistics["average_wage"] = total_wages / total_employed if total_employed > 0 else 0.0
        self.statistics["job_vacancies"] = total_vacancies
        self.statistics["buildings"] = len(self.colony.buildings)
        # GDP calculation can be added here based on production data

        # Publish statistics to colony
        self.colony.population = total_population


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
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Miner", max_quantity=10000, employer=self)]
        super().__init__(
            name="Mineral Extractor",
            construction_cost=300,
            construction_time=240,
            geography="Rural",
            upkeep=1,
            inputs={},
            outputs={"Minerals": 4},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class EnergyPlant(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Engineer", max_quantity=10000, employer=self)]
        super().__init__(
            name="Energy Plant",
            construction_cost=300,
            construction_time=240,
            geography="Rural",
            upkeep=1,
            inputs={},
            outputs={"Energy": 6},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class Farm(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Farmer", max_quantity=10000, employer=self)]
        super().__init__(
            name="Farm",
            construction_cost=300,
            construction_time=240,
            geography="Rural",
            upkeep=1,
            inputs={},
            outputs={"Food": 6},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class CityDistrict(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Urban Worker", max_quantity=10000, employer=self)]
        super().__init__(
            name="City District",
            construction_cost=300,
            construction_time=240,
            geography="Urban",
            upkeep=1,
            inputs={},
            outputs={"Housing": 5},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


# Now some tier 2 buildings

class ResearchLab(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Scientist", max_quantity=10000, employer=self)]
        super().__init__(
            name="Research Lab",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Consumer Goods": 2},
            outputs={"Research": 10},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class Factory(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Factory Worker", max_quantity=10000, employer=self)]
        super().__init__(
            name="Factory",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Minerals": 6, },
            outputs={"Consumer Goods": 6},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class AlloyFoundry(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Metallurgist", max_quantity=10000, employer=self)]
        super().__init__(
            name="Alloy Foundry",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Minerals": 6},
            outputs={"Alloys": 3},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class AdministrationCenter(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Administrator", max_quantity=10000, employer=self)]
        super().__init__(
            name="Administration Center",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Consumer Goods": 2},
            outputs={"Stability": 5, "Unity": 4},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class HoloTheater(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Entertainer", max_quantity=10000, employer=self)]
        super().__init__(
            name="Holo-Theater",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Consumer Goods": 1},
            outputs={"Amenities": 10},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class HydroponicsFarm(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Hydroponic Farmer", max_quantity=10000, employer=self)]
        super().__init__(
            name="Hydroponics Farm",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Energy": 4},
            outputs={"Food": 6},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class HealthClinic(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Doctor", max_quantity=10000, employer=self)]
        super().__init__(
            name="Health Clinic",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Consumer Goods": 1},
            outputs={"Health Services": 10},  # in stellaris, output is 4 amenities, 5% growth, and 2.5% habitability
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class Spaceport(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Dockworker", max_quantity=10000, employer=self)]
        super().__init__(
            name="Spaceport",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Alloys": 2, "Energy": 2},
            outputs={"Trade": 10},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class RoboticsFactory(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Robotics Engineer", max_quantity=10000, employer=self)]
        super().__init__(
            name="Robotics Factory",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Alloys": 2},
            outputs={"Robots": 2},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class EnforcementCenter(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Law Enforcer", max_quantity=10000, employer=self)]
        super().__init__(
            name="Enforcement Center",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={},
            outputs={"Stability": 10},
            # In Stellaris, each enforcer produces 1 stability, -25 crime, and 2 defense army
            jobs=jobs,
            levels=levels,
            colony=colony
        )


# Special Resource Buildings

class Refinery(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Refinery Worker", max_quantity=10000, employer=self)]
        super().__init__(
            name="Refinery",
            construction_cost=500,
            construction_time=480,
            geography="Urban",
            upkeep=3,
            inputs={"Rare Minerals": 10},
            outputs={"Exotic Goods": 2},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class Harvester(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Harvester Operator", max_quantity=10000, employer=self)]
        super().__init__(
            name="Harvester",
            construction_cost=200,
            construction_time=360,
            geography="Rural",
            upkeep=1,
            inputs={},
            outputs={"Exotic Goods": 2},
            jobs=jobs,
            levels=levels,
            colony=colony
        )


# Specialized Buildings

class ResearchInstitute(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Senior Scientist", max_quantity=10000, employer=self)]
        super().__init__(
            name="Research Institute",
            construction_cost=600,
            construction_time=480,
            geography="Urban",
            upkeep=5,
            inputs={"Exotic Goods": 1, "Consumer Goods": 2},
            outputs={"Research": 1.15},  # 15% multiplier. rn is just 1.15 points
            jobs=jobs,
            levels=levels,
            colony=colony
        )


# Military Buildings

class Shipyard(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Shipbuilder", max_quantity=10000, employer=self)]
        super().__init__(
            name="Shipyard",
            construction_cost=500,
            construction_time=480,
            geography="Urban",
            upkeep=3,
            inputs={"Alloys": 4, "Energy": 2},
            outputs={"Warships": 1},  # in stellaris, each shipyard produces 1 ship per month
            jobs=jobs,
            levels=levels,
            colony=colony
        )


class NavalBase(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Naval Officer", max_quantity=10000, employer=self)]
        super().__init__(
            name="Naval Base",
            construction_cost=600,
            construction_time=600,
            geography="Urban",
            upkeep=4,
            inputs={"Alloys": 2, "Energy": 2},
            outputs={"Fleet Capacity": 10},  # in stellaris, each naval base produces 10 fleet capacity
            jobs=jobs,
            levels=levels,
            colony=colony
        )
