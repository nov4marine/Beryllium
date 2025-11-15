from model.economy.market import Market


class Colony:
    """mega class to represent a colonized world"""

    def __init__(self, planet, owner, name):
        self.planet = planet  # Reference to which planet it is on
        self.owner = owner  # Owning nation
        self.name = name  # Name of colonized world
        self.national_market = owner.national_market

        self.pops = []
        self.buildings = []
        self.jobs = []
        self.job_offers = []  # Job Board

        self.construction_queue = []

        self.stability = 100
        self.unemployed = 0
        self.local_bank = None
        self.local_market = Market()
        self.local_bls = LocalBLS(self)

    @property
    def stats(self):
        """
        [NEW PROPERTY] Provides clean, direct access to the latest calculated statistics.
        External entities (like the Planet Menu or parent Nation) should use this.
        """
        return self.local_bls.statistics
    
    # Job assignment methods
    def assign_jobs_simple(self):
        """
        Directly assigns pops to job vacancies in order, without applications or splitting.
        All pops are treated as a single group for now.
        """
        total_pops = sum(pop.size for pop in self.pops)
        pops_remaining = total_pops

        for building in self.buildings:
            for job in building.jobs:
                if pops_remaining <= 0:
                    job.employees = 0
                    job.vacancies = job.max_quantity
                    continue
                to_assign = min(job.vacancies, pops_remaining)
                job.employees = to_assign
                job.vacancies = job.max_quantity - to_assign
                pops_remaining -= to_assign

        # For prototype: assign all pops to the first available job (optional)
        for pop in self.pops:
            pop.current_job = None
            for building in self.buildings:
                for job in building.jobs:
                    if job.employees > 0:
                        pop.current_job = job
                        break
                if pop.current_job:
                    break
    
    def run_labor_market(self):
        """
        A more complex labor market simulation.
        I think it would be better to centralize this logic as a colony method rather than spreading it across Pop and Building classes.
        Probably more performant too, to handle it top down, rather than having each pop search for jobs individually.
        """
        # 1. Gather all job openings
        job_board = []
        for building in self.buildings:
            for job in building.jobs:
                job.evaluate_labor_market()
                if job.hiring == True:
                    job_offer = {"job": job, "openings": job.openings, "wage": job.wage}
                    job_board.append(job_offer)

        # 2. Pops are assigned to jobs based on wage and availability. no applications.
        for pop in self.pops:
            if pop.current_job is not None:
                continue  # Already employed

            # Sort job board by wage descending
            sorted_jobs = sorted(job_board, key=lambda x: x["wage"], reverse=True)

            for job_offer in sorted_jobs:
                job = job_offer["job"]
                if job_offer["openings"] > 0:
                    # Assign pops to this job
                    recruits = min(pop.size, job_offer["openings"])
                    # if pop needs to be split, handle that
                    if recruits < pop.size:
                        new_pop = pop.split(recruits)
                        job.hire(new_pop)
                        job_offer["openings"] -= recruits
                    else:
                        job.hire(pop)
                        job_offer["openings"] -= recruits
                        break  # Move to next pop


    def on_monthly_update(self):
        """This method aggregates all logic for the monthly economy tick"""
        # --- Step 1: Labor Market ---
        #self.assign_jobs_simple()  # Use simplified assignment
        self.run_labor_market()  # Use labor market simulation
        # --- Step 2: Production and Wages ---
        for building in self.buildings:
            building.operate()
        # --- Step 3: Consumption and Pop Needs ---
        for pop in self.pops:
            pop.update_economy_tick()
        # --- Step 4: Update Market Prices ---
        self.local_market.on_monthly_update()
        # --- Step 5: Update Local BLS Statistics ---
        self.local_bls.update_statistics()

    def setup_capital(self):
        print(f"capital deployed on planet {self.planet.name}. Nation color is {self.owner.color}")
        self.buildings = [
            MineralExtractor(self, levels=3),
            EnergyPlant(self, levels=3),
            Farm(self, levels=3),
            CityDistrict(self, levels=3),
            ResearchLab(self, levels=2),
            Factory(self, levels=2),
            AlloyFoundry(self, levels=2),
            AdministrationCenter(self, levels=2),
            HoloTheater(self, levels=2),
        ]

        self.pops = [Pop(self, size=1200000)]  # 1.2 million initial population
        total_population = sum(pop.size for pop in self.pops)
        print(f"Colony {self.name} initialized with {len(self.buildings)} buildings and population {total_population}.")

        # Goals for building/job operating logic:
    # A. Staffing:
        # 1. By default, buildings should attempt to stay fully staffed at all times.
        # 2. Staffing can be reduced if building is operating at a loss for more than 3 consecutive months.
        # 3. Qualified workers can be poached by other buildings offering higher wages.
        # 4. Staffing adjustments should be gradual, loose target: no more than 5% of total jobs per month.
        # 5. building should maintain a minimum 10% employment/staffing level. If below, attempt to hire more pops.
            # 5a. If staffing remains at or below 50% for 3 consecutive months, building should prepare to downsize (remove a level).
    # B. Wages:
        # 1. Buildings should always seek to to maximize profits by adjusting wages and to a lesser extent, staffing/production levels.
            # 1a. Starting wages should planet average for a given profession, else 10. Wages should adjust by +/- 2% per month.
            # 1b. The decision to adjust(reduce) wages should be based on local labor market conditions. Mainly underemployment rates for qualified pops.
            # 1c. To prevent oscillation, wages should not decrease if underemployment is: 
                # below 5%, or less than less than 10 buildings worth of employees, whichever is less.
        # 2. Buildings should increase wages if:
            # 2a. They are unable to fill vacancies for more than 1 consecutive months.
        # 3. Wages should be capped if building profit margin is less than 10%


