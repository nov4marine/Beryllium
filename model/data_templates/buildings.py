# Goals for building/job operating logic:
    # A. Staffing:
    # 1. By default, buildings should attempt to stay fully staffed at all times.
    # 2. Staffing can be reduced if building is operating at a loss for more than 3 consecutive months.
    # 3. Qualified workers can be poached by other buildings offering higher wages.
    # 4. Staffing adjustments should be gradual, loose target: no more than 5% of total jobs per month.
    # 5. building should maintain a minimum 10% employment/staffing level. If below, attempt to hire more pops.
    # 5a. If staffing remains at or below 50% for 3 consecutive months, building should prepare to downsize (remove a level).
    # B. Wages:
    # 1. Buildings should always seek to maximize profits by adjusting wages and to a lesser extent, staffing/production levels.
    # 1a. Starting wages should use planet average for a given profession, else 10. Wages should adjust by +/- 2% per month.
    # 1b. The decision to adjust(reduce) wages should be based on local labor market conditions. Mainly underemployment rates for qualified pops.
    # 1c. To prevent oscillation, wages should not decrease if underemployment is:
    # below 5%, or less than 10 buildings worth of employees, whichever is less.
    # 2. Buildings should begin to increase wages if:
    # 2a. They are unable to fill ANY vacancies for more than 1 consecutive months.
    # 2b. They are unable to reach target staffing within 6? or 12? months.
    # 3. Wages should be capped if building profit margin is less than 10%

from dataclasses import dataclass

class Building: # 2nd Draft
    """A building on a colony, which can produce goods and services, employ pops, and generate profit"""

    def __init__(self, name, construction_cost, construction_time, inputs, outputs, jobs=None):
        self.name = name
        self.construction_cost = construction_cost
        self.construction_time = construction_time
        #self.upkeep = maybe initially just 5% of construction cost anually?
        self.inputs = inputs
        self.outputs = outputs
        self.jobs = jobs
        self.levels = 0

        self.cash_reserves = 1000.0
        self.ownership = {"total": 0, "private": 0, "government": 0, "workers": 0}

        self.productivity = 0.0
        self.staffing = 0.0


@dataclass
class Job:
    profession: str
    max_quantity: int
    wage: float = 10.0
    employees: int = 0
    # Logic like hiring/firing is removed; the LaborManager will handle that.


# building_registry.py
BUILDING_PROTOTYPES = {
    "Mineral Extractor": Building(
        name="Mineral Extractor",
        inputs={},
        outputs={"Minerals": 4},
        jobs=[Job("Miner", 10000)],
        construction_cost=300,
        construction_time=240
    ),
    "Energy Plant": Building(
        name="Energy Plant",
        construction_cost=300,
        construction_time=240,
        inputs={},
        outputs={"Energy": 6},
        jobs=[Job("Technician", 10000)]
    ),
    "Farm": Building(
        name="Farm",
        construction_cost=300,
        construction_time=240,
        inputs={},
        outputs={"Food": 6},
        jobs=[Job("Farmer", 10000)]
    ),
    "City District": Building(
        name="City District",
        construction_cost=300,
        construction_time=240,
        inputs={},
        outputs={"Housing": 5},
        jobs=[Job("Urban Worker", 10000)]
    ),

    # --- Tier 2 ---

    "Factory": Building(
        name="Factory",
        construction_cost=400,
        construction_time=360,
        inputs={"Minerals": 6},
        outputs={"Consumer Goods": 6},
        jobs=[Job("Factory Worker", 10000)],
    ),
    "Foundry": Building(
        name="Foundry",
        construction_cost=400,
        construction_time=360,
        inputs={"Minerals": 6},
        outputs={"Alloys": 3},
        jobs=[Job("Metallurgist", 10000)]
    ),
    "Holo-Theater": Building(
        name="Holo-Theater",
        construction_cost=400,
        construction_time=360,
        inputs={"Consumer Goods": 1},
        outputs={"Amenities": 10},
        jobs=[Job("Entertainer", 10000)],
    ),
    "Research Lab": Building(
        name="Research Lab",
        construction_cost=400,
        construction_time=360,
        inputs={"Consumer Goods": 2},
        outputs={"Research": 10},
        jobs=[Job("Scientist", 10000)]
    ),
    "Administration Center": Building(
        name="Administration Center",
        construction_cost=400,
        construction_time=360,
        inputs={"Consumer Goods": 2},
        outputs={"Stability": 5, "Unity": 4},
        jobs=[Job("Bureaucrat", 10000)]
    ),
    "Hydroponics Farm": Building(
        name="Hydroponics Farm",
        construction_cost=400,
        construction_time=360,
        inputs={"Energy": 4},
        outputs={"Food": 6},
        jobs=[Job("Hydroponic Farmer", 10000)]
    ),
    "Health Clinic": Building(
        name="Health Clinic",
        construction_cost=400,
        construction_time=360,
        inputs={"Consumer Goods": 1},
        outputs={"Health Services": 10},
        jobs=[Job("Doctor", 10000)]
    ),
    "Robotics Factory": Building(
        name="Robotics Factory",
        construction_cost=400,
        construction_time=360,
        inputs={"Alloys": 2},
        outputs={"Robots": 2},
        jobs=[Job("Robotics Engineer", 10000)]
    ),
    "Enforcement Center": Building(
        name="Enforcement Center",
        construction_cost=400,
        construction_time=360,
        inputs={},
        outputs={"Stability": 10},
        jobs=[Job("Enforcer", 10000)]
    ),

    # --- Non Stellaris Buildings ---

    "Shipyard": Building(
        name="Shipyard",
        construction_cost=500,
        construction_time=480,
        inputs={"Alloys": 4, "Energy": 2},
        outputs={"Warships": 1},
        jobs=[Job("Shipwright", 10000)]
    ),
    "Spaceport": Building(
        name="Spaceport",
        construction_cost=400,
        construction_time=360,
        inputs={"Alloys": 2, "Energy": 2},
        outputs={"Trade": 10},
        jobs=[Job("Dockworker", 10000)]
    )
    # Still need to add refinery, harvester.
}