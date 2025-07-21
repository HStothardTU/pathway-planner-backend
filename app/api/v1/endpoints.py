from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time
import json

from app.db.session import get_db
from app.db.models import Scenario
from app.services.optimizer import optimize_transport_pathway
from app.services.scenario import validate_scenario_parameters
from . import schemas

router = APIRouter()

# Enhanced vehicle types data with granular subtypes and DEFRA emissions factors
VEHICLE_EMISSIONS = {
    "Passenger Cars": {
        # Petrol Cars - by engine size and efficiency
        "Petrol Car (Mini)": {"tailpipe": 0.120, "lifecycle": 0.150},
        "Petrol Car (Small)": {"tailpipe": 0.150, "lifecycle": 0.180},
        "Petrol Car (Medium)": {"tailpipe": 0.180, "lifecycle": 0.210},
        "Petrol Car (Large)": {"tailpipe": 0.220, "lifecycle": 0.250},
        "Petrol Car (Luxury)": {"tailpipe": 0.280, "lifecycle": 0.310},
        "Petrol Car (Sports)": {"tailpipe": 0.320, "lifecycle": 0.350},
        
        # Diesel Cars - by engine size and efficiency
        "Diesel Car (Mini)": {"tailpipe": 0.110, "lifecycle": 0.140},
        "Diesel Car (Small)": {"tailpipe": 0.140, "lifecycle": 0.170},
        "Diesel Car (Medium)": {"tailpipe": 0.170, "lifecycle": 0.200},
        "Diesel Car (Large)": {"tailpipe": 0.200, "lifecycle": 0.230},
        "Diesel Car (Luxury)": {"tailpipe": 0.250, "lifecycle": 0.280},
        
        # Hybrid Cars - by type and efficiency
        "Hybrid Car (Mild Petrol)": {"tailpipe": 0.140, "lifecycle": 0.180},
        "Hybrid Car (Full Petrol)": {"tailpipe": 0.130, "lifecycle": 0.170},
        "Hybrid Car (Mild Diesel)": {"tailpipe": 0.130, "lifecycle": 0.170},
        "Hybrid Car (Full Diesel)": {"tailpipe": 0.120, "lifecycle": 0.160},
        "Plug-in Hybrid (PHEV)": {"tailpipe": 0.070, "lifecycle": 0.135},
        
        # Electric Cars - by battery size and efficiency
        "Battery Electric Car (Mini)": {"tailpipe": 0.000, "lifecycle": 0.055},
        "Battery Electric Car (Small)": {"tailpipe": 0.000, "lifecycle": 0.060},
        "Battery Electric Car (Medium)": {"tailpipe": 0.000, "lifecycle": 0.065},
        "Battery Electric Car (Large)": {"tailpipe": 0.000, "lifecycle": 0.070},
        "Battery Electric Car (Luxury)": {"tailpipe": 0.000, "lifecycle": 0.075},
        
        # Hydrogen Cars
        "Hydrogen Car (FCEV)": {"tailpipe": 0.000, "lifecycle": 0.040},
        "Hydrogen Car (ICE)": {"tailpipe": 0.080, "lifecycle": 0.120}
    },
    "Buses": {
        # Diesel Buses - by size and usage
        "Diesel Bus (Mini)": {"tailpipe": 0.750, "lifecycle": 0.850},
        "Diesel Bus (Single Deck)": {"tailpipe": 0.850, "lifecycle": 0.950},
        "Diesel Bus (Double Deck)": {"tailpipe": 0.950, "lifecycle": 1.050},
        "Diesel Bus (Articulated)": {"tailpipe": 1.100, "lifecycle": 1.200},
        "Diesel Bus (Coach)": {"tailpipe": 1.050, "lifecycle": 1.150},
        
        # Hybrid Buses
        "Hybrid Diesel Bus (Single Deck)": {"tailpipe": 0.650, "lifecycle": 0.750},
        "Hybrid Diesel Bus (Double Deck)": {"tailpipe": 0.750, "lifecycle": 0.850},
        
        # Electric Buses
        "Battery Electric Bus (Mini)": {"tailpipe": 0.000, "lifecycle": 0.220},
        "Battery Electric Bus (Single Deck)": {"tailpipe": 0.000, "lifecycle": 0.250},
        "Battery Electric Bus (Double Deck)": {"tailpipe": 0.000, "lifecycle": 0.280},
        "Battery Electric Bus (Articulated)": {"tailpipe": 0.000, "lifecycle": 0.320},
        
        # Hydrogen Buses
        "Hydrogen Bus (FCEV)": {"tailpipe": 0.000, "lifecycle": 0.200},
        "Hydrogen Bus (ICE)": {"tailpipe": 0.400, "lifecycle": 0.500}
    },
    "Heavy Goods Vehicles (HGVs)": {
        # Diesel HGVs - by weight class and type
        "Diesel Rigid HGV (3.5-7.5t)": {"tailpipe": 0.750, "lifecycle": 0.850},
        "Diesel Rigid HGV (7.5-17t)": {"tailpipe": 0.850, "lifecycle": 0.950},
        "Diesel Rigid HGV (17-26t)": {"tailpipe": 0.950, "lifecycle": 1.050},
        "Diesel Rigid HGV (26-32t)": {"tailpipe": 1.050, "lifecycle": 1.150},
        "Diesel Articulated HGV (26-33t)": {"tailpipe": 1.050, "lifecycle": 1.150},
        "Diesel Articulated HGV (33-44t)": {"tailpipe": 1.150, "lifecycle": 1.250},
        "Diesel Articulated HGV (>44t)": {"tailpipe": 1.250, "lifecycle": 1.350},
        
        # Electric HGVs
        "Battery Electric HGV (Rigid 7.5-17t)": {"tailpipe": 0.000, "lifecycle": 0.280},
        "Battery Electric HGV (Rigid 17-26t)": {"tailpipe": 0.000, "lifecycle": 0.300},
        "Battery Electric HGV (Articulated 26-33t)": {"tailpipe": 0.000, "lifecycle": 0.350},
        "Battery Electric HGV (Articulated 33-44t)": {"tailpipe": 0.000, "lifecycle": 0.400},
        
        # Hydrogen HGVs
        "Hydrogen HGV (FCEV Rigid)": {"tailpipe": 0.000, "lifecycle": 0.275},
        "Hydrogen HGV (FCEV Articulated)": {"tailpipe": 0.000, "lifecycle": 0.325}
    },
    "Vans / Light Goods Vehicles (LGVs)": {
        # Diesel Vans - by size and payload
        "Diesel Van (Mini)": {"tailpipe": 0.180, "lifecycle": 0.230},
        "Diesel Van (Small)": {"tailpipe": 0.220, "lifecycle": 0.270},
        "Diesel Van (Medium)": {"tailpipe": 0.250, "lifecycle": 0.300},
        "Diesel Van (Large)": {"tailpipe": 0.280, "lifecycle": 0.330},
        "Diesel Van (Extra Large)": {"tailpipe": 0.320, "lifecycle": 0.370},
        
        # Electric Vans
        "Electric Van (Mini)": {"tailpipe": 0.000, "lifecycle": 0.100},
        "Electric Van (Small)": {"tailpipe": 0.000, "lifecycle": 0.110},
        "Electric Van (Medium)": {"tailpipe": 0.000, "lifecycle": 0.120},
        "Electric Van (Large)": {"tailpipe": 0.000, "lifecycle": 0.130},
        "Electric Van (Extra Large)": {"tailpipe": 0.000, "lifecycle": 0.140},
        
        # Hydrogen Vans
        "Hydrogen Van (FCEV)": {"tailpipe": 0.000, "lifecycle": 0.140},
        "Hydrogen Van (ICE)": {"tailpipe": 0.120, "lifecycle": 0.180}
    },
    "Motorcycles": {
        # Petrol Motorcycles - by engine size
        "Petrol Motorcycle (50cc)": {"tailpipe": 0.060, "lifecycle": 0.080},
        "Petrol Motorcycle (125cc)": {"tailpipe": 0.080, "lifecycle": 0.100},
        "Petrol Motorcycle (250cc)": {"tailpipe": 0.100, "lifecycle": 0.120},
        "Petrol Motorcycle (500cc)": {"tailpipe": 0.120, "lifecycle": 0.140},
        "Petrol Motorcycle (750cc)": {"tailpipe": 0.140, "lifecycle": 0.160},
        "Petrol Motorcycle (1000cc+)": {"tailpipe": 0.160, "lifecycle": 0.180},
        
        # Electric Motorcycles
        "Electric Motorcycle (Small)": {"tailpipe": 0.000, "lifecycle": 0.025},
        "Electric Motorcycle (Medium)": {"tailpipe": 0.000, "lifecycle": 0.030},
        "Electric Motorcycle (Large)": {"tailpipe": 0.000, "lifecycle": 0.035},
        "Electric Scooter (50cc equivalent)": {"tailpipe": 0.000, "lifecycle": 0.020},
        "Electric Scooter (125cc equivalent)": {"tailpipe": 0.000, "lifecycle": 0.025}
    },
    "Specialist Vehicles": {
        # Agricultural and Construction
        "Agricultural Tractor (Small)": {"tailpipe": 1.500, "lifecycle": 1.700},
        "Agricultural Tractor (Medium)": {"tailpipe": 2.000, "lifecycle": 2.200},
        "Agricultural Tractor (Large)": {"tailpipe": 2.500, "lifecycle": 2.700},
        "Construction Vehicle (Excavator)": {"tailpipe": 2.200, "lifecycle": 2.400},
        "Construction Vehicle (Bulldozer)": {"tailpipe": 2.800, "lifecycle": 3.000},
        "Construction Vehicle (Crane)": {"tailpipe": 1.800, "lifecycle": 2.000},
        
        # Emergency and Service Vehicles
        "Emergency Vehicle (Ambulance)": {"tailpipe": 0.950, "lifecycle": 1.050},
        "Emergency Vehicle (Fire Engine)": {"tailpipe": 1.100, "lifecycle": 1.200},
        "Emergency Vehicle (Police Car)": {"tailpipe": 0.200, "lifecycle": 0.230},
        "Service Vehicle (Refuse Truck)": {"tailpipe": 1.300, "lifecycle": 1.400},
        "Service Vehicle (Street Sweeper)": {"tailpipe": 0.900, "lifecycle": 1.000},
        
        # Electric Specialist Vehicles
        "Electric Agricultural Tractor": {"tailpipe": 0.000, "lifecycle": 0.400},
        "Electric Construction Vehicle": {"tailpipe": 0.000, "lifecycle": 0.500},
        "Electric Emergency Vehicle": {"tailpipe": 0.000, "lifecycle": 0.250},
        "Electric Service Vehicle": {"tailpipe": 0.000, "lifecycle": 0.300}
    }
}

