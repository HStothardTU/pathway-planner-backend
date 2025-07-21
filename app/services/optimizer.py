import numpy as np
from scipy.optimize import minimize, LinearConstraint, Bounds
from typing import Dict, List, Any, Optional
import pandas as pd

def optimize_transport_pathway(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced optimization function for transport decarbonization pathways
    Supports multiple vehicle types, usage patterns, and constraints
    """
    try:
        # Extract parameters
        years = data.get('years', [2025, 2030, 2040, 2050])
        target_reduction = data.get('target_emissions_reduction', 0.5)
        max_annual_change = data.get('max_annual_change', 0.1)
        vehicle_types = data.get('vehicle_types', ['Passenger Cars'])
        emissions_factors = data.get('emissions_factors', {})
        usage_patterns = data.get('usage_patterns', {})
        enable_constraints = data.get('enable_constraints', True)
        
        # Validate inputs
        if not years or len(years) < 2:
            raise ValueError("At least 2 years must be specified")
        
        if not vehicle_types:
            raise ValueError("At least one vehicle type must be specified")
        
        # Generate demo data if not provided
        miles_traveled = data.get('miles_traveled', {})
        fuel_mix = data.get('fuel_mix', {})
        
        if not miles_traveled or not fuel_mix:
            miles_traveled, fuel_mix = generate_demo_data(vehicle_types, years, usage_patterns)
        
        # Prepare optimization problem
        n_years = len(years)
        n_vehicle_types = len(vehicle_types)
        
        # Create initial state
        initial_state = create_initial_state(vehicle_types, fuel_mix, years)
        
        # Define objective function
        def objective(x):
            return calculate_total_emissions(x, vehicle_types, emissions_factors, miles_traveled, years)
        
        # Define constraints
        constraints = []
        
        # Target reduction constraint
        initial_emissions = calculate_total_emissions(initial_state, vehicle_types, emissions_factors, miles_traveled, years)
        target_emissions = initial_emissions * (1 - target_reduction)
        
        constraints.append({
            'type': 'ineq',
            'fun': lambda x: target_emissions - calculate_total_emissions(x, vehicle_types, emissions_factors, miles_traveled, years)
        })
        
        # Annual change constraints
        if enable_constraints:
            for i in range(n_years - 1):
                for j in range(n_vehicle_types):
                    # Maximum increase constraint
                    constraints.append({
                        'type': 'ineq',
                        'fun': lambda x, i=i, j=j: max_annual_change - (x[i * n_vehicle_types + j] - x[(i-1) * n_vehicle_types + j])
                    })
                    # Maximum decrease constraint
                    constraints.append({
                        'type': 'ineq',
                        'fun': lambda x, i=i, j=j: max_annual_change - (x[(i-1) * n_vehicle_types + j] - x[i * n_vehicle_types + j])
                    })
        
        # Bounds (0 to 1 for adoption rates)
        bounds = Bounds(0, 1)
        
        # Run optimization
        result = minimize(
            objective,
            initial_state,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if not result.success:
            # Try with relaxed constraints
            relaxed_constraints = [constraints[0]]  # Keep only target constraint
            result = minimize(
                objective,
                initial_state,
                method='SLSQP',
                bounds=bounds,
                constraints=relaxed_constraints,
                options={'maxiter': 1000}
            )
        
        # Process results
        optimized_adoption = result.x.reshape(n_years, n_vehicle_types)
        
        # Calculate detailed results
        results = calculate_detailed_results(
            optimized_adoption, vehicle_types, emissions_factors, 
            miles_traveled, years, initial_emissions
        )
        
        return {
            "success": result.success,
            "message": result.message,
            "optimized_adoption": optimized_adoption.tolist(),
            "vehicle_types": vehicle_types,
            "years": years,
            "results": results,
            "optimization_info": {
                "iterations": result.nit,
                "function_evaluations": result.nfev,
                "final_objective": result.fun
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Optimization failed: {str(e)}",
            "error": str(e)
        }

def generate_demo_data(vehicle_types: List[str], years: List[int], usage_patterns: Dict = None) -> tuple:
    """Generate realistic demo data for optimization"""
    miles_traveled = {}
    fuel_mix = {}
    
    # Base usage patterns if not provided
    if not usage_patterns:
        usage_patterns = {
            "Passenger Cars": {"Petrol Car (Medium)": 10000},
            "Buses": {"Diesel Bus (Single Deck)": 25000},
            "Heavy Goods Vehicles (HGVs)": {"Diesel Rigid HGV (7.5-17t)": 15000},
            "Vans / Light Goods Vehicles (LGVs)": {"Diesel Van (Medium)": 15000},
            "Motorcycles": {"Petrol Motorcycle (Medium)": 5000}
        }
    
    # Generate miles traveled data
    for year in years:
        miles_traveled[year] = {}
        for vehicle_type in vehicle_types:
            if vehicle_type in usage_patterns:
                for vehicle, base_usage in usage_patterns[vehicle_type].items():
                    # Add some year-to-year variation
                    growth_factor = 1 + 0.02 * (year - years[0])  # 2% annual growth
                    miles_traveled[year][vehicle] = base_usage * growth_factor
    
    # Generate initial fuel mix (starting with mostly fossil fuels)
    for year in years:
        fuel_mix[year] = {}
        for vehicle_type in vehicle_types:
            if vehicle_type in usage_patterns:
                for vehicle in usage_patterns[vehicle_type].keys():
                    if "Electric" in vehicle or "Hydrogen" in vehicle:
                        fuel_mix[year][vehicle] = 0.05  # 5% initial adoption
                    elif "Hybrid" in vehicle:
                        fuel_mix[year][vehicle] = 0.15  # 15% initial adoption
                    else:
                        fuel_mix[year][vehicle] = 0.80  # 80% fossil fuels
    
    return miles_traveled, fuel_mix

def create_initial_state(vehicle_types: List[str], fuel_mix: Dict, years: List[int]) -> np.ndarray:
    """Create initial state vector for optimization"""
    n_years = len(years)
    n_vehicle_types = len(vehicle_types)
    
    initial_state = np.zeros(n_years * n_vehicle_types)
    
    for i, year in enumerate(years):
        for j, vehicle_type in enumerate(vehicle_types):
            # Use average adoption rate for this vehicle type in this year
            if year in fuel_mix and vehicle_type in fuel_mix[year]:
                adoption_rates = list(fuel_mix[year][vehicle_type].values())
                initial_state[i * n_vehicle_types + j] = np.mean(adoption_rates)
            else:
                initial_state[i * n_vehicle_types + j] = 0.1  # Default 10%
    
    return initial_state

def calculate_total_emissions(adoption_rates: np.ndarray, vehicle_types: List[str], 
                            emissions_factors: Dict, miles_traveled: Dict, years: List[int]) -> float:
    """Calculate total emissions for given adoption rates"""
    total_emissions = 0.0
    n_vehicle_types = len(vehicle_types)
    
    for i, year in enumerate(years):
        for j, vehicle_type in enumerate(vehicle_types):
            adoption_rate = adoption_rates[i * n_vehicle_types + j]
            
            if vehicle_type in emissions_factors and year in miles_traveled:
                for vehicle, emissions in emissions_factors[vehicle_type].items():
                    if vehicle in miles_traveled[year]:
                        # Use lifecycle emissions
                        emission_factor = emissions.get('lifecycle', emissions.get('tailpipe', 0))
                        miles = miles_traveled[year][vehicle]
                        total_emissions += adoption_rate * emission_factor * miles
    
    return total_emissions

def calculate_detailed_results(optimized_adoption: np.ndarray, vehicle_types: List[str],
                             emissions_factors: Dict, miles_traveled: Dict, 
                             years: List[int], initial_emissions: float) -> Dict[str, Any]:
    """Calculate detailed results for visualization"""
    results = {
        "emissions_by_year": [],
        "emissions_by_vehicle_type": {},
        "adoption_progress": {},
        "cost_analysis": {},
        "summary": {}
    }
    
    # Calculate emissions by year
    for i, year in enumerate(years):
        year_emissions = 0.0
        for j, vehicle_type in enumerate(vehicle_types):
            adoption_rate = optimized_adoption[i, j]
            
            if vehicle_type in emissions_factors and year in miles_traveled:
                for vehicle, emissions in emissions_factors[vehicle_type].items():
                    if vehicle in miles_traveled[year]:
                        emission_factor = emissions.get('lifecycle', emissions.get('tailpipe', 0))
                        miles = miles_traveled[year][vehicle]
                        year_emissions += adoption_rate * emission_factor * miles
        
        results["emissions_by_year"].append({
            "year": year,
            "emissions": year_emissions,
            "reduction_percent": ((initial_emissions - year_emissions) / initial_emissions) * 100
        })
    
    # Calculate emissions by vehicle type
    for vehicle_type in vehicle_types:
        results["emissions_by_vehicle_type"][vehicle_type] = []
        for i, year in enumerate(years):
            vehicle_emissions = 0.0
            adoption_rate = optimized_adoption[i, vehicle_types.index(vehicle_type)]
            
            if vehicle_type in emissions_factors and year in miles_traveled:
                for vehicle, emissions in emissions_factors[vehicle_type].items():
                    if vehicle in miles_traveled[year]:
                        emission_factor = emissions.get('lifecycle', emissions.get('tailpipe', 0))
                        miles = miles_traveled[year][vehicle]
                        vehicle_emissions += adoption_rate * emission_factor * miles
            
            results["emissions_by_vehicle_type"][vehicle_type].append({
                "year": year,
                "emissions": vehicle_emissions,
                "adoption_rate": adoption_rate
            })
    
    # Calculate adoption progress
    for j, vehicle_type in enumerate(vehicle_types):
        results["adoption_progress"][vehicle_type] = []
        for i, year in enumerate(years):
            results["adoption_progress"][vehicle_type].append({
                "year": year,
                "adoption_rate": optimized_adoption[i, j] * 100
            })
    
    # Calculate cost analysis (simplified)
    results["cost_analysis"] = calculate_cost_analysis(optimized_adoption, vehicle_types, years)
    
    # Summary statistics
    final_emissions = results["emissions_by_year"][-1]["emissions"]
    total_reduction = ((initial_emissions - final_emissions) / initial_emissions) * 100
    
    results["summary"] = {
        "initial_emissions": initial_emissions,
        "final_emissions": final_emissions,
        "total_reduction_percent": total_reduction,
        "years_analyzed": len(years),
        "vehicle_types_analyzed": len(vehicle_types),
        "target_achieved": total_reduction >= 50  # Assuming 50% target
    }
    
    return results

def calculate_cost_analysis(optimized_adoption: np.ndarray, vehicle_types: List[str], 
                          years: List[int]) -> Dict[str, Any]:
    """Calculate simplified cost analysis"""
    # Simplified cost factors (in practice, these would come from detailed cost models)
    cost_factors = {
        "Passenger Cars": {"fossil": 0.12, "electric": 0.08, "hydrogen": 0.15},
        "Buses": {"fossil": 0.25, "electric": 0.18, "hydrogen": 0.22},
        "Heavy Goods Vehicles (HGVs)": {"fossil": 0.35, "electric": 0.28, "hydrogen": 0.32},
        "Vans / Light Goods Vehicles (LGVs)": {"fossil": 0.20, "electric": 0.15, "hydrogen": 0.18},
        "Motorcycles": {"fossil": 0.08, "electric": 0.05, "hydrogen": 0.10}
    }
    
    cost_analysis = {
        "total_cost_by_year": [],
        "cost_by_vehicle_type": {},
        "cost_breakdown": {}
    }
    
    for i, year in enumerate(years):
        year_cost = 0.0
        for j, vehicle_type in enumerate(vehicle_types):
            adoption_rate = optimized_adoption[i, j]
            
            # Simplified cost calculation
            if vehicle_type in cost_factors:
                # Assume mix of technologies based on adoption rate
                fossil_cost = cost_factors[vehicle_type]["fossil"] * (1 - adoption_rate)
                clean_cost = cost_factors[vehicle_type]["electric"] * adoption_rate
                year_cost += fossil_cost + clean_cost
        
        cost_analysis["total_cost_by_year"].append({
            "year": year,
            "cost_per_mile": year_cost
        })
    
    return cost_analysis

def validate_optimization_inputs(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate optimization inputs and provide feedback"""
    errors = []
    warnings = []
    
    # Check required fields
    required_fields = ['years', 'target_emissions_reduction', 'vehicle_types']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings}
    
    # Validate years
    years = data.get('years', [])
    if len(years) < 2:
        errors.append("At least 2 years must be specified")
    
    # Validate target reduction
    target = data.get('target_emissions_reduction', 0)
    if not 0 <= target <= 1:
        errors.append("Target emissions reduction must be between 0 and 1")
    
    # Validate vehicle types
    vehicle_types = data.get('vehicle_types', [])
    if not vehicle_types:
        errors.append("At least one vehicle type must be specified")
    
    # Check emissions factors
    emissions_factors = data.get('emissions_factors', {})
    if not emissions_factors:
        warnings.append("No emissions factors provided - using defaults")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    } 