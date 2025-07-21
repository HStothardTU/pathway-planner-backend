import streamlit as st

def show():
    # Main header with gradient design
    st.markdown('<div class="main-header"><h1>Parameter Editor</h1><h3>Edit parameters for vehicles, technology, and constraints</h3></div>', unsafe_allow_html=True)
    
    # Vehicle Parameters
    st.subheader("Vehicle Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Passenger Cars**")
        petrol_emissions = st.number_input("Petrol Car Emissions (kg CO₂e/km)", value=0.210, format="%.3f")
        diesel_emissions = st.number_input("Diesel Car Emissions (kg CO₂e/km)", value=0.200, format="%.3f")
        electric_emissions = st.number_input("Electric Car Emissions (kg CO₂e/km)", value=0.065, format="%.3f")
        hydrogen_emissions = st.number_input("Hydrogen Car Emissions (kg CO₂e/km)", value=0.040, format="%.3f")
    
    with col2:
        st.markdown("**Buses**")
        bus_diesel_emissions = st.number_input("Diesel Bus Emissions (kg CO₂e/km)", value=1.000, format="%.3f")
        bus_electric_emissions = st.number_input("Electric Bus Emissions (kg CO₂e/km)", value=0.250, format="%.3f")
        bus_hydrogen_emissions = st.number_input("Hydrogen Bus Emissions (kg CO₂e/km)", value=0.200, format="%.3f")
    
    st.divider()
    
    # Technology Parameters
    st.subheader("Technology Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Cost Parameters (£/km)**")
        petrol_cost = st.number_input("Petrol Cost", value=0.12, format="%.2f")
        diesel_cost = st.number_input("Diesel Cost", value=0.10, format="%.2f")
        electric_cost = st.number_input("Electric Cost", value=0.08, format="%.2f")
        hydrogen_cost = st.number_input("Hydrogen Cost", value=0.15, format="%.2f")
    
    with col2:
        st.markdown("**Infrastructure Constraints**")
        max_electric_charging = st.number_input("Max Electric Charging Capacity (%)", value=80, min_value=0, max_value=100)
        max_hydrogen_stations = st.number_input("Max Hydrogen Stations", value=50, min_value=0)
        grid_capacity = st.number_input("Grid Capacity (MW)", value=1000, min_value=0)
    
    st.divider()
    
    # Policy Constraints
    st.subheader("Policy Constraints")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Timeline Constraints**")
        ban_petrol_year = st.number_input("Petrol/Diesel Ban Year", value=2040, min_value=2025, max_value=2050)
        net_zero_year = st.number_input("Net Zero Target Year", value=2050, min_value=2025, max_value=2050)
        max_annual_change = st.slider("Max Annual Technology Change (%)", 5, 30, 15)
    
    with col2:
        st.markdown("**Budget Constraints**")
        annual_budget = st.number_input("Annual Budget (£M)", value=100, min_value=0)
        infrastructure_budget = st.number_input("Infrastructure Budget (£M)", value=500, min_value=0)
        vehicle_subsidies = st.number_input("Vehicle Subsidies (£M)", value=50, min_value=0)
    
    st.divider()
    
    # Save Parameters
    if st.button("Save Parameters", type="primary"):
        # Here you would save the parameters to the backend
        st.success("Parameters saved successfully!")
        
        # Store in session state for demo
        st.session_state["vehicle_parameters"] = {
            "passenger_cars": {
                "petrol": petrol_emissions,
                "diesel": diesel_emissions,
                "electric": electric_emissions,
                "hydrogen": hydrogen_emissions
            },
            "buses": {
                "diesel": bus_diesel_emissions,
                "electric": bus_electric_emissions,
                "hydrogen": bus_hydrogen_emissions
            },
            "costs": {
                "petrol": petrol_cost,
                "diesel": diesel_cost,
                "electric": electric_cost,
                "hydrogen": hydrogen_cost
            },
            "constraints": {
                "ban_petrol_year": ban_petrol_year,
                "net_zero_year": net_zero_year,
                "max_annual_change": max_annual_change,
                "annual_budget": annual_budget
            }
        }
    
    # Show current parameters
    if "vehicle_parameters" in st.session_state:
        with st.expander("Current Parameters"):
            st.json(st.session_state["vehicle_parameters"])
    
    # Quick navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Scenario Builder", use_container_width=True):
            st.switch_page("pages/scenario_builder.py")
    with col2:
        if st.button("Go to Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py") 