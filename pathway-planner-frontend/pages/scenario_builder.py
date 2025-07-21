import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, List, Any

API_BASE = "http://localhost:8000/api/v1"

# Enhanced vehicle types with more granular subtypes and DEFRA emissions factors
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

def validate_scenario_parameters(name: str, description: str, vehicle_types: List[str], 
                               target_reduction: float, max_change: float, years: List[int],
                               emissions_type: str = "Lifecycle (recommended)",
                               include_usage_patterns: bool = True,
                               enable_constraints: bool = True) -> Dict[str, Any]:
    """Comprehensive parameter validation with detailed feedback"""
    errors = []
    warnings = []
    suggestions = []
    
    # Name validation
    if not name or len(name.strip()) == 0:
        errors.append("Scenario name is required")
    elif len(name) < 3:
        errors.append("Scenario name must be at least 3 characters long")
    elif len(name) > 100:
        errors.append("Scenario name must be less than 100 characters")
    elif not name.replace(" ", "").replace("-", "").replace("_", "").isalnum():
        warnings.append("Scenario name contains special characters - consider using alphanumeric characters only")
    
    # Description validation
    if description:
        if len(description) > 500:
            warnings.append("Description is quite long - consider keeping it under 500 characters")
        if len(description) < 10:
            suggestions.append("Consider adding more detail to your scenario description")
    
    # Vehicle types validation
    if not vehicle_types:
        errors.append("At least one vehicle type must be selected")
    elif len(vehicle_types) > 15:
        warnings.append("Many vehicle types selected - this may slow down optimization")
        suggestions.append("Consider focusing on key vehicle categories for faster analysis")
    
    # Validate specific vehicle types
    valid_categories = list(VEHICLE_EMISSIONS.keys())
    for vt in vehicle_types:
        if vt not in valid_categories:
            errors.append(f"Invalid vehicle type: {vt}")
        elif vt == "Specialist Vehicles" and len(vehicle_types) == 1:
            warnings.append("Specialist vehicles alone may not provide comprehensive transport analysis")
            suggestions.append("Consider including passenger cars, buses, or HGVs for broader coverage")
    
    # Target reduction validation
    if target_reduction < 0 or target_reduction > 1:
        errors.append("Target reduction must be between 0% and 100%")
    elif target_reduction > 0.9:
        warnings.append("Very high reduction target (>90%) - ensure this is realistic")
        suggestions.append("Consider breaking down into intermediate targets (2030, 2040, 2050)")
    elif target_reduction > 0.8:
        warnings.append("High reduction target (>80%) - ensure this is achievable")
    elif target_reduction < 0.1:
        warnings.append("Low reduction target (<10%) - may not achieve significant decarbonization")
        suggestions.append("Consider more ambitious targets for meaningful impact")
    
    # Max change validation
    if max_change < 0.05 or max_change > 0.3:
        errors.append("Maximum annual change must be between 5% and 30%")
    elif max_change > 0.25:
        warnings.append("Very high annual change rate (>25%) - may be challenging to achieve")
        suggestions.append("Consider a more gradual transition for realistic implementation")
    elif max_change > 0.2:
        warnings.append("High annual change rate (>20%) - ensure infrastructure can support this pace")
    elif max_change < 0.08:
        warnings.append("Low annual change rate (<8%) - may not meet targets")
        suggestions.append("Consider increasing the change rate or extending the timeline")
    
    # Years validation
    if len(years) < 2:
        errors.append("At least 2 years must be selected")
    elif len(years) > 12:
        warnings.append("Many years selected (>12) - this may increase computation time")
        suggestions.append("Consider using 5-year intervals for long-term analysis")
    
    # Check for realistic year progression
    years_sorted = sorted(years)
    if years_sorted != years:
        errors.append("Years must be in ascending order")
    
    for i in range(len(years_sorted) - 1):
        gap = years_sorted[i+1] - years_sorted[i]
        if gap < 1:
            errors.append("Years must have at least 1 year gap")
        elif gap > 15:
            warnings.append(f"Large gap between {years_sorted[i]} and {years_sorted[i+1]} - consider intermediate years")
        elif gap > 10:
            suggestions.append(f"Consider adding intermediate years between {years_sorted[i]} and {years_sorted[i+1]}")
    
    # Check for reasonable year range
    if years_sorted[0] < 2020:
        warnings.append("Starting year before 2020 may not reflect current technology")
    if years_sorted[-1] > 2060:
        warnings.append("End year after 2060 may have high uncertainty")
    
    # Emissions type validation
    if emissions_type not in ["Lifecycle (recommended)", "Tailpipe only"]:
        warnings.append("Unusual emissions calculation type selected")
    
    # Advanced options validation
    if not include_usage_patterns:
        warnings.append("Usage patterns disabled - analysis may be less accurate")
        suggestions.append("Enable usage patterns for more realistic calculations")
    
    if not enable_constraints:
        warnings.append("Constraints disabled - results may not be realistic")
        suggestions.append("Enable constraints for more realistic technology adoption")
    
    # Cross-validation checks
    if target_reduction > 0.5 and max_change < 0.15:
        suggestions.append("Consider increasing max annual change to meet high reduction target")
    
    if len(years_sorted) > 5 and max_change > 0.15:
        suggestions.append("High change rate over many years - consider intermediate targets")
    
    if "Passenger Cars" in vehicle_types and target_reduction > 0.7:
        suggestions.append("High reduction target for passenger cars - consider infrastructure requirements")
    
    if "Heavy Goods Vehicles (HGVs)" in vehicle_types and target_reduction > 0.6:
        suggestions.append("High reduction target for HGVs - consider technology readiness")
    
    # Generate positive feedback
    if not warnings and not errors:
        suggestions.append("Scenario parameters look excellent!")
    
    if len(vehicle_types) >= 3 and len(vehicle_types) <= 8:
        suggestions.append("Good vehicle type selection - provides comprehensive coverage")
    
    if 0.3 <= target_reduction <= 0.7:
        suggestions.append("Realistic reduction target - good balance of ambition and achievability")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions
    }