# Enhanced vehicle usage patterns (miles per year) based on DfT data
VEHICLE_USAGE = {
    "Passenger Cars": {
        # Petrol Cars
        "Petrol Car (Mini)": 6000,
        "Petrol Car (Small)": 8000,
        "Petrol Car (Medium)": 10000,
        "Petrol Car (Large)": 12000,
        "Petrol Car (Luxury)": 15000,
        "Petrol Car (Sports)": 8000,
        
        # Diesel Cars
        "Diesel Car (Mini)": 8000,
        "Diesel Car (Small)": 12000,
        "Diesel Car (Medium)": 15000,
        "Diesel Car (Large)": 18000,
        "Diesel Car (Luxury)": 20000,
        
        # Hybrid Cars
        "Hybrid Car (Mild Petrol)": 8500,
        "Hybrid Car (Full Petrol)": 9000,
        "Hybrid Car (Mild Diesel)": 10500,
        "Hybrid Car (Full Diesel)": 11000,
        "Plug-in Hybrid (PHEV)": 8000,
        
        # Electric Cars
        "Battery Electric Car (Mini)": 5500,
        "Battery Electric Car (Small)": 7000,
        "Battery Electric Car (Medium)": 8000,
        "Battery Electric Car (Large)": 9000,
        "Battery Electric Car (Luxury)": 10000,
        
        # Hydrogen Cars
        "Hydrogen Car (FCEV)": 8000,
        "Hydrogen Car (ICE)": 10000
    },
    "Buses": {
        # Diesel Buses
        "Diesel Bus (Mini)": 20000,
        "Diesel Bus (Single Deck)": 25000,
        "Diesel Bus (Double Deck)": 30000,
        "Diesel Bus (Articulated)": 35000,
        "Diesel Bus (Coach)": 40000,
        
        # Hybrid Buses
        "Hybrid Diesel Bus (Single Deck)": 25000,
        "Hybrid Diesel Bus (Double Deck)": 30000,
        
        # Electric Buses
        "Battery Electric Bus (Mini)": 20000,
        "Battery Electric Bus (Single Deck)": 25000,
        "Battery Electric Bus (Double Deck)": 30000,
        "Battery Electric Bus (Articulated)": 35000,
        
        # Hydrogen Buses
        "Hydrogen Bus (FCEV)": 25000,
        "Hydrogen Bus (ICE)": 25000
    },
    "Heavy Goods Vehicles (HGVs)": {
        # Diesel HGVs
        "Diesel Rigid HGV (3.5-7.5t)": 12000,
        "Diesel Rigid HGV (7.5-17t)": 15000,
        "Diesel Rigid HGV (17-26t)": 20000,
        "Diesel Rigid HGV (26-32t)": 25000,
        "Diesel Articulated HGV (26-33t)": 35000,
        "Diesel Articulated HGV (33-44t)": 40000,
        "Diesel Articulated HGV (>44t)": 45000,
        
        # Electric HGVs
        "Battery Electric HGV (Rigid 7.5-17t)": 15000,
        "Battery Electric HGV (Rigid 17-26t)": 20000,
        "Battery Electric HGV (Articulated 26-33t)": 25000,
        "Battery Electric HGV (Articulated 33-44t)": 30000,
        
        # Hydrogen HGVs
        "Hydrogen HGV (FCEV Rigid)": 20000,
        "Hydrogen HGV (FCEV Articulated)": 25000
    },
    "Vans / Light Goods Vehicles (LGVs)": {
        # Diesel Vans
        "Diesel Van (Mini)": 8000,
        "Diesel Van (Small)": 12000,
        "Diesel Van (Medium)": 15000,
        "Diesel Van (Large)": 18000,
        "Diesel Van (Extra Large)": 22000,
        
        # Electric Vans
        "Electric Van (Mini)": 7000,
        "Electric Van (Small)": 10000,
        "Electric Van (Medium)": 12000,
        "Electric Van (Large)": 15000,
        "Electric Van (Extra Large)": 18000,
        
        # Hydrogen Vans
        "Hydrogen Van (FCEV)": 12000,
        "Hydrogen Van (ICE)": 15000
    },
    "Motorcycles": {
        # Petrol Motorcycles
        "Petrol Motorcycle (50cc)": 2000,
        "Petrol Motorcycle (125cc)": 3000,
        "Petrol Motorcycle (250cc)": 5000,
        "Petrol Motorcycle (500cc)": 8000,
        "Petrol Motorcycle (750cc)": 10000,
        "Petrol Motorcycle (1000cc+)": 12000,
        
        # Electric Motorcycles
        "Electric Motorcycle (Small)": 3500,
        "Electric Motorcycle (Medium)": 4000,
        "Electric Motorcycle (Large)": 5000,
        "Electric Scooter (50cc equivalent)": 2000,
        "Electric Scooter (125cc equivalent)": 2500
    },
    "Specialist Vehicles": {
        # Agricultural and Construction
        "Agricultural Tractor (Small)": 800,
        "Agricultural Tractor (Medium)": 1200,
        "Agricultural Tractor (Large)": 1500,
        "Construction Vehicle (Excavator)": 2000,
        "Construction Vehicle (Bulldozer)": 1800,
        "Construction Vehicle (Crane)": 1500,
        
        # Emergency and Service Vehicles
        "Emergency Vehicle (Ambulance)": 30000,
        "Emergency Vehicle (Fire Engine)": 25000,
        "Emergency Vehicle (Police Car)": 35000,
        "Service Vehicle (Refuse Truck)": 20000,
        "Service Vehicle (Street Sweeper)": 15000,
        
        # Electric Specialist Vehicles
        "Electric Agricultural Tractor": 800,
        "Electric Construction Vehicle": 2000,
        "Electric Emergency Vehicle": 30000,
        "Electric Service Vehicle": 20000
    }
}

