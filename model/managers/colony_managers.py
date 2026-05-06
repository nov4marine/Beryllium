    
import copy

from model.data_templates.buildings import *

class BuildingManager:
    """Production and Wholesale"""
    @staticmethod
    def produce(colony):
        """Processes all building production (both input and output) for a single colony."""
        for building_name, building in colony.buildings.items():
            # 1. Calculate Staffing Efficiency
            # In your new 'Victoria 3' style, levels and jobs are linked
            total_slots = sum(job.max_quantity for job in building.jobs) * building.levels
            total_employed = sum(job.employees for job in building.jobs)
            
            # Efficiency is (Actual Workers / Max Possible Slots)
            efficiency = total_employed / total_slots if total_slots > 0 else 0

            # 2. Consume Inputs
            for good, amount in building.inputs.items():
                slot = colony.stockpile.get(good)
                if slot:
                    total_inputs = amount * building.levels * efficiency
                    slot.quantity = max(slot.quantity - total_inputs, 0)
                    # TODO: Logic for 'if we don't have enough' goes here later
                    building.cash_reserves -= total_inputs * slot.current_price

            # 3. Generate Outputs
            for good, amount in building.outputs.items():
                slot = colony.stockpile.get(good)
                if slot:
                    actual_produced = amount * building.levels * efficiency
                    slot.quantity = min(slot.quantity + actual_produced, slot.max_capacity)
                    building.cash_reserves += actual_produced * slot.current_price

    @staticmethod
    def add_building_to_colony(colony, building_name, levels=1):
        if building_name not in BUILDING_PROTOTYPES:
            print(f"Error: {building_name} not found.")
            return

        # 1. Create a unique instance from the prototype
        new_building = copy.deepcopy(BUILDING_PROTOTYPES[building_name])
        
        # 2. Set the instance-specific data
        new_building.levels = levels
        new_building.cash_reserves = 1000.0  # Starting seed money
        
        # 3. Add to the colony dictionary
        colony.buildings[building_name] = new_building

class MarketManager:
    @staticmethod
    def update_prices(colony):
        """
        Adjusts the current_price of each resource based on supply/demand.
        This system only writes to ResourceSlot; it does not move money.
        """
        for slot in colony.stockpile.values():
            # Calculate 'Scarcity' (how empty the stockpile is)
            # If quantity is 0, scarcity is 1.0. If full, scarcity is 0.0.
            scarcity = 1.0 - (slot.quantity / slot.max_capacity)
            
            # Simple linear price curve: 
            # Price = Base + (Base * Scarcity * Sensitivity)
            # You can make this much more complex later!
            sensitivity = 2.0 
            new_price = slot.base_price + (slot.base_price * scarcity * sensitivity)
            
            slot.current_price = round(new_price, 2)

class FinancialManager:
    """Consumption and Retail"""
    @staticmethod
    def pay_wages(colony):
        for building in colony.buildings.values():
            for job in building.jobs:
                total_wage_bill = job.wage * job.employees
                # Logic to subtract from building bank and add to pop wealth
                # (This is where you'd handle building bankruptcy logic)
                building.cash_reserves -= total_wage_bill

    @staticmethod
    def process_consumption(colony):
        for pop in colony.pops:
            for good, quantity_needed in pop.needs.items():
                slot = colony.stockpile.get(good)
                if slot:
                    # Pop buys what they need at the exact same price
                    # If they can't afford it, they buy as much as their wealth allows
                    total_demand = quantity_needed * pop.size
                    affordable_quantity = min(total_demand, pop.wealth / slot.current_price)
                    
                    # Ensure we don't buy more than is physically in the stockpile
                    actual_bought = min(affordable_quantity, slot.quantity)
                    
                    # Execute transaction
                    pop.wealth -= actual_bought * slot.current_price
                    slot.quantity -= actual_bought

class LaborManager:
    @staticmethod
    def run_market(colony):
        """
        Simple Labor Market: Finds unemployed pops and fills building vacancies.
        """
        # 1. Calculate Total Available Labor
        # We assume all pops can work for now.
        total_labor_pool = sum(pop.size for pop in colony.pops)
        
        # 2. Count Total Job Slots
        # We iterate through the dictionary of buildings you just refactored.
        for building in colony.buildings.values():
            for job in building.jobs:
                # Target staffing based on levels
                total_vacancies = (job.max_quantity * building.levels) - job.employees
                
                if total_vacancies > 0 and total_labor_pool > 0:
                    # Fill as many as possible from the pool
                    hired = min(total_vacancies, total_labor_pool)
                    job.employees += hired
                    total_labor_pool -= hired
                    
        # 3. Track Unemployment (for your BLS/Stats later)
        colony.unemployed = total_labor_pool

# Below this line, not yet done ---- V

class LaborMarketManager:
    def __init__(self, colony) -> None:
        self.colony = colony

    def run_labor_market(self):
        """
        A more complex labor market simulation.
        I think it would be better to centralize this logic as a colony method rather than spreading it across Pop and Building classes.
        Probably more performant too, to handle it top down, rather than having each pop search for jobs individually.
        """
        # 1. Gather all job openings
        job_board = []
        for building in self.colony.buildings:
            for job in building.jobs:
                job.evaluate_labor_market()
                if job.hiring:  # = True is shortened to this
                    job_offer = {"job": job, "openings": job.openings, "wage": job.wage}
                    job_board.append(job_offer)

        # 2. Pops are assigned to jobs based on wage and availability. no applications.
        for pop in self.colony.pops:
            if pop.job is not None:
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

    # Job assignment methods
    def assign_jobs_simple(self):
        """DEPRACATED
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
            pop.job = None
            for building in self.buildings:
                for job in building.jobs:
                    if job.employees > 0:
                        pop.job = job
                        break
                if pop.job:
                    break



# Uncategorized yet. ----
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
    # --- Step 6: Log Data and Analyze for inconsistencies (optional) ---
    for building in self.buildings:
        for job in building.jobs:
            job.update_statistics()

def setup_capital(self):
    print(f"capital deployING on planet {self.planet.name}. Nation color is {self.owner.color}")
    self.buildings = [
        MineralExtractor(self, levels=3),
        EnergyPlant(self, levels=3),
        Farm(self, levels=3),
        CityDistrict(self, levels=3),
        ResearchLab(self, levels=2),
        Factory(self, levels=2),
        AlloyFoundry(self, levels=2),
        #AdministrationCenter(self, levels=2),
        HoloTheater(self, levels=2),
    ]

    # --- Initial Population ---
    # The game should start in a functional state, with buildings staffed and producing.
    for building in self.buildings:
        for job in building.jobs:
            pop = Pop(self, size=10_000)
            job.assigned_pops.append(pop)
            self.pops.append(pop)
            job.employees += pop.size
            job.vacancies -= pop.size
            pop.job = job
            
    # Perform a couple of monthly updates to stabilize the economy and populate statistics, as well as log initial state to detect issues.
    for _ in range(2):
        self.on_monthly_update()

    total_population = sum(pop.size for pop in self.pops)
    print(f"Colony {self.name} initialized with {len(self.buildings)} buildings and population {total_population}.")

