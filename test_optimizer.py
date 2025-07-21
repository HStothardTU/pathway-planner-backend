from app.services.optimizer import optimize_scenario

# Sample scenario data
data = {
    "years": [2025, 2030, 2040, 2050],
    "vehicles": {
        "car": {
            "miles_traveled": [1_000_000, 1_100_000, 1_200_000, 1_300_000],
            "subtypes": {
                "petrol": {
                    "emission_factor": 250,
                    "cost_per_mile": 0.12,
                    "adoption": [0.7, 0.5, 0.2, 0.0],
                },
                "diesel": {
                    "emission_factor": 220,
                    "cost_per_mile": 0.10,
                    "adoption": [0.2, 0.2, 0.1, 0.0],
                },
                "electric": {
                    "emission_factor": 50,
                    "cost_per_mile": 0.08,
                    "adoption": [0.1, 0.25, 0.6, 0.8],
                },
                "hydrogen": {
                    "emission_factor": 20,
                    "cost_per_mile": 0.15,
                    "adoption": [0.0, 0.05, 0.1, 0.2],
                }
            }
        },
        "bus": {
            "miles_traveled": [100_000, 110_000, 120_000, 130_000],
            "subtypes": {
                "diesel": {
                    "emission_factor": 220,
                    "cost_per_mile": 0.10,
                    "adoption": [0.8, 0.6, 0.3, 0.0],
                },
                "electric": {
                    "emission_factor": 50,
                    "cost_per_mile": 0.08,
                    "adoption": [0.1, 0.2, 0.4, 0.5],
                },
                "hydrogen": {
                    "emission_factor": 20,
                    "cost_per_mile": 0.15,
                    "adoption": [0.1, 0.2, 0.3, 0.5],
                }
            }
        }
    }
}

if __name__ == "__main__":
    result = optimize_scenario(data, objective="emissions")
    print("Success:", result["success"])
    print("Message:", result["message"])
    print("Optimized Adoption Rates:", result["optimized_adoption"])
    print("Objective Value (Total Emissions):", result["objective_value"]) 