@router.get("/health")
def health_check():
    """Enhanced health check with system information"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "features": {
            "enhanced_vehicle_types": True,
            "validation": True,
            "usage_patterns": True,
            "constraints": True
        },
        "vehicle_categories": list(VEHICLE_EMISSIONS.keys()),
        "total_vehicle_types": sum(len(vehicles) for vehicles in VEHICLE_EMISSIONS.values())
    }

@router.get("/vehicle-types")
def get_vehicle_types():
    """Get all available vehicle types and their data"""
    return {
        "emissions_factors": VEHICLE_EMISSIONS,
        "usage_patterns": VEHICLE_USAGE,
        "categories": list(VEHICLE_EMISSIONS.keys()),
        "summary": {
            "total_categories": len(VEHICLE_EMISSIONS),
            "total_vehicle_types": sum(len(vehicles) for vehicles in VEHICLE_EMISSIONS.values()),
            "categories": {
                category: {
                    "vehicle_count": len(vehicles),
                    "avg_emissions": sum(emissions["lifecycle"] for emissions in vehicles.values()) / len(vehicles)
                }
                for category, vehicles in VEHICLE_EMISSIONS.items()
            }
        }
    }

@router.get("/vehicle-types/{category}")
def get_vehicle_types_by_category(category: str):
    """Get vehicle types for a specific category"""
    if category not in VEHICLE_EMISSIONS:
        raise HTTPException(
            status_code=404, 
            detail=f"Vehicle category '{category}' not found. Available categories: {list(VEHICLE_EMISSIONS.keys())}"
        )
    
    return {
        "category": category,
        "vehicle_types": list(VEHICLE_EMISSIONS[category].keys()),
        "emissions_factors": VEHICLE_EMISSIONS[category],
        "usage_patterns": VEHICLE_USAGE.get(category, {}),
        "summary": {
            "vehicle_count": len(VEHICLE_EMISSIONS[category]),
            "avg_emissions": sum(emissions["lifecycle"] for emissions in VEHICLE_EMISSIONS[category].values()) / len(VEHICLE_EMISSIONS[category])
        }
    }

@router.post("/validate-scenario")
def validate_scenario(scenario: schemas.ScenarioCreate):
    """Validate scenario parameters with detailed feedback"""
    try:
        # Use the enhanced validation from schemas
        validation_result = validate_scenario_parameters(scenario.parameters)
        
        return {
            "valid": validation_result["valid"],
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
            "suggestions": validation_result.get("suggestions", [])
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": [],
            "suggestions": []
        }

@router.post("/scenarios/", response_model=schemas.ScenarioRead, status_code=status.HTTP_201_CREATED)
def create_scenario(scenario: schemas.ScenarioCreate, db: Session = Depends(get_db)):
    """Create a new scenario with enhanced validation"""
    try:
        # Additional validation for vehicle types
        vehicle_types = scenario.parameters.get('vehicle_types', [])
        for vehicle_type in vehicle_types:
            if vehicle_type not in VEHICLE_EMISSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid vehicle type: {vehicle_type}. Available types: {list(VEHICLE_EMISSIONS.keys())}"
                )
        
        # Create scenario with enhanced parameters
        db_scenario = Scenario(
            name=scenario.name,
            description=scenario.description,
            parameters=scenario.parameters
        )
        
        db.add(db_scenario)
        db.commit()
        db.refresh(db_scenario)
        
        return db_scenario
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create scenario: {str(e)}")

@router.get("/scenarios/", response_model=List[schemas.ScenarioRead])
def list_scenarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all scenarios with enhanced filtering"""
    scenarios = db.query(Scenario).offset(skip).limit(limit).all()
    return scenarios