class Building:
    """A building on a colony, which can produce goods and services, employ pops, and generate profit"""

    def __init__(self, name, construction_cost, construction_time, upkeep, inputs, outputs, geography=None, jobs=None, levels=0, colony=None):
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

        self.revenue = 0
        self.expenses = 0
        self.profit = 0
        self.ownership = {"total": 0, "private": 0, "government": 0, "workers": 0}

        self.productivity = 0

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
        self.revenue = 0
        self.expenses = 0
        self.profit = 0

        self.process_goods()
        self.pay_workers()
        self.allocate_profit()
        self.calculate_productivity()

    def process_goods(self):
        job_staffing = []
        for job in self.jobs:
            staffing = job.employees / job.max_quantity
            job_staffing.append(staffing)

        total_staffing = sum(job_staffing) / len(job_staffing)

        expenses = 0
        revenue = 0
        for good, quantity in self.inputs.items():
            total_inputs = quantity * total_staffing * self.levels
            expenses += self.colony.local_market.buy_good(good, total_inputs)
            self.balance_sheet["expenses"][good] = expenses
            self.expenses += expenses

        for good, quantity in self.outputs.items():
            total_outputs = quantity * total_staffing * self.levels
            revenue += self.colony.local_market.sell_good(good, total_outputs)
            self.balance_sheet["revenue"][good] = revenue
            self.revenue += revenue

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
        self.openings = 0

        # Flags for labor market evaluation
        self.hiring = True # whether the job is actively hiring

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
            consumption[good] = base_need + (alpha * (self.wealth ** beta))
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


    def update_statistics_dense(self):
        """A denser version using sum() with generator expressions for brevity. Not currently used, since clarity is preferred."""
        total_population = sum(pop.size for pop in self.colony.pops)
        total_employed = sum(job.max_quantity - job.vacancies for building in self.colony.buildings for job in building.jobs)
        total_wages = sum(job.wage * (job.max_quantity - job.vacancies) for building in self.colony.buildings for job in building.jobs)
        total_vacancies = sum(job.vacancies for building in self.colony.buildings for job in building.jobs)

        self.statistics["population"] = total_population
        self.statistics["unemployment_rate"] = (total_population - total_employed) / total_population if total_population > 0 else 0.0
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
        jobs = [Job(profession="Miner", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Engineer", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Farmer", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Urban Worker", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Scientist", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Factory Worker", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Factory",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Minerals": 6,},
            outputs={"Consumer Goods": 6},
            jobs=jobs,
            levels=levels,
            colony=colony
        )

class AlloyFoundry(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Metallurgist", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Administrator", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Entertainer", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Hydroponic Farmer", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Doctor", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Health Clinic",
            construction_cost=400,
            construction_time=360,
            geography="Urban",
            upkeep=2,
            inputs={"Consumer Goods": 1},
            outputs={"Health Services": 10}, # in stellaris, output is 4 amenities, 5% growth, and 2.5% habitability
            jobs=jobs,
            levels=levels,
            colony=colony
        )

class Spaceport(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Dockworker", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Robotics Engineer", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Law Enforcer", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Refinery Worker", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Harvester Operator", max_quantity=10000000, employer=self)]
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
        jobs = [Job(profession="Senior Scientist", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Research Institute",
            construction_cost=600,
            construction_time=480,
            geography="Urban",
            upkeep=5,
            inputs={"Exotic Goods": 1, "Consumer Goods": 2},
            outputs={"Research": 1.15}, # 15% multiplier. rn is just 1.15 points 
            jobs=jobs,
            levels=levels,
            colony=colony
        )

# Military Buildings

class Shipyard(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Shipbuilder", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Shipyard",
            construction_cost=500,
            construction_time=480,
            geography="Urban",
            upkeep=3,
            inputs={"Alloys": 4, "Energy": 2},
            outputs={"Warships": 1}, # in stellaris, each shipyard produces 1 ship per month
            jobs=jobs,
            levels=levels,
            colony=colony
        )

class NavalBase(Building):
    def __init__(self, colony, levels=0):
        jobs = [Job(profession="Naval Officer", max_quantity=10000000, employer=self)]
        super().__init__(
            name="Naval Base",
            construction_cost=600,
            construction_time=600,
            geography="Urban",
            upkeep=4,
            inputs={"Alloys": 2, "Energy": 2},
            outputs={"Fleet Capacity": 10}, # in stellaris, each naval base produces 10 fleet capacity
            jobs=jobs,
            levels=levels,
            colony=colony
        )
