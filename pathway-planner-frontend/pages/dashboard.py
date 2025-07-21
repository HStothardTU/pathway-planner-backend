import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_BASE = "http://localhost:8000"

def get_scenarios():
    try:
        response = requests.get(f"{API_BASE}/api/v1/scenarios/")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def show():
    # Main header with gradient design
    st.markdown('<div class="main-header"><h1>Dashboard</h1><h3>Teesside Transport Decarbonization Tool</h3></div>', unsafe_allow_html=True)
    
    # Key Metrics Row with gradient cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card"><h4>Total Scenarios</h4><h2>5</h2><p style="color: #2E8B57;">+2</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h4>Optimized Pathways</h4><h2>3</h2><p style="color: #4682B4;">+1</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h4>CO₂ Reduction</h4><h2>45%</h2><p style="color: #2E8B57;">+12%</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><h4>Cost Savings</h4><h2>£2.3M</h2><p style="color: #4682B4;">+£0.5M</p></div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Recent Activity and Quick Actions
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Recent Scenarios")
        scenarios = get_scenarios()
        
        if scenarios:
            # Create a simple table of recent scenarios
            scenario_data = []
            for scenario in scenarios[-5:]:  # Show last 5
                scenario_data.append({
                    "Name": scenario.get("name", "Unknown"),
                    "Description": scenario.get("description", "No description")[:50] + "...",
                    "Status": "Optimized" if scenario.get("parameters") else "Pending"
                })
            
            df = pd.DataFrame(scenario_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No scenarios found. Create your first scenario in the Scenario Builder.")
    
    with col2:
        st.subheader("Quick Actions")
        
        if st.button("Create New Scenario", use_container_width=True, key="create_scenario"):
            st.session_state.navigate_to = "Scenario Builder"
            st.rerun()
        
        if st.button("Run Optimization", use_container_width=True, key="run_optimization"):
            st.session_state.navigate_to = "Visualize Pathways"
            st.rerun()
        
        if st.button("View Reports", use_container_width=True, key="view_reports"):
            st.session_state.navigate_to = "Reports & Export"
            st.rerun()
    
    st.divider()
    
    # Sample Chart for Demo
    st.subheader("Sample Pathway Visualization")
    
    # Create sample data for demo
    years = [2025, 2030, 2035, 2040, 2045, 2050]
    emissions = [100, 85, 70, 55, 35, 20]  # Decreasing emissions
    costs = [10, 9.5, 9, 8.2, 7.5, 7]  # Decreasing costs
    
    # Create the chart with green and blue theme
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years, y=emissions,
        mode='lines+markers',
        name='CO₂ Emissions (kt)',
        line=dict(color='#2E8B57', width=3),
        marker=dict(size=8, color='#2E8B57')
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=[c * 10 for c in costs],  # Scale costs for visibility
        mode='lines+markers',
        name='Cost (£M)',
        line=dict(color='#4682B4', width=3),
        marker=dict(size=8, color='#4682B4'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Sample Decarbonization Pathway",
        xaxis_title="Year",
        yaxis_title="CO₂ Emissions (kt)",
        yaxis2=dict(
            title="Cost (£M)",
            overlaying='y',
            side='right'
        ),
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Demo Info with gradient styling
    with st.expander("Demo Information"):
        st.markdown("""
        **This is a demo of the Pathway Planner tool for Teesside Transport Decarbonization.**
        
        **Key Features:**
        - **Scenario Builder**: Create and manage different decarbonization scenarios
        - **Optimization Engine**: Find optimal fuel mix pathways
        - **Visualization**: Interactive charts and pathway analysis
        - **Reporting**: Export results in CSV and PDF formats
        
        **Next Steps:**
        1. Create a scenario in Scenario Builder
        2. Run optimization in Visualize Pathways
        3. Export results and reports
        
        **Technical Stack:**
        - Backend: FastAPI + SQLAlchemy + PostgreSQL
        - Frontend: Streamlit + Plotly
        - Optimization: Linear programming solver
        """) 