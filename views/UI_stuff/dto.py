from dataclasses import dataclass

# --- World DTOs ---

@dataclass
class BuildingDTO:
    name: str
    levels: int
    productivity: float
    profit: float
    staffing: float

@dataclass
class ColonyDTO:
    name: str
    planet_name: str
    owner: str
    #market: MarketDTO
    climate: str
    gdp: float
    population: int
    stability: float
    unemployment_rate: float
    buildings: list  # List[BuildingDTO]

@dataclass
class CelestialDTO:
    name: str
    body_type: str
    radius: float
    size: float
    color: tuple  # (R, G, B)

@dataclass
class StarDTO(CelestialDTO):
    star_type: str

@dataclass
class PlanetDTO(CelestialDTO):
    planet_type: str
    habitable: bool
    climate: str = None  # Optional, only for habitable planets
    colony:  ColonyDTO = None  # Optional, only if there's a colony

@dataclass
class MoonDTO(CelestialDTO):
    pass

@dataclass
class AsteroidDTO(CelestialDTO):
    pass

def colony_to_dto(colony):
    # Only include what the planet menu needs
    return ColonyDTO(
        name=colony.name,
        climate=getattr(colony.planet, "climate", "unknown"),
        gdp=colony.stats.get("gdp", 0.0),
        population=colony.stats.get("population", 0),
        stability=colony.stats.get("stability", 0.0),
        unemployment_rate=colony.stats.get("unemployment_rate", 0.0),
        buildings=[building_to_dto(b) for b in colony.buildings]
    )

def building_to_dto(building):
    return BuildingDTO(
        name=building.name,
        levels=building.levels,
        productivity=building.productivity,
        profit=building.profit,
        staffing=building.staffing
    )

def celestial_to_dto(body):
    if body.body_type == "star":
        return StarDTO(
            name=body.name,
            body_type=body.body_type,
            radius=body.radius,
            size=body.size,
            color=body.color,
            angle=body.angle,
            speed=body.speed,
            star_type=getattr(body, "star_type", None)
        )
    elif body.body_type == "planet":
        return PlanetDTO(
            name=body.name,
            body_type=body.body_type,
            radius=body.radius,
            size=body.size,
            color=body.color,
            angle=body.angle,
            speed=body.speed,
            planet_type=getattr(body, "planet_type", None),
            habitable=getattr(body, "habitable", False),
            climate=getattr(body, "climate", None),
            colony=getattr(body, "colony", None)
        )
    elif body.body_type == "moon":
        return MoonDTO(
            name=body.name,
            body_type=body.body_type,
            radius=body.radius,
            size=body.size,
            color=body.color,
            angle=body.angle,
            speed=body.speed,
            planet_type=getattr(body, "planet_type", None),
            habitable=getattr(body, "habitable", False),
            climate=getattr(body, "climate", None),
            colony=getattr(body, "colony", None)
        )
    elif body.body_type == "asteroid":
        return AsteroidDTO(
            name=body.name,
            body_type=body.body_type,
            radius=body.radius,
            size=body.size,
            color=body.color,
            angle=body.angle,
            speed=body.speed
        )
    else:
        return CelestialDTO(
            name=body.name,
            body_type=body.body_type,
            radius=body.radius,
            size=body.size,
            color=body.color,
            angle=body.angle,
            speed=body.speed
        )