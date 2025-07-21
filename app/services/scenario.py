from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import Scenario
from app.api.v1.schemas import ScenarioCreate, ScenarioUpdate, ScenarioRead

def validate_scenario_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced parameter validation with detailed feedback
    """
    errors = []
    warnings = []
    suggestions = []
    
    # Required parameters check
    required_keys = ['years', 'target_emissions_reduction', 'max_annual_change', 'vehicle_types']
    for key in required_keys:
        if key not in parameters:
            errors.append(f"Missing required parameter: {key}")
    
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    # Years validation
    years = parameters.get('years', [])
    if not isinstance(years, list):
        errors.append("Years must be a list")
    elif len(years) < 2:
        errors.append("At least 2 years must be specified")
    elif len(years) > 10:
        errors.append("Maximum 10 years allowed")
    else:
        # Check for valid years and progression
        try:
            years_int = [int(year) for year in years]
            if years_int != sorted(years_int):
                errors.append("Years must be in ascending order")
            
            # Check for reasonable year gaps
            for i in range(len(years_int) - 1):
                gap = years_int[i+1] - years_int[i]
                if gap < 1:
                    errors.append("Years must have at least 1 year gap")
                elif gap > 10:
                    warnings.append(f"Large gap between {years_int[i]} and {years_int[i+1]} - consider intermediate years")
            
            # Check for reasonable year range
            if years_int[0] < 2020:
                warnings.append("Starting year before 2020 may not reflect current technology")
            if years_int[-1] > 2060:
                warnings.append("End year after 2060 may have high uncertainty")
                
        except (ValueError, TypeError):
            errors.append("Years must be valid integers")
    
    # Target reduction validation
    target = parameters.get('target_emissions_reduction', 0)
    if not isinstance(target, (int, float)):
        errors.append("Target emissions reduction must be a number")
    elif not 0 <= target <= 1:
        errors.append("Target emissions reduction must be between 0 and 1")
    elif target > 0.8:
        warnings.append("Very high reduction target - ensure this is realistic")
        suggestions.append("Consider breaking down into intermediate targets")
    elif target < 0.1:
        warnings.append("Low reduction target - may not achieve significant decarbonization")
    
    # Max annual change validation
    max_change = parameters.get('max_annual_change', 0)
    if not isinstance(max_change, (int, float)):
        errors.append("Maximum annual change must be a number")
    elif not 0.05 <= max_change <= 0.3:
        errors.append("Maximum annual change must be between 0.05 and 0.3")
    elif max_change > 0.2:
        warnings.append("High annual change rate - may be challenging to achieve")
        suggestions.append("Consider a more gradual transition")
    elif max_change < 0.08:
        warnings.append("Low annual change rate - may not meet targets")
    
    # Vehicle types validation
    vehicle_types = parameters.get('vehicle_types', [])
    if not isinstance(vehicle_types, list):
        errors.append("Vehicle types must be a list")
    elif not vehicle_types:
        errors.append("At least one vehicle type must be specified")
    elif len(vehicle_types) > 10:
        warnings.append("Many vehicle types selected - this may slow down optimization")
        suggestions.append("Consider focusing on key vehicle categories")
    
    # Check if vehicle types are valid (basic check)
    valid_categories = [
        "Passenger Cars", "Buses", "Heavy Goods Vehicles (HGVs)", 
        "Vans / Light Goods Vehicles (LGVs)", "Motorcycles"
    ]
    for vt in vehicle_types:
        if vt not in valid_categories:
            warnings.append(f"Unknown vehicle type: {vt}")
    
    # Emissions factors validation
    emissions_factors = parameters.get('emissions_factors', {})
    if emissions_factors:
        if not isinstance(emissions_factors, dict):
            errors.append("Emissions factors must be a dictionary")
        else:
            for category, vehicles in emissions_factors.items():
                if not isinstance(vehicles, dict):
                    warnings.append(f"Invalid emissions data for {category}")
                    continue
                
                for vehicle, emissions in vehicles.items():
                    if not isinstance(emissions, dict):
                        warnings.append(f"Invalid emissions data for {vehicle}")
                        continue
                    
                    if 'lifecycle' not in emissions or 'tailpipe' not in emissions:
                        warnings.append(f"Missing emissions data for {vehicle}")
                    else:
                        lifecycle = emissions.get('lifecycle', 0)
                        tailpipe = emissions.get('tailpipe', 0)
                        
                        if not isinstance(lifecycle, (int, float)) or not isinstance(tailpipe, (int, float)):
                            warnings.append(f"Invalid emissions values for {vehicle}")
                        elif lifecycle < tailpipe:
                            warnings.append(f"Lifecycle emissions should be >= tailpipe for {vehicle}")
                        elif lifecycle > 2.0:
                            warnings.append(f"Very high lifecycle emissions for {vehicle}: {lifecycle}")
    
    # Usage patterns validation
    usage_patterns = parameters.get('usage_patterns', {})
    if usage_patterns:
        if not isinstance(usage_patterns, dict):
            warnings.append("Usage patterns must be a dictionary")
        else:
            for category, vehicles in usage_patterns.items():
                if not isinstance(vehicles, dict):
                    warnings.append(f"Invalid usage data for {category}")
                    continue
                
                for vehicle, usage in vehicles.items():
                    if not isinstance(usage, (int, float)):
                        warnings.append(f"Invalid usage value for {vehicle}")
                    elif usage < 0:
                        warnings.append(f"Negative usage value for {vehicle}")
                    elif usage > 100000:
                        warnings.append(f"Very high usage value for {vehicle}: {usage}")
    
    # Advanced constraints validation
    enable_constraints = parameters.get('enable_constraints', True)
    if not isinstance(enable_constraints, bool):
        warnings.append("Enable constraints should be a boolean value")
    
    # Generate suggestions based on analysis
    if not warnings and not errors:
        suggestions.append("Scenario parameters look good!")
    
    if target > 0.5 and max_change < 0.15:
        suggestions.append("Consider increasing max annual change to meet high reduction target")
    
    if len(years) > 5 and max_change > 0.15:
        suggestions.append("High change rate over many years - consider intermediate targets")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions
    }

def create_scenario(db: Session, scenario: ScenarioCreate) -> Scenario:
    """Create a new scenario with validation"""
    # Validate parameters
    validation = validate_scenario_parameters(scenario.parameters)
    if not validation["valid"]:
        raise ValueError(f"Invalid scenario parameters: {validation['errors']}")
    
    db_scenario = Scenario(
        name=scenario.name,
        description=scenario.description,
        parameters=scenario.parameters
    )
    
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

def get_scenario(db: Session, scenario_id: int) -> Optional[Scenario]:
    """Get a scenario by ID"""
    return db.query(Scenario).filter(Scenario.id == scenario_id).first()

def get_scenarios(db: Session, skip: int = 0, limit: int = 100) -> List[Scenario]:
    """Get all scenarios with pagination"""
    return db.query(Scenario).offset(skip).limit(limit).all()

def update_scenario(db: Session, scenario_id: int, scenario: ScenarioUpdate) -> Optional[Scenario]:
    """Update a scenario with validation"""
    db_scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not db_scenario:
        return None
    
    update_data = scenario.dict(exclude_unset=True)
    
    # Validate parameters if provided
    if 'parameters' in update_data:
        validation = validate_scenario_parameters(update_data['parameters'])
        if not validation["valid"]:
            raise ValueError(f"Invalid scenario parameters: {validation['errors']}")
    
    for field, value in update_data.items():
        setattr(db_scenario, field, value)
    
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

def delete_scenario(db: Session, scenario_id: int) -> bool:
    """Delete a scenario"""
    db_scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not db_scenario:
        return False
    
    db.delete(db_scenario)
    db.commit()
    return True

def get_scenario_summary(db: Session, scenario_id: int) -> Dict[str, Any]:
    """Get enhanced summary information for a scenario"""
    scenario = get_scenario(db, scenario_id)
    if not scenario:
        return {}
    
    params = scenario.parameters
    vehicle_types = params.get('vehicle_types', [])
    
    # Calculate summary metrics
    summary = {
        "id": scenario.id,
        "name": scenario.name,
        "description": scenario.description,
        "created_at": scenario.created_at,
        "updated_at": scenario.updated_at,
        "parameters": {
            "target_reduction_percent": params.get('target_emissions_reduction', 0) * 100,
            "max_annual_change_percent": params.get('max_annual_change', 0) * 100,
            "analysis_years": len(params.get('years', [])),
            "vehicle_categories": vehicle_types,
            "total_vehicle_types": sum(len(params.get('emissions_factors', {}).get(vt, {})) for vt in vehicle_types),
            "emissions_type": params.get('emissions_type', 'Lifecycle (recommended)'),
            "include_usage_patterns": params.get('usage_patterns') is not None,
            "enable_constraints": params.get('enable_constraints', True)
        },
        "validation": validate_scenario_parameters(params)
    }
    
    return summary

def search_scenarios(db: Session, search_term: str = None, 
                    vehicle_types: List[str] = None, 
                    min_reduction: float = None,
                    max_reduction: float = None) -> List[Scenario]:
    """Search scenarios with filters"""
    query = db.query(Scenario)
    
    if search_term:
        query = query.filter(
            (Scenario.name.contains(search_term)) | 
            (Scenario.description.contains(search_term))
        )
    
    if vehicle_types:
        # This is a simplified search - in production you'd want more sophisticated filtering
        for vt in vehicle_types:
            query = query.filter(Scenario.parameters.contains({"vehicle_types": [vt]}))
    
    if min_reduction is not None:
        query = query.filter(Scenario.parameters.contains({"target_emissions_reduction": {"$gte": min_reduction}}))
    
    if max_reduction is not None:
        query = query.filter(Scenario.parameters.contains({"target_emissions_reduction": {"$lte": max_reduction}}))
    
    return query.all() 