@router.get("/scenarios/{scenario_id}", response_model=schemas.ScenarioRead)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get a specific scenario with enhanced information"""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Add enhanced information
    scenario_data = {
        "id": scenario.id,
        "name": scenario.name,
        "description": scenario.description,
        "parameters": scenario.parameters,
        "created_at": scenario.created_at,
        "updated_at": scenario.updated_at
    }
    
    # Add vehicle type summary
    if scenario.parameters and 'vehicle_types' in scenario.parameters:
        vehicle_types = scenario.parameters['vehicle_types']
        total_vehicles = sum(len(VEHICLE_EMISSIONS.get(vt, {})) for vt in vehicle_types)
        scenario_data["vehicle_summary"] = {
            "selected_categories": vehicle_types,
            "total_vehicle_types": total_vehicles,
            "target_reduction": scenario.parameters.get('target_emissions_reduction', 0) * 100,
            "analysis_years": len(scenario.parameters.get('years', []))
        }
    
    return scenario_data

@router.put("/scenarios/{scenario_id}", response_model=schemas.ScenarioRead)
def update_scenario(scenario_id: int, scenario: schemas.ScenarioUpdate, db: Session = Depends(get_db)):
    """Update a scenario with enhanced validation"""
    db_scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if db_scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        update_data = scenario.dict(exclude_unset=True)
        
        # Validate vehicle types if provided
        if 'parameters' in update_data and 'vehicle_types' in update_data['parameters']:
            vehicle_types = update_data['parameters']['vehicle_types']
            for vehicle_type in vehicle_types:
                if vehicle_type not in VEHICLE_EMISSIONS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid vehicle type: {vehicle_type}. Available types: {list(VEHICLE_EMISSIONS.keys())}"
                    )
        
        for field, value in update_data.items():
            setattr(db_scenario, field, value)
        
        db.commit()
        db.refresh(db_scenario)
        return db_scenario
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update scenario: {str(e)}")

@router.delete("/scenarios/{scenario_id}")
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Delete a scenario"""
    db_scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if db_scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        db.delete(db_scenario)
        db.commit()
        return {"message": "Scenario deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete scenario: {str(e)}")

