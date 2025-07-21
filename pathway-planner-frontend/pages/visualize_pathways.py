import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

API_BASE = "http://localhost:8000/api/v1"

def get_scenarios():
    try:
        response = requests.get(f"{API_BASE}/scenarios/")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching scenarios: {e}")
    return []

def run_optimization(scenario_id: int, include_usage_patterns: bool = True, enable_constraints: bool = True):
    """Run optimization for a specific scenario"""
    try:
        data = {
            "scenario_id": scenario_id,
            "include_usage_patterns": include_usage_patterns,
            "enable_constraints": enable_constraints
        }
        
        response = requests.post(f"{API_BASE}/optimize", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Optimization failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error running optimization: {e}")
        return None

def show():
    # Main header with gradient design
    st.markdown('<div class="main-header"><h1>Visualize Pathways</h1><h3>Run optimization and visualize decarbonization pathways</h3></div>', unsafe_allow_html=True)
    
    # Get selected scenario
    selected_id = st.session_state.get("selected_scenario_id")
    scenarios = get_scenarios()
    
    if selected_id and scenarios:
        selected_scenario = next((s for s in scenarios if s["id"] == selected_id), None)
        if selected_scenario:
            st.success(f"Selected Scenario: **{selected_scenario['name']}**")
            
            # Display scenario details
            with st.expander("Scenario Details", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Description:** {selected_scenario.get('description', 'No description')}")
                    if selected_scenario.get('parameters'):
                        params = selected_scenario['parameters']
                        st.markdown(f"**Target Reduction:** {params.get('target_emissions_reduction', 0)*100:.1f}%")
                        st.markdown(f"**Max Annual Change:** {params.get('max_annual_change', 0)*100:.1f}%")
                        st.markdown(f"**Analysis Years:** {len(params.get('years', []))}")
                
                with col2:
                    if selected_scenario.get('parameters'):
                        params = selected_scenario['parameters']
                        vehicle_types = params.get('vehicle_types', [])
                        st.markdown(f"**Vehicle Types:** {len(vehicle_types)} categories")
                        for vt in vehicle_types:
                            st.markdown(f"• {vt}")
                        
                        if params.get('usage_patterns'):
                            st.markdown("**Usage Patterns:** Enabled")
                        else:
                            st.markdown("**Usage Patterns:** Disabled")
                        
                        if params.get('enable_constraints', True):
                            st.markdown("**Constraints:** Enabled")
                        else:
                            st.markdown("**Constraints:** Disabled")
    
    # Scenario selection
    if scenarios:
        scenario_names = [f"{s['name']} (ID: {s['id']})" for s in scenarios]
        selected_scenario_name = st.selectbox(
            "Select Scenario for Optimization",
            scenario_names,
            index=0 if not selected_id else next((i for i, s in enumerate(scenarios) if s["id"] == selected_id), 0)
        )
        
        # Extract scenario ID
        selected_scenario_id = int(selected_scenario_name.split("(ID: ")[1].split(")")[0])
        selected_scenario = next((s for s in scenarios if s["id"] == selected_scenario_id), None)
        
        if selected_scenario:
            st.session_state["selected_scenario_id"] = selected_scenario_id
            
            # Optimization options
            st.subheader("Optimization Options")
            col1, col2 = st.columns(2)
            
            with col1:
                include_usage_patterns = st.checkbox(
                    "Include Usage Patterns", 
                    value=selected_scenario.get('parameters', {}).get('usage_patterns') is not None,
                    help="Use realistic annual mileage for each vehicle type"
                )
            
            with col2:
                enable_constraints = st.checkbox(
                    "Enable Constraints", 
                    value=selected_scenario.get('parameters', {}).get('enable_constraints', True),
                    help="Apply realistic technology adoption constraints"
                )
            
            # Run optimization
            if st.button("Run Optimization", type="primary"):
                with st.spinner("Running optimization..."):
                    optimization_result = run_optimization(
                        selected_scenario_id, 
                        include_usage_patterns, 
                        enable_constraints
                    )
                    
                    if optimization_result and optimization_result.get('success'):
                        st.session_state["optimization_results"] = optimization_result
                        st.success("Optimization completed successfully!")
                    else:
                        st.error("Optimization failed. Check the scenario parameters.")
    
    # Display optimization results
    if "optimization_results" in st.session_state:
        results = st.session_state["optimization_results"]
        
        st.subheader("Optimization Results")
        
        # Summary metrics
        if results.get('results', {}).get('summary'):
            summary = results['results']['summary']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Initial Emissions", 
                    f"{summary.get('initial_emissions', 0):.1f}",
                    help="Emissions at the start of the analysis period"
                )
            
            with col2:
                st.metric(
                    "Final Emissions", 
                    f"{summary.get('final_emissions', 0):.1f}",
                    help="Emissions at the end of the analysis period"
                )
            
            with col3:
                st.metric(
                    "Total Reduction", 
                    f"{summary.get('total_reduction_percent', 0):.1f}%",
                    help="Percentage reduction achieved"
                )
            
            with col4:
                st.metric(
                    "Target Achieved", 
                    "Yes" if summary.get('target_achieved', False) else "No",
                    help="Whether the target reduction was achieved"
                )
        
        # Emissions over time
        if results.get('results', {}).get('emissions_by_year'):
            st.subheader("Emissions Reduction Over Time")
            
            emissions_data = results['results']['emissions_by_year']
            df_emissions = pd.DataFrame(emissions_data)
            
            fig = go.Figure()
            
            # Emissions line
            fig.add_trace(go.Scatter(
                x=df_emissions['year'],
                y=df_emissions['emissions'],
                mode='lines+markers',
                name='Total Emissions',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ))
            
            # Reduction percentage (secondary axis)
            fig.add_trace(go.Scatter(
                x=df_emissions['year'],
                y=df_emissions['reduction_percent'],
                mode='lines+markers',
                name='Reduction %',
                yaxis='y2',
                line=dict(color='green', width=2, dash='dash'),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title="Emissions and Reduction Over Time",
                xaxis_title="Year",
                yaxis_title="Emissions (kg CO₂e)",
                yaxis2=dict(
                    title="Reduction (%)",
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                ),
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Vehicle type breakdown
        if results.get('results', {}).get('emissions_by_vehicle_type'):
            st.subheader("Emissions by Vehicle Type")
            
            vehicle_emissions = results['results']['emissions_by_vehicle_type']
            
            # Create stacked area chart
            fig = go.Figure()
            
            for vehicle_type, data in vehicle_emissions.items():
                df_vehicle = pd.DataFrame(data)
                fig.add_trace(go.Scatter(
                    x=df_vehicle['year'],
                    y=df_vehicle['emissions'],
                    mode='lines',
                    fill='tonexty',
                    name=vehicle_type,
                    stackgroup='one'
                ))
            
            fig.update_layout(
                title="Emissions Breakdown by Vehicle Type",
                xaxis_title="Year",
                yaxis_title="Emissions (kg CO₂e)",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Adoption progress
        if results.get('results', {}).get('adoption_progress'):
            st.subheader("Technology Adoption Progress")
            
            adoption_data = results['results']['adoption_progress']
            
            # Create line chart for adoption rates
            fig = go.Figure()
            
            for vehicle_type, data in adoption_data.items():
                df_adoption = pd.DataFrame(data)
                fig.add_trace(go.Scatter(
                    x=df_adoption['year'],
                    y=df_adoption['adoption_rate'],
                    mode='lines+markers',
                    name=vehicle_type,
                    line=dict(width=3),
                    marker=dict(size=6)
                ))
            
            fig.update_layout(
                title="Clean Technology Adoption Rates",
                xaxis_title="Year",
                yaxis_title="Adoption Rate (%)",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Cost analysis
        if results.get('results', {}).get('cost_analysis', {}).get('total_cost_by_year'):
            st.subheader("Cost Analysis")
            
            cost_data = results['results']['cost_analysis']['total_cost_by_year']
            df_cost = pd.DataFrame(cost_data)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_cost['year'],
                y=df_cost['cost_per_mile'],
                mode='lines+markers',
                name='Cost per Mile',
                line=dict(color='blue', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Transport Cost Evolution",
                xaxis_title="Year",
                yaxis_title="Cost per Mile (£)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Optimization information
        if results.get('optimization_info'):
            st.subheader("Optimization Details")
            
            opt_info = results['optimization_info']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Iterations", opt_info.get('iterations', 0))
            
            with col2:
                st.metric("Function Evaluations", opt_info.get('function_evaluations', 0))
            
            with col3:
                st.metric("Final Objective", f"{opt_info.get('final_objective', 0):.2f}")
        
        # Export options
        st.subheader("Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to CSV"):
                if selected_scenario_id:
                    try:
                        response = requests.get(f"{API_BASE}/scenarios/{selected_scenario_id}/export/csv")
                        if response.status_code == 200:
                            csv_data = response.json()
                            st.download_button(
                                label="Download CSV",
                                data=csv_data['content'],
                                file_name=csv_data['filename'],
                                mime="text/csv"
                            )
                        else:
                            st.error("Failed to export CSV")
                    except Exception as e:
                        st.error(f"Export error: {e}")
        
        with col2:
            if st.button("Export to PDF"):
                st.info("PDF export functionality coming in Week 2")
    
    else:
        # Show demo data option
        if st.button("Load Demo Data for Optimization"):
            st.info("Please select a scenario and run optimization to see results.")
        
        # Show sample visualization
        st.subheader("Sample Pathway Visualization")
        
        # Create sample data
        years = [2025, 2030, 2035, 2040, 2045, 2050]
        sample_emissions = [100, 85, 70, 55, 40, 25]
        sample_reduction = [0, 15, 30, 45, 60, 75]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=sample_emissions,
            mode='lines+markers',
            name='Sample Emissions',
            line=dict(color='red', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=sample_reduction,
            mode='lines+markers',
            name='Sample Reduction %',
            yaxis='y2',
            line=dict(color='green', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Sample Decarbonization Pathway",
            xaxis_title="Year",
            yaxis_title="Emissions (kg CO₂e)",
            yaxis2=dict(
                title="Reduction (%)",
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("Select a scenario and run optimization to see real results!")
    
    # Quick navigation
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Scenario Builder", use_container_width=True):
            st.switch_page("pages/scenario_builder.py")
    with col2:
        if st.button("Go to Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py")
    with col3:
        if st.button("Reports & Export", use_container_width=True):
            st.switch_page("pages/reports_export.py") 