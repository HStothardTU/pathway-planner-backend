from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_scenario_results(scenario_data):
    years = scenario_data["years"]
    results = []

    for i, year in enumerate(years):
        year_result = {
            "year": year,
            "vehicles": {},
            "total_emissions": 0,
            "total_cost": 0,
            "fuel_demand": {}
        }
        for vehicle, vdata in scenario_data["vehicles"].items():
            miles = vdata["miles_traveled"][i]
            vehicle_emissions = 0
            vehicle_cost = 0
            vehicle_fuel_demand = {}
            for subtype, sdata in vdata["subtypes"].items():
                adoption = sdata["adoption"][i]
                emissions = miles * adoption * sdata["emission_factor"]
                cost = miles * adoption * sdata["cost_per_mile"]
                fuel = miles * adoption

                vehicle_emissions += emissions
                vehicle_cost += cost
                vehicle_fuel_demand[subtype] = fuel

                # Aggregate to year totals
                year_result["total_emissions"] += emissions
                year_result["total_cost"] += cost
                year_result["fuel_demand"][subtype] = year_result["fuel_demand"].get(subtype, 0) + fuel

            year_result["vehicles"][vehicle] = {
                "emissions": vehicle_emissions,
                "cost": vehicle_cost,
                "fuel_demand": vehicle_fuel_demand
            }
        results.append(year_result)
    return results 