@router.post("/optimize", response_model=schemas.OptimizationResponse)
def optimize_pathway(request: schemas.OptimizationRequest, db: Session = Depends(get_db)):
    """Enhanced optimization with vehicle types and usage patterns"""
    start_time = time.time()
    
    try:
        # Get scenario
        scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Prepare optimization data with enhanced vehicle information
        optimization_data = {
            "years": scenario.parameters.get("years", []),
            "target_emissions_reduction": scenario.parameters.get("target_emissions_reduction", 0),
            "max_annual_change": scenario.parameters.get("max_annual_change", 0.1),
            "vehicle_types": scenario.parameters.get("vehicle_types", []),
            "emissions_factors": scenario.parameters.get("emissions_factors", VEHICLE_EMISSIONS),
            "usage_patterns": scenario.parameters.get("usage_patterns", VEHICLE_USAGE) if request.include_usage_patterns else None,
            "enable_constraints": request.enable_constraints
        }
        
        # Override with custom parameters if provided
        if request.custom_parameters:
            optimization_data.update(request.custom_parameters)
        
        # Run optimization
        results = optimize_transport_pathway(optimization_data)
        
        computation_time = time.time() - start_time
        
        return schemas.OptimizationResponse(
            scenario_id=request.scenario_id,
            success=True,
            results=results,
            computation_time=computation_time
        )
        
    except Exception as e:
        computation_time = time.time() - start_time
        return schemas.OptimizationResponse(
            scenario_id=request.scenario_id,
            success=False,
            error_message=str(e),
            computation_time=computation_time
        )

