import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def show():
    # Main header with gradient design
    st.markdown('<div class="main-header"><h1>Uncertainty Explorer</h1><h3>Explore data gaps and uncertainty in transport decarbonization</h3></div>', unsafe_allow_html=True)
    
    # Uncertainty Analysis
    st.subheader("Emissions Uncertainty Analysis")
    
    # Sample uncertainty data
    vehicle_types = ["Passenger Cars", "Buses", "HGVs", "Vans"]
    base_emissions = [0.065, 0.250, 0.325, 0.120]  # Electric vehicle emissions
    uncertainty_ranges = [0.02, 0.05, 0.08, 0.03]  # Uncertainty ranges
    
    # Create uncertainty visualization with green and blue theme
    fig = go.Figure()
    
    for i, vehicle in enumerate(vehicle_types):
        base = base_emissions[i]
        uncertainty = uncertainty_ranges[i]
        
        # Add uncertainty range
        fig.add_trace(go.Scatter(
            x=[vehicle, vehicle],
            y=[base - uncertainty, base + uncertainty],
            mode='lines',
            line=dict(color='#4682B4', width=8),
            name=f'{vehicle} Range',
            showlegend=False
        ))
        
        # Add central estimate
        fig.add_trace(go.Scatter(
            x=[vehicle],
            y=[base],
            mode='markers',
            marker=dict(size=12, color='#2E8B57'),
            name=f'{vehicle} Estimate',
            showlegend=False
        ))
    
    fig.update_layout(
        title="Emissions Uncertainty by Vehicle Type",
        xaxis_title="Vehicle Type",
        yaxis_title="Emissions (kg CO₂e/km)",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Data Quality Assessment
    st.subheader("Data Quality Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Completeness**")
        
        # Sample data completeness
        data_sources = ["DEFRA Emissions", "BEIS Energy", "DfT Transport", "Local Authority"]
        completeness = [95, 87, 78, 65]
        
        fig = px.bar(
            x=data_sources,
            y=completeness,
            title="Data Completeness by Source (%)",
            labels={'x': 'Data Source', 'y': 'Completeness (%)'},
            color_discrete_sequence=['#2E8B57']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Data Confidence Levels**")
        
        # Confidence levels for different parameters
        parameters = ["Vehicle Emissions", "Fuel Costs", "Infrastructure", "Policy Timeline"]
        confidence = [85, 70, 60, 90]
        
        fig = px.bar(
            x=parameters,
            y=confidence,
            title="Confidence Levels (%)",
            labels={'x': 'Parameter', 'y': 'Confidence (%)'},
            color_discrete_sequence=['#4682B4']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Sensitivity Analysis
    st.subheader("Sensitivity Analysis")
    
    # Parameter sensitivity
    sensitivity_params = ["Electricity Grid Mix", "Hydrogen Production", "Vehicle Efficiency", "Infrastructure Costs"]
    sensitivity_scores = [0.85, 0.72, 0.68, 0.45]
    
    fig = px.bar(
        x=sensitivity_params,
        y=sensitivity_scores,
        title="Parameter Sensitivity Scores",
        labels={'x': 'Parameter', 'y': 'Sensitivity Score'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Monte Carlo Simulation
    st.subheader("Monte Carlo Simulation")
    
    if st.button("Run Uncertainty Simulation"):
        # Generate sample Monte Carlo results
        np.random.seed(42)
        n_simulations = 1000
        
        # Simulate emissions reductions with uncertainty
        base_reduction = 0.6  # 60% reduction target
        uncertainty = 0.1     # 10% uncertainty
        
        reductions = np.random.normal(base_reduction, uncertainty, n_simulations)
        costs = np.random.normal(100, 20, n_simulations)  # £100M ± £20M
        
        # Create scatter plot
        fig = px.scatter(
            x=reductions * 100,
            y=costs,
            title="Emissions Reduction vs Cost (Monte Carlo Simulation)",
            labels={'x': 'Emissions Reduction (%)', 'y': 'Cost (£M)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean Reduction", f"{np.mean(reductions)*100:.1f}%")
        with col2:
            st.metric("Mean Cost", f"£{np.mean(costs):.0f}M")
        with col3:
            st.metric("Success Rate", f"{np.sum(reductions >= 0.5)/len(reductions)*100:.1f}%")
    
    st.divider()
    
    # Recommendations
    st.subheader("Recommendations")
    
    with st.expander("Data Improvement Priorities"):
        st.markdown("""
        **High Priority:**
        - Improve local transport data collection
        - Standardize emissions measurement protocols
        - Enhance infrastructure cost data
        
        **Medium Priority:**
        - Develop real-time emissions monitoring
        - Improve hydrogen production data
        - Better vehicle efficiency tracking
        
        **Low Priority:**
        - Historical data validation
        - Cross-border data harmonization
        """)
    
    # Quick navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Scenario Builder", use_container_width=True):
            st.switch_page("pages/scenario_builder.py")
    with col2:
        if st.button("Go to Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py") 