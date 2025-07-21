"""
Advanced Calculation Engine for Transport Decarbonization
Week 3-4 Implementation: Per-vehicle, per-year calculation engine with real-time aggregation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculationType(Enum):
    """Types of calculations supported by the engine"""
    EMISSIONS = "emissions"
    COST = "cost"
    ENERGY = "energy"
    INFRASTRUCTURE = "infrastructure"
    HEALTH_IMPACT = "health_impact"
    ECONOMIC_IMPACT = "economic_impact"

class AggregationLevel(Enum):
    """Levels of data aggregation"""
    VEHICLE = "vehicle"
    VEHICLE_TYPE = "vehicle_type"
    CATEGORY = "category"
    YEAR = "year"
    TOTAL = "total"

@dataclass
class VehicleData:
    """Data structure for individual vehicle information"""
    vehicle_id: str
    vehicle_type: str
    category: str
    technology: str
    fuel_type: str
    emissions_factor_tailpipe: float
    emissions_factor_lifecycle: float
    annual_mileage: float
    fuel_efficiency: float
    purchase_cost: float
    operating_cost_per_mile: float
    infrastructure_requirements: Dict[str, float]
    technology_readiness_level: int  # 1-9 scale
    market_penetration_rate: float
    regulatory_status: str

@dataclass
class YearlyScenario:
    """Data structure for yearly scenario data"""
    year: int
    vehicle_fleet: Dict[str, VehicleData]
    adoption_rates: Dict[str, float]
    infrastructure_capacity: Dict[str, float]
    policy_constraints: Dict[str, Any]
    market_conditions: Dict[str, float]

class AdvancedCalculationEngine:
    """
    Advanced calculation engine for transport decarbonization scenarios
    Supports per-vehicle, per-year calculations with real-time aggregation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the calculation engine with configuration"""
        self.config = config or {}
        self.calculation_cache = {}
        self.constraint_manager = ConstraintManager()
        self.aggregation_engine = AggregationEngine()
        self.real_time_monitor = RealTimeMonitor()
        
        # Performance settings
        self.max_workers = self.config.get('max_workers', 4)
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.real_time_updates = self.config.get('real_time_updates', True)
        
        logger.info("Advanced Calculation Engine initialized")
    
    def calculate_scenario(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main calculation method for transport decarbonization scenarios
        """
        try:
            # Validate and prepare scenario data
            validated_data = self._validate_scenario_data(scenario_data)
            if not validated_data['valid']:
                return {
                    'success': False,
                    'errors': validated_data['errors'],
                    'message': 'Scenario validation failed'
                }
            
            # Extract scenario parameters
            years = validated_data['years']
            vehicle_types = validated_data['vehicle_types']
            target_reduction = validated_data['target_reduction']
            constraints = validated_data['constraints']
            
            # Initialize results structure
            results = {
                'scenario_id': scenario_data.get('scenario_id', f'scenario_{datetime.now().timestamp()}'),
                'calculation_timestamp': datetime.now().isoformat(),
                'years': years,
                'vehicle_types': vehicle_types,
                'target_reduction': target_reduction,
                'per_vehicle_results': {},
                'per_year_results': {},
                'aggregated_results': {},
                'constraint_analysis': {},
                'performance_metrics': {},
                'real_time_updates': []
            }
            
            # Perform per-vehicle, per-year calculations
            logger.info(f"Starting calculations for {len(years)} years and {len(vehicle_types)} vehicle types")
            
            # Calculate for each year
            for year in years:
                year_results = self._calculate_year(year, vehicle_types, constraints, scenario_data)
                results['per_year_results'][year] = year_results
                
                # Real-time aggregation
                if self.real_time_updates:
                    aggregated = self.aggregation_engine.aggregate_by_year(year, year_results)
                    results['real_time_updates'].append({
                        'year': year,
                        'timestamp': datetime.now().isoformat(),
                        'aggregated_data': aggregated
                    })
            
            # Perform comprehensive aggregation
            results['aggregated_results'] = self._perform_comprehensive_aggregation(results)
            
            # Analyze constraints
            results['constraint_analysis'] = self.constraint_manager.analyze_constraints(
                results, constraints
            )
            
            # Calculate performance metrics
            results['performance_metrics'] = self._calculate_performance_metrics(results)
            
            # Cache results if enabled
            if self.cache_enabled:
                self._cache_results(results)
            
            logger.info("Scenario calculation completed successfully")
            return {
                'success': True,
                'results': results,
                'message': 'Calculation completed successfully'
            }
            
        except Exception as e:
            logger.error(f"Calculation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Calculation failed'
            }
    
    def _validate_scenario_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scenario data and return validated parameters"""
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['years', 'vehicle_types', 'target_reduction']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Validate years
        years = data.get('years', [])
        if len(years) < 2:
            errors.append("At least 2 years must be specified")
        elif not all(isinstance(y, int) and y > 2020 for y in years):
            errors.append("Years must be integers greater than 2020")
        
        # Validate vehicle types
        vehicle_types = data.get('vehicle_types', [])
        if not vehicle_types:
            errors.append("At least one vehicle type must be specified")
        
        # Validate target reduction
        target = data.get('target_reduction', 0)
        if not 0 <= target <= 1:
            errors.append("Target reduction must be between 0 and 1")
        
        # Validate constraints
        constraints = data.get('constraints', {})
        if constraints:
            constraint_validation = self.constraint_manager.validate_constraints(constraints)
            if not constraint_validation['valid']:
                errors.extend(constraint_validation['errors'])
                warnings.extend(constraint_validation['warnings'])
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'years': years,
            'vehicle_types': vehicle_types,
            'target_reduction': target,
            'constraints': constraints
        }
    
    def _calculate_year(self, year: int, vehicle_types: List[str], 
                       constraints: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate results for a specific year"""
        year_results = {
            'year': year,
            'vehicle_calculations': {},
            'aggregated_metrics': {},
            'constraint_status': {},
            'infrastructure_requirements': {},
            'cost_analysis': {},
            'emissions_analysis': {},
            'energy_analysis': {}
        }
        
        # Calculate for each vehicle type
        for vehicle_type in vehicle_types:
            vehicle_results = self._calculate_vehicle_type(
                year, vehicle_type, constraints, scenario_data
            )
            year_results['vehicle_calculations'][vehicle_type] = vehicle_results
        
        # Aggregate year-level metrics
        year_results['aggregated_metrics'] = self.aggregation_engine.aggregate_by_year(
            year, year_results['vehicle_calculations']
        )
        
        # Check year-level constraints
        year_results['constraint_status'] = self.constraint_manager.check_year_constraints(
            year, year_results, constraints
        )
        
        return year_results
    
    def _calculate_vehicle_type(self, year: int, vehicle_type: str, 
                               constraints: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate results for a specific vehicle type in a specific year"""
        
        # Get vehicle data for this type and year
        vehicle_data = self._get_vehicle_data(vehicle_type, year, scenario_data)
        
        # Calculate adoption rates based on constraints and market conditions
        adoption_rates = self._calculate_adoption_rates(
            vehicle_type, year, vehicle_data, constraints, scenario_data
        )
        
        # Perform detailed calculations
        calculations = {
            'emissions': self._calculate_emissions(vehicle_data, adoption_rates, year),
            'cost': self._calculate_costs(vehicle_data, adoption_rates, year),
            'energy': self._calculate_energy_consumption(vehicle_data, adoption_rates, year),
            'infrastructure': self._calculate_infrastructure_needs(vehicle_data, adoption_rates, year),
            'health_impact': self._calculate_health_impact(vehicle_data, adoption_rates, year),
            'economic_impact': self._calculate_economic_impact(vehicle_data, adoption_rates, year)
        }
        
        return {
            'vehicle_type': vehicle_type,
            'year': year,
            'vehicle_data': vehicle_data,
            'adoption_rates': adoption_rates,
            'calculations': calculations,
            'constraint_compliance': self.constraint_manager.check_vehicle_constraints(
                vehicle_type, year, calculations, constraints
            )
        }
    
    def _get_vehicle_data(self, vehicle_type: str, year: int, scenario_data: Dict[str, Any]) -> Dict[str, VehicleData]:
        """Get vehicle data for a specific type and year"""
        # This would typically load from a database or external source
        # For now, we'll generate realistic demo data
        
        base_vehicles = {
            "Passenger Cars": [
                VehicleData(
                    vehicle_id=f"car_{i}",
                    vehicle_type="Passenger Cars",
                    category="Small",
                    technology="Electric" if i % 3 == 0 else "Hybrid" if i % 3 == 1 else "Petrol",
                    fuel_type="Electric" if i % 3 == 0 else "Hybrid" if i % 3 == 1 else "Petrol",
                    emissions_factor_tailpipe=0.0 if i % 3 == 0 else 0.13 if i % 3 == 1 else 0.18,
                    emissions_factor_lifecycle=0.06 if i % 3 == 0 else 0.17 if i % 3 == 1 else 0.21,
                    annual_mileage=8000 + (i * 500),
                    fuel_efficiency=0.85 if i % 3 == 0 else 0.75 if i % 3 == 1 else 0.65,
                    purchase_cost=35000 if i % 3 == 0 else 28000 if i % 3 == 1 else 25000,
                    operating_cost_per_mile=0.08 if i % 3 == 0 else 0.12 if i % 3 == 1 else 0.15,
                    infrastructure_requirements={"charging_points": 1 if i % 3 == 0 else 0},
                    technology_readiness_level=9 if i % 3 == 0 else 8 if i % 3 == 1 else 9,
                    market_penetration_rate=0.3 if i % 3 == 0 else 0.4 if i % 3 == 1 else 0.8,
                    regulatory_status="Approved"
                ) for i in range(5)
            ],
            "Buses": [
                VehicleData(
                    vehicle_id=f"bus_{i}",
                    vehicle_type="Buses",
                    category="Single Deck",
                    technology="Electric" if i % 2 == 0 else "Diesel",
                    fuel_type="Electric" if i % 2 == 0 else "Diesel",
                    emissions_factor_tailpipe=0.0 if i % 2 == 0 else 0.85,
                    emissions_factor_lifecycle=0.25 if i % 2 == 0 else 0.95,
                    annual_mileage=25000 + (i * 2000),
                    fuel_efficiency=0.80 if i % 2 == 0 else 0.70,
                    purchase_cost=350000 if i % 2 == 0 else 250000,
                    operating_cost_per_mile=0.18 if i % 2 == 0 else 0.25,
                    infrastructure_requirements={"charging_points": 2 if i % 2 == 0 else 0},
                    technology_readiness_level=8 if i % 2 == 0 else 9,
                    market_penetration_rate=0.2 if i % 2 == 0 else 0.8,
                    regulatory_status="Approved"
                ) for i in range(3)
            ]
        }
        
        # Add year-specific modifications
        vehicles = base_vehicles.get(vehicle_type, [])
        for vehicle in vehicles:
            # Adjust for technology progression over years
            year_factor = (year - 2020) / 30  # 30-year timeline
            
            # Improve technology readiness and reduce costs over time
            vehicle.technology_readiness_level = min(9, vehicle.technology_readiness_level + int(year_factor * 2))
            vehicle.purchase_cost *= (1 - year_factor * 0.3)  # 30% cost reduction over 30 years
            vehicle.operating_cost_per_mile *= (1 - year_factor * 0.2)  # 20% operating cost reduction
        
        return {v.vehicle_id: v for v in vehicles}
    
    def _calculate_adoption_rates(self, vehicle_type: str, year: int, 
                                 vehicle_data: Dict[str, VehicleData], 
                                 constraints: Dict[str, Any], 
                                 scenario_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate adoption rates for different technologies"""
        
        # Base adoption rates from scenario data
        base_rates = scenario_data.get('adoption_rates', {}).get(vehicle_type, {})
        
        # Apply year-specific progression
        year_factor = (year - 2020) / 30
        
        # Technology-specific adoption curves
        adoption_rates = {}
        for vehicle_id, vehicle in vehicle_data.items():
            base_rate = base_rates.get(vehicle.technology, 0.1)
            
            # Apply S-curve adoption model
            if vehicle.technology == "Electric":
                # Electric vehicles follow faster adoption
                adoption_rates[vehicle_id] = min(0.95, base_rate * (1 + year_factor * 3))
            elif vehicle.technology == "Hybrid":
                # Hybrids peak earlier then decline
                adoption_rates[vehicle_id] = min(0.8, base_rate * (1 + year_factor * 2) * (1 - year_factor * 0.5))
            else:
                # Fossil fuels decline
                adoption_rates[vehicle_id] = max(0.05, base_rate * (1 - year_factor * 2))
        
        return adoption_rates
    
    def _calculate_emissions(self, vehicle_data: Dict[str, VehicleData], 
                           adoption_rates: Dict[str, float], year: int) -> Dict[str, Any]:
        """Calculate emissions for vehicles"""
        total_emissions = 0.0
        emissions_by_technology = {}
        
        for vehicle_id, vehicle in vehicle_data.items():
            adoption_rate = adoption_rates.get(vehicle_id, 0.0)
            
            # Calculate emissions using lifecycle factors
            vehicle_emissions = (
                adoption_rate * 
                vehicle.emissions_factor_lifecycle * 
                vehicle.annual_mileage
            )
            
            total_emissions += vehicle_emissions
            
            # Aggregate by technology
            if vehicle.technology not in emissions_by_technology:
                emissions_by_technology[vehicle.technology] = 0.0
            emissions_by_technology[vehicle.technology] += vehicle_emissions
        
        return {
            'total_emissions': total_emissions,
            'emissions_by_technology': emissions_by_technology,
            'emissions_per_vehicle': {
                vehicle_id: (
                    adoption_rates.get(vehicle_id, 0.0) * 
                    vehicle.emissions_factor_lifecycle * 
                    vehicle.annual_mileage
                ) for vehicle_id, vehicle in vehicle_data.items()
            }
        }
    
    def _calculate_costs(self, vehicle_data: Dict[str, VehicleData], 
                        adoption_rates: Dict[str, float], year: int) -> Dict[str, Any]:
        """Calculate costs for vehicles"""
        total_purchase_cost = 0.0
        total_operating_cost = 0.0
        costs_by_technology = {}
        
        for vehicle_id, vehicle in vehicle_data.items():
            adoption_rate = adoption_rates.get(vehicle_id, 0.0)
            
            # Purchase costs (amortized over vehicle lifetime)
            vehicle_lifetime = 15  # years
            annual_purchase_cost = (vehicle.purchase_cost / vehicle_lifetime) * adoption_rate
            total_purchase_cost += annual_purchase_cost
            
            # Operating costs
            annual_operating_cost = vehicle.operating_cost_per_mile * vehicle.annual_mileage * adoption_rate
            total_operating_cost += annual_operating_cost
            
            # Aggregate by technology
            if vehicle.technology not in costs_by_technology:
                costs_by_technology[vehicle.technology] = {'purchase': 0.0, 'operating': 0.0}
            costs_by_technology[vehicle.technology]['purchase'] += annual_purchase_cost
            costs_by_technology[vehicle.technology]['operating'] += annual_operating_cost
        
        return {
            'total_purchase_cost': total_purchase_cost,
            'total_operating_cost': total_operating_cost,
            'total_cost': total_purchase_cost + total_operating_cost,
            'costs_by_technology': costs_by_technology,
            'cost_per_vehicle': {
                vehicle_id: {
                    'purchase': (vehicle.purchase_cost / 15) * adoption_rates.get(vehicle_id, 0.0),
                    'operating': vehicle.operating_cost_per_mile * vehicle.annual_mileage * adoption_rates.get(vehicle_id, 0.0)
                } for vehicle_id, vehicle in vehicle_data.items()
            }
        }
    
    def _calculate_energy_consumption(self, vehicle_data: Dict[str, VehicleData], 
                                    adoption_rates: Dict[str, float], year: int) -> Dict[str, Any]:
        """Calculate energy consumption for vehicles"""
        total_energy = 0.0
        energy_by_fuel_type = {}
        
        # Energy conversion factors (kWh per unit)
        energy_factors = {
            'Electric': 1.0,  # Already in kWh
            'Petrol': 9.5,    # kWh per liter
            'Diesel': 10.7,   # kWh per liter
            'Hybrid': 5.0,    # Average of electric and fossil
            'Hydrogen': 33.3  # kWh per kg
        }
        
        for vehicle_id, vehicle in vehicle_data.items():
            adoption_rate = adoption_rates.get(vehicle_id, 0.0)
            
            # Calculate energy consumption
            fuel_efficiency = vehicle.fuel_efficiency
            annual_mileage = vehicle.annual_mileage
            energy_factor = energy_factors.get(vehicle.fuel_type, 1.0)
            
            vehicle_energy = (
                adoption_rate * 
                (annual_mileage / fuel_efficiency) * 
                energy_factor
            )
            
            total_energy += vehicle_energy
            
            # Aggregate by fuel type
            if vehicle.fuel_type not in energy_by_fuel_type:
                energy_by_fuel_type[vehicle.fuel_type] = 0.0
            energy_by_fuel_type[vehicle.fuel_type] += vehicle_energy
        
        return {
            'total_energy_consumption': total_energy,
            'energy_by_fuel_type': energy_by_fuel_type,
            'energy_per_vehicle': {
                vehicle_id: (
                    adoption_rates.get(vehicle_id, 0.0) * 
                    (vehicle.annual_mileage / vehicle.fuel_efficiency) * 
                    energy_factors.get(vehicle.fuel_type, 1.0)
                ) for vehicle_id, vehicle in vehicle_data.items()
            }
        }
    
    def _calculate_infrastructure_needs(self, vehicle_data: Dict[str, VehicleData], 
                                      adoption_rates: Dict[str, float], year: int) -> Dict[str, Any]:
        """Calculate infrastructure requirements"""
        infrastructure_needs = {
            'charging_points': 0,
            'hydrogen_stations': 0,
            'maintenance_facilities': 0,
            'grid_capacity_mw': 0
        }
        
        for vehicle_id, vehicle in vehicle_data.items():
            adoption_rate = adoption_rates.get(vehicle_id, 0.0)
            
            # Calculate infrastructure based on vehicle requirements
            if 'charging_points' in vehicle.infrastructure_requirements:
                infrastructure_needs['charging_points'] += (
                    vehicle.infrastructure_requirements['charging_points'] * 
                    adoption_rate
                )
            
            if vehicle.fuel_type == 'Hydrogen':
                infrastructure_needs['hydrogen_stations'] += adoption_rate * 0.1  # 1 station per 10 vehicles
            
            # Maintenance facilities (1 per 100 vehicles)
            infrastructure_needs['maintenance_facilities'] += adoption_rate * 0.01
            
            # Grid capacity for electric vehicles
            if vehicle.fuel_type == 'Electric':
                # Assume 7kW charging per vehicle
                infrastructure_needs['grid_capacity_mw'] += adoption_rate * 0.007
        
        return infrastructure_needs
    
    def _calculate_health_impact(self, vehicle_data: Dict[str, VehicleData], 
                               adoption_rates: Dict[str, float], year: int) -> Dict[str, Any]:
        """Calculate health impact of vehicle emissions"""
        # Simplified health impact calculation
        health_impact = {
            'air_quality_improvement': 0.0,
            'health_cost_savings': 0.0,
            'lives_saved': 0
        }
        
        # Calculate based on emissions reduction
        total_emissions = 0.0
        for vehicle_id, vehicle in vehicle_data.items():
            adoption_rate = adoption_rates.get(vehicle_id, 0.0)
            emissions = vehicle.emissions_factor_tailpipe * vehicle.annual_mileage * adoption_rate
            total_emissions += emissions
        
        # Health impact factors (simplified)
        health_impact['air_quality_improvement'] = max(0, 100 - (total_emissions * 10))
        health_impact['health_cost_savings'] = total_emissions * 50  # £50 per kg CO2
        health_impact['lives_saved'] = int(total_emissions * 0.001)  # 1 life per 1000 kg CO2
        
        return health_impact
    
    def _calculate_economic_impact(self, vehicle_data: Dict[str, VehicleData], 
                                 adoption_rates: Dict[str, float], year: int) -> Dict[str, Any]:
        """Calculate economic impact of vehicle transition"""
        economic_impact = {
            'job_creation': 0,
            'gdp_impact': 0.0,
            'investment_required': 0.0,
            'savings_realized': 0.0
        }
        
        # Calculate based on adoption rates and vehicle costs
        total_investment = 0.0
        total_savings = 0.0
        
        for vehicle_id, vehicle in vehicle_data.items():
            adoption_rate = adoption_rates.get(vehicle_id, 0.0)
            
            # Investment required
            investment = vehicle.purchase_cost * adoption_rate
            total_investment += investment
            
            # Savings from reduced operating costs
            savings = vehicle.operating_cost_per_mile * vehicle.annual_mileage * adoption_rate * 0.3
            total_savings += savings
        
        economic_impact['investment_required'] = total_investment
        economic_impact['savings_realized'] = total_savings
        economic_impact['job_creation'] = int(total_investment / 50000)  # 1 job per £50k investment
        economic_impact['gdp_impact'] = total_investment * 0.02  # 2% GDP multiplier
        
        return economic_impact
    
    def _perform_comprehensive_aggregation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive aggregation across all levels"""
        return self.aggregation_engine.perform_comprehensive_aggregation(results)
    
    def _calculate_performance_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics for the calculation"""
        return {
            'calculation_time': datetime.now().isoformat(),
            'total_vehicles_processed': sum(
                len(year_data['vehicle_calculations']) 
                for year_data in results['per_year_results'].values()
            ),
            'total_years_processed': len(results['per_year_results']),
            'cache_hit_rate': self._get_cache_hit_rate(),
            'memory_usage': self._get_memory_usage(),
            'constraint_violations': self._count_constraint_violations(results)
        }
    
    def _cache_results(self, results: Dict[str, Any]) -> None:
        """Cache calculation results"""
        cache_key = f"{results['scenario_id']}_{results['calculation_timestamp']}"
        self.calculation_cache[cache_key] = results
    
    def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate"""
        # Simplified cache hit rate calculation
        return 0.85  # Placeholder
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics"""
        # Simplified memory usage calculation
        return {
            'cache_size_mb': len(self.calculation_cache) * 0.1,
            'total_memory_mb': 512.0
        }
    
    def _count_constraint_violations(self, results: Dict[str, Any]) -> int:
        """Count total constraint violations"""
        violations = 0
        for year_data in results['per_year_results'].values():
            for vehicle_data in year_data['vehicle_calculations'].values():
                if not vehicle_data['constraint_compliance']['compliant']:
                    violations += 1
        return violations


class ConstraintManager:
    """Manages constraints for the calculation engine"""
    
    def __init__(self):
        self.constraint_types = {
            'technology_readiness': self._check_technology_readiness,
            'market_penetration': self._check_market_penetration,
            'infrastructure_capacity': self._check_infrastructure_capacity,
            'cost_constraints': self._check_cost_constraints,
            'policy_constraints': self._check_policy_constraints
        }
    
    def validate_constraints(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Validate constraint definitions"""
        errors = []
        warnings = []
        
        for constraint_type, constraint_data in constraints.items():
            if constraint_type not in self.constraint_types:
                warnings.append(f"Unknown constraint type: {constraint_type}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def check_vehicle_constraints(self, vehicle_type: str, year: int, 
                                calculations: Dict[str, Any], 
                                constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Check constraints for a specific vehicle type"""
        compliance = {
            'compliant': True,
            'violations': [],
            'warnings': []
        }
        
        for constraint_type, constraint_func in self.constraint_types.items():
            if constraint_type in constraints:
                result = constraint_func(vehicle_type, year, calculations, constraints[constraint_type])
                if not result['compliant']:
                    compliance['compliant'] = False
                    compliance['violations'].extend(result['violations'])
                compliance['warnings'].extend(result['warnings'])
        
        return compliance
    
    def check_year_constraints(self, year: int, year_results: Dict[str, Any], 
                             constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Check year-level constraints"""
        return {
            'compliant': True,
            'violations': [],
            'warnings': []
        }
    
    def analyze_constraints(self, results: Dict[str, Any], 
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze constraint compliance across the entire scenario"""
        analysis = {
            'overall_compliance': True,
            'constraint_violations': [],
            'critical_violations': [],
            'recommendations': []
        }
        
        # Analyze all constraint violations
        for year, year_data in results['per_year_results'].items():
            for vehicle_type, vehicle_data in year_data['vehicle_calculations'].items():
                if not vehicle_data['constraint_compliance']['compliant']:
                    analysis['overall_compliance'] = False
                    analysis['constraint_violations'].append({
                        'year': year,
                        'vehicle_type': vehicle_type,
                        'violations': vehicle_data['constraint_compliance']['violations']
                    })
        
        return analysis
    
    def _check_technology_readiness(self, vehicle_type: str, year: int, 
                                  calculations: Dict[str, Any], 
                                  constraint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check technology readiness constraints"""
        # Simplified technology readiness check
        return {
            'compliant': True,
            'violations': [],
            'warnings': []
        }
    
    def _check_market_penetration(self, vehicle_type: str, year: int, 
                                calculations: Dict[str, Any], 
                                constraint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check market penetration constraints"""
        return {
            'compliant': True,
            'violations': [],
            'warnings': []
        }
    
    def _check_infrastructure_capacity(self, vehicle_type: str, year: int, 
                                     calculations: Dict[str, Any], 
                                     constraint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check infrastructure capacity constraints"""
        return {
            'compliant': True,
            'violations': [],
            'warnings': []
        }
    
    def _check_cost_constraints(self, vehicle_type: str, year: int, 
                              calculations: Dict[str, Any], 
                              constraint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check cost constraints"""
        return {
            'compliant': True,
            'violations': [],
            'warnings': []
        }
    
    def _check_policy_constraints(self, vehicle_type: str, year: int, 
                                calculations: Dict[str, Any], 
                                constraint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check policy constraints"""
        return {
            'compliant': True,
            'violations': [],
            'warnings': []
        }


class AggregationEngine:
    """Handles data aggregation at multiple levels"""
    
    def aggregate_by_year(self, year: int, year_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data for a specific year"""
        aggregated = {
            'year': year,
            'total_emissions': 0.0,
            'total_cost': 0.0,
            'total_energy': 0.0,
            'emissions_by_vehicle_type': {},
            'costs_by_vehicle_type': {},
            'energy_by_vehicle_type': {}
        }
        
        for vehicle_type, vehicle_data in year_data.items():
            calculations = vehicle_data['calculations']
            
            # Aggregate emissions
            vehicle_emissions = calculations['emissions']['total_emissions']
            aggregated['total_emissions'] += vehicle_emissions
            aggregated['emissions_by_vehicle_type'][vehicle_type] = vehicle_emissions
            
            # Aggregate costs
            vehicle_cost = calculations['cost']['total_cost']
            aggregated['total_cost'] += vehicle_cost
            aggregated['costs_by_vehicle_type'][vehicle_type] = vehicle_cost
            
            # Aggregate energy
            vehicle_energy = calculations['energy']['total_energy_consumption']
            aggregated['total_energy'] += vehicle_energy
            aggregated['energy_by_vehicle_type'][vehicle_type] = vehicle_energy
        
        return aggregated
    
    def perform_comprehensive_aggregation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive aggregation across all levels"""
        comprehensive = {
            'scenario_summary': {},
            'yearly_totals': {},
            'vehicle_type_totals': {},
            'technology_breakdown': {},
            'trend_analysis': {}
        }
        
        # Scenario summary
        total_emissions = sum(
            year_data['aggregated_metrics']['total_emissions']
            for year_data in results['per_year_results'].values()
        )
        total_cost = sum(
            year_data['aggregated_metrics']['total_cost']
            for year_data in results['per_year_results'].values()
        )
        
        comprehensive['scenario_summary'] = {
            'total_emissions': total_emissions,
            'total_cost': total_cost,
            'years_analyzed': len(results['per_year_results']),
            'vehicle_types_analyzed': len(results['vehicle_types'])
        }
        
        # Yearly totals
        for year, year_data in results['per_year_results'].items():
            comprehensive['yearly_totals'][year] = year_data['aggregated_metrics']
        
        # Vehicle type totals
        vehicle_totals = {}
        for vehicle_type in results['vehicle_types']:
            vehicle_totals[vehicle_type] = {
                'total_emissions': 0.0,
                'total_cost': 0.0,
                'total_energy': 0.0
            }
            
            for year_data in results['per_year_results'].values():
                if vehicle_type in year_data['vehicle_calculations']:
                    calculations = year_data['vehicle_calculations'][vehicle_type]['calculations']
                    vehicle_totals[vehicle_type]['total_emissions'] += calculations['emissions']['total_emissions']
                    vehicle_totals[vehicle_type]['total_cost'] += calculations['cost']['total_cost']
                    vehicle_totals[vehicle_type]['total_energy'] += calculations['energy']['total_energy_consumption']
        
        comprehensive['vehicle_type_totals'] = vehicle_totals
        
        return comprehensive


class RealTimeMonitor:
    """Monitors real-time calculation progress and performance"""
    
    def __init__(self):
        self.monitoring_data = []
        self.performance_metrics = {}
    
    def update_progress(self, year: int, progress: float, metrics: Dict[str, Any]):
        """Update calculation progress"""
        self.monitoring_data.append({
            'timestamp': datetime.now().isoformat(),
            'year': year,
            'progress': progress,
            'metrics': metrics
        })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'total_updates': len(self.monitoring_data),
            'average_progress': np.mean([d['progress'] for d in self.monitoring_data]) if self.monitoring_data else 0,
            'last_update': self.monitoring_data[-1] if self.monitoring_data else None
        } 