@router.get("/scenarios/{scenario_id}/export/csv")
def export_scenario_csv(scenario_id: int, db: Session = Depends(get_db)):
    """Export scenario data as CSV with enhanced vehicle information"""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Enhanced CSV export with vehicle details
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Scenario Export", scenario.name])
    writer.writerow([])
    writer.writerow(["Basic Information"])
    writer.writerow(["Name", scenario.name])
    writer.writerow(["Description", scenario.description or ""])
    writer.writerow(["Created", scenario.created_at])
    writer.writerow([])
    
    # Write parameters
    writer.writerow(["Parameters"])
    params = scenario.parameters
    writer.writerow(["Target Reduction", f"{params.get('target_emissions_reduction', 0)*100:.1f}%"])
    writer.writerow(["Max Annual Change", f"{params.get('max_annual_change', 0)*100:.1f}%"])
    writer.writerow(["Years", ", ".join(map(str, params.get('years', [])))])
    writer.writerow([])
    
    # Write vehicle information
    writer.writerow(["Vehicle Types"])
    vehicle_types = params.get('vehicle_types', [])
    for vt in vehicle_types:
        writer.writerow([vt])
        if vt in VEHICLE_EMISSIONS:
            for vehicle, emissions in VEHICLE_EMISSIONS[vt].items():
                writer.writerow(["", vehicle, f"{emissions['lifecycle']:.3f}", "kg CO₂e/km"])
    writer.writerow([])
    
    output.seek(0)
    return {
        "filename": f"scenario_{scenario_id}_{scenario.name.replace(' ', '_')}.csv",
        "content": output.getvalue()
    }

@router.get("/scenarios/{scenario_id}/export/pdf")
def export_scenario_pdf(scenario_id: int, db: Session = Depends(get_db)):
    """Export scenario data as PDF with enhanced formatting"""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Enhanced PDF export (placeholder for now)
    return {
        "message": "PDF export functionality coming in Week 2",
        "scenario_id": scenario_id,
        "scenario_name": scenario.name
    } 