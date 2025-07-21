import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

def get_scenarios():
    try:
        response = requests.get(f"{API_BASE}/scenarios/")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def show():
    # Main header with gradient design
    st.markdown('<div class="main-header"><h1>Reports & Export</h1><h3>Generate and export comprehensive decarbonization reports</h3></div>', unsafe_allow_html=True)
    
    # Report Generation
    st.subheader("Generate Report")
    
    scenarios = get_scenarios()
    
    if scenarios:
        # Scenario selection
        scenario_options = {s["name"]: s["id"] for s in scenarios}
        selected_scenario_name = st.selectbox("Select Scenario", list(scenario_options.keys()))
        selected_scenario_id = scenario_options[selected_scenario_name]
        
        # Report type selection
        report_type = st.radio(
            "Report Type",
            ["Executive Summary", "Technical Analysis", "Full Report", "Custom"]
        )
        
        # Report options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Content Options**")
            include_charts = st.checkbox("Include Charts", value=True)
            include_tables = st.checkbox("Include Data Tables", value=True)
            include_recommendations = st.checkbox("Include Recommendations", value=True)
            include_uncertainty = st.checkbox("Include Uncertainty Analysis", value=False)
        
        with col2:
            st.markdown("**Format Options**")
            include_executive_summary = st.checkbox("Executive Summary", value=True)
            include_methodology = st.checkbox("Methodology", value=False)
            include_appendix = st.checkbox("Appendix", value=False)
            include_references = st.checkbox("References", value=True)
        
        # Generate report
        if st.button("Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                # Simulate report generation
                st.success("Report generated successfully!")
                
                # Show report preview
                st.subheader("Report Preview")
                
                # Executive Summary
                if include_executive_summary:
                    st.markdown("### Executive Summary")
                    st.markdown(f"""
                    **Scenario:** {selected_scenario_name}
                    
                    This report presents the decarbonization pathway analysis for Teesside transport, 
                    focusing on achieving significant emissions reductions through strategic vehicle 
                    electrification and infrastructure development.
                    
                    **Key Findings:**
                    - Target emissions reduction: 60%
                    - Estimated cost: £2.3M
                    - Timeline: 2025-2050
                    - Primary focus: Passenger vehicles and public transport
                    """)
                
                # Technical Analysis
                if include_charts:
                    st.markdown("### Technical Analysis")
                    
                    # Sample chart with green and blue theme
                    years = [2025, 2030, 2035, 2040, 2045, 2050]
                    emissions = [100, 85, 70, 55, 35, 20]
                    costs = [10, 9.5, 9, 8.2, 7.5, 7]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=years, 
                        y=emissions, 
                        name='Emissions (kt)',
                        line=dict(color='#2E8B57', width=3),
                        marker=dict(color='#2E8B57', size=8)
                    ))
                    fig.add_trace(go.Scatter(
                        x=years, 
                        y=[c*10 for c in costs], 
                        name='Cost (£M)', 
                        yaxis='y2',
                        line=dict(color='#4682B4', width=3),
                        marker=dict(color='#4682B4', size=8)
                    ))
                    fig.update_layout(
                        title="Emissions and Cost Projections",
                        yaxis2=dict(overlaying='y', side='right'),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Data Tables
                if include_tables:
                    st.markdown("### Data Tables")
                    
                    # Sample data table
                    data = {
                        "Year": [2025, 2030, 2035, 2040, 2045, 2050],
                        "Emissions (kt)": [100, 85, 70, 55, 35, 20],
                        "Cost (£M)": [10, 9.5, 9, 8.2, 7.5, 7],
                        "Electric Vehicles (%)": [10, 25, 45, 65, 80, 90]
                    }
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Recommendations
                if include_recommendations:
                    st.markdown("### Recommendations")
                    st.markdown("""
                    1. **Immediate Actions (2025-2030):**
                       - Begin electric vehicle infrastructure rollout
                       - Implement public transport electrification
                       - Develop hydrogen refueling network
                    
                    2. **Medium-term Goals (2030-2040):**
                       - Achieve 50% electric vehicle adoption
                       - Complete public transport electrification
                       - Establish hydrogen economy foundation
                    
                    3. **Long-term Vision (2040-2050):**
                       - Achieve net-zero transport emissions
                       - Full integration of renewable energy
                       - Sustainable transport ecosystem
                    """)
        
        st.divider()
        
        # Export Options
        st.subheader("Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Export PDF"):
                st.info("PDF export functionality would be implemented here")
        
        with col2:
            if st.button("Export Excel"):
                st.info("Excel export functionality would be implemented here")
        
        with col3:
            if st.button("Export CSV"):
                st.info("CSV export functionality would be implemented here")
    
    else:
        st.info("No scenarios found. Create scenarios in the Scenario Builder first.")
    
    st.divider()
    
    # Report Templates
    st.subheader("Report Templates")
    
    template_options = [
        "Executive Summary Template",
        "Technical Report Template", 
        "Stakeholder Presentation Template",
        "Policy Brief Template"
    ]
    
    selected_template = st.selectbox("Select Template", template_options)
    
    if st.button("Load Template"):
        st.info(f"Template '{selected_template}' would be loaded here")
    
    st.divider()
    
    # Report History
    st.subheader("Report History")
    
    # Sample report history
    report_history = [
        {"date": "2025-01-15", "scenario": "Conservative Pathway", "type": "Executive Summary", "status": "Generated"},
        {"date": "2025-01-10", "scenario": "Accelerated Transition", "type": "Technical Analysis", "status": "Generated"},
        {"date": "2025-01-05", "scenario": "Net Zero by 2040", "type": "Full Report", "status": "Generated"}
    ]
    
    if report_history:
        df_history = pd.DataFrame(report_history)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
    else:
        st.info("No reports generated yet.")
    
    # Quick navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Scenario Builder", use_container_width=True):
            st.switch_page("pages/scenario_builder.py")
    with col2:
        if st.button("Go to Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py") 