def list_scenarios():
    try:
        response = requests.get(f"{API_BASE}/scenarios/")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching scenarios: {e}")
    return []

def create_scenario(data):
    try:
        response = requests.post(f"{API_BASE}/scenarios/", json=data)
        if response.status_code == 201:
            return response.json()
    except Exception as e:
        st.error(f"Error creating scenario: {e}")
    return None

def delete_scenario(scenario_id):
    try:
        response = requests.delete(f"{API_BASE}/scenarios/{scenario_id}")
        return response.status_code == 204
    except Exception as e:
        st.error(f"Error deleting scenario: {e}")
        return False

def show():
    st.title("Scenario Builder")
    st.markdown("Create and manage decarbonization scenarios for Teesside transport")
    
    # Enhanced demo scenarios with more vehicle types
    if st.button("Load Enhanced Demo Scenarios"):
        demo_scenarios = [
            {
                "name": "Conservative Pathway",
                "description": "Gradual transition focusing on passenger vehicles and public transport",
                "parameters": {
                    "years": [2025, 2030, 2035, 2040, 2045, 2050],
                    "target_emissions_reduction": 0.3,
                    "max_annual_change": 0.05,
                    "vehicle_types": ["Passenger Cars", "Buses"],
                    "emissions_factors": VEHICLE_EMISSIONS,
                    "usage_patterns": VEHICLE_USAGE
                }
            },
            {
                "name": "Accelerated Transition",
                "description": "Faster adoption of electric and hydrogen technologies across all vehicle types",
                "parameters": {
                    "years": [2025, 2030, 2035, 2040, 2045, 2050],
                    "target_emissions_reduction": 0.6,
                    "max_annual_change": 0.15,
                    "vehicle_types": ["Passenger Cars", "Buses", "Vans / Light Goods Vehicles (LGVs)", "Motorcycles"],
                    "emissions_factors": VEHICLE_EMISSIONS,
                    "usage_patterns": VEHICLE_USAGE
                }
            },
            {
                "name": "Net Zero by 2040",
                "description": "Aggressive pathway to achieve net zero transport emissions by 2040",
                "parameters": {
                    "years": [2025, 2030, 2035, 2040],
                    "target_emissions_reduction": 1.0,
                    "max_annual_change": 0.25,
                    "vehicle_types": ["Passenger Cars", "Buses", "Heavy Goods Vehicles (HGVs)", "Vans / Light Goods Vehicles (LGVs)", "Motorcycles"],
                    "emissions_factors": VEHICLE_EMISSIONS,
                    "usage_patterns": VEHICLE_USAGE
                }
            }
        ]
        
        with st.spinner("Creating enhanced demo scenarios..."):
            for scenario in demo_scenarios:
                create_scenario(scenario)
        
        st.success("Enhanced demo scenarios loaded! Refresh to see them.")
        st.experimental_rerun()

    st.divider()
    
    # Create New Scenario with enhanced features
    with st.expander("Create New Scenario", expanded=True):
        with st.form("create_scenario_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Scenario Name", placeholder="e.g., Electric First Pathway", 
                                   help="Enter a descriptive name for your scenario")
                description = st.text_area("Description", placeholder="Describe your scenario, objectives, and key assumptions...",
                                          help="Provide context for your decarbonization pathway")
                
                # Enhanced vehicle type selection with search
                st.subheader("Vehicle Types")
                st.markdown("Select vehicle categories to include in your scenario:")
                
                # Add search functionality
                search_term = st.text_input("Search vehicle types:", placeholder="e.g., electric, large, hybrid")
                
                # Filter vehicle types based on search
                available_categories = list(VEHICLE_EMISSIONS.keys())
                if search_term:
                    available_categories = [cat for cat in available_categories 
                                          if search_term.lower() in cat.lower()]
                
                selected_vehicle_categories = st.multiselect(
                    "Select vehicle categories:",
                    available_categories,
                    default=["Passenger Cars", "Buses"],
                    help="Choose which vehicle types to include in your analysis"
                )
            
            with col2:
                st.subheader("Target Parameters")
                target_reduction = st.slider("Target Emissions Reduction (%)", 0, 100, 50, 5,
                                           help="Percentage reduction in emissions by the final year")
                max_change = st.slider("Max Annual Change (%)", 5, 30, 10, 5,
                                     help="Maximum percentage change in technology adoption per year")
                
                st.subheader("Timeline")
                years = st.multiselect(
                    "Target Years",
                    [2025, 2030, 2035, 2040, 2045, 2050],
                    default=[2025, 2030, 2040, 2050],
                    help="Select years for analysis (minimum 2, maximum 10)"
                )
                
                # Emissions calculation type
                st.subheader("Emissions Calculation")
                emissions_type = st.radio(
                    "Use emissions factors:",
                    ["Lifecycle (recommended)", "Tailpipe only"],
                    help="Lifecycle includes vehicle manufacture, fuel production, and disposal"
                )
                
                # Advanced options
                st.subheader("Advanced Options")
                include_usage_patterns = st.checkbox("Include usage patterns", value=True,
                                                   help="Use realistic annual mileage for each vehicle type")
                enable_constraints = st.checkbox("Enable advanced constraints", value=True,
                                               help="Apply realistic technology adoption constraints")
            
            # Show selected vehicle types and their emissions with enhanced display
            if selected_vehicle_categories:
                st.subheader("Selected Vehicle Types & Emissions")
                
                # Create tabs for better organization
                tab1, tab2, tab3 = st.tabs(["Emissions Data", "Usage Patterns", "Summary"])
                
                with tab1:
                    for category in selected_vehicle_categories:
                        st.markdown(f"**{category}**")
                        category_vehicles = VEHICLE_EMISSIONS[category]
                        
                        # Create a table for this category
                        vehicle_data = []
                        for vehicle, emissions in category_vehicles.items():
                            if emissions_type == "Lifecycle (recommended)":
                                emission_value = emissions["lifecycle"]
                            else:
                                emission_value = emissions["tailpipe"]
                            
                            usage = VEHICLE_USAGE[category].get(vehicle, 0)
                            
                            vehicle_data.append({
                                "Vehicle Type": vehicle,
                                f"Emissions (kg CO₂e/km)": f"{emission_value:.3f}",
                                "Annual Usage (miles)": f"{usage:,}" if include_usage_patterns else "N/A"
                            })
                        
                        # Display as a table
                        df = pd.DataFrame(vehicle_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                
                with tab2:
                    if include_usage_patterns:
                        usage_data = []
                        for category in selected_vehicle_categories:
                            for vehicle, usage in VEHICLE_USAGE[category].items():
                                usage_data.append({
                                    "Category": category,
                                    "Vehicle Type": vehicle,
                                    "Annual Miles": usage,
                                    "Emissions Factor": VEHICLE_EMISSIONS[category][vehicle]["lifecycle"]
                                })
                        
                        df_usage = pd.DataFrame(usage_data)
                        st.dataframe(df_usage, use_container_width=True, hide_index=True)
                    else:
                        st.info("Usage patterns not enabled for this scenario")
                
                with tab3:
                    total_vehicles = sum(len(VEHICLE_EMISSIONS[cat]) for cat in selected_vehicle_categories)
                    st.metric("Total Vehicle Types", total_vehicles)
                    st.metric("Target Reduction", f"{target_reduction}%")
                    st.metric("Max Annual Change", f"{max_change}%")
                    st.metric("Analysis Years", len(years))
            
            # Enhanced validation and feedback
            submitted = st.form_submit_button("Create Scenario")
            if submitted:
                # Validate parameters
                validation = validate_scenario_parameters(
                    name, description, selected_vehicle_categories, 
                    target_reduction/100, max_change/100, years
                )
                
                if validation["errors"]:
                    st.error("Please fix the following errors:")
                    for error in validation["errors"]:
                        st.error(f"• {error}")
                
                if validation["warnings"]:
                    st.warning("Please review the following warnings:")
                    for warning in validation["warnings"]:
                        st.warning(f"• {warning}")
                
                if validation["valid"] and name and selected_vehicle_categories:
                    # Prepare emissions factors for selected vehicles
                    selected_emissions = {}
                    selected_usage = {}
                    
                    for category in selected_vehicle_categories:
                        selected_emissions[category] = VEHICLE_EMISSIONS[category]
                        if include_usage_patterns:
                            selected_usage[category] = VEHICLE_USAGE[category]
                    
                    parameters = {
                        "years": sorted(years),
                        "target_emissions_reduction": target_reduction / 100,
                        "max_annual_change": max_change / 100,
                        "vehicle_types": selected_vehicle_categories,
                        "emissions_factors": selected_emissions,
                        "emissions_type": emissions_type,
                        "usage_patterns": selected_usage if include_usage_patterns else None,
                        "enable_constraints": enable_constraints
                    }
                    
                    data = {
                        "name": name,
                        "description": description,
                        "parameters": parameters
                    }
                    
                    with st.spinner("Creating scenario..."):
                        result = create_scenario(data)
                        if result:
                            st.success(f"Scenario '{name}' created successfully!")
                            st.balloons()
                            st.experimental_rerun()
                        else:
                            st.error("Failed to create scenario. Check your connection to the backend.")

    st.divider()
    
    # Enhanced scenario management
    st.subheader("Your Scenarios")
    
    scenarios = list_scenarios()
    if scenarios:
        # Add filtering and sorting options
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_scenarios = st.text_input("Search scenarios:", placeholder="Search by name or description")
        
        with col2:
            sort_by = st.selectbox("Sort by:", ["Name", "Created Date", "Vehicle Count", "Target Reduction"])
        
        # Filter scenarios
        filtered_scenarios = scenarios
        if search_scenarios:
            filtered_scenarios = [s for s in scenarios 
                                if search_scenarios.lower() in s.get('name', '').lower() 
                                or search_scenarios.lower() in s.get('description', '').lower()]
        
        # Sort scenarios
        if sort_by == "Name":
            filtered_scenarios.sort(key=lambda x: x.get('name', ''))
        elif sort_by == "Vehicle Count":
            filtered_scenarios.sort(key=lambda x: len(x.get('parameters', {}).get('vehicle_types', [])), reverse=True)
        elif sort_by == "Target Reduction":
            filtered_scenarios.sort(key=lambda x: x.get('parameters', {}).get('target_emissions_reduction', 0), reverse=True)
        
        # Display scenarios with enhanced information
        for i, scenario in enumerate(filtered_scenarios):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{scenario['name']}**")
                    st.caption(scenario.get('description', 'No description'))
                    
                    if scenario.get('parameters'):
                        params = scenario['parameters']
                        vehicle_count = len(params.get('vehicle_types', []))
                        target = params.get('target_emissions_reduction', 0) * 100
                        years_count = len(params.get('years', []))
                        
                        # Enhanced metrics display
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        with metrics_col1:
                            st.metric("Target", f"{target:.0f}%")
                        with metrics_col2:
                            st.metric("Vehicles", vehicle_count)
                        with metrics_col3:
                            st.metric("Years", years_count)
                
                with col2:
                    if st.button(f"View", key=f"view_{i}"):
                        st.session_state["selected_scenario_id"] = scenario["id"]
                        st.success(f"Selected: {scenario['name']}")
                
                with col3:
                    if st.button(f"Edit", key=f"edit_{i}"):
                        st.info("Edit functionality coming in Week 2")
                
                with col4:
                    if st.button(f"Delete", key=f"delete_{i}"):
                        if delete_scenario(scenario["id"]):
                            st.success("Scenario deleted!")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to delete scenario")
                
                st.divider()
    else:
        st.info("No scenarios found. Create your first scenario above or load enhanced demo scenarios.")
    
    # Quick navigation with enhanced options
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Go to Visualization", use_container_width=True):
            st.switch_page("pages/visualize_pathways.py")
    with col2:
        if st.button("Go to Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py")
    with col3:
        if st.button("Parameter Editor", use_container_width=True):
            st.switch_page("pages/parameter_editor.py") 