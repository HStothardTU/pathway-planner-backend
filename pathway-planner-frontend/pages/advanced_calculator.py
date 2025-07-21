"""
Advanced Calculation Engine Frontend
Week 3-4: Per-vehicle, per-year calculation engine with real-time aggregation
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import time

# API configuration
API_BASE = "http://localhost:8000/api/v1"

def show():
    """Main function to display the advanced calculation engine page"""
    
    st.set_page_config(
        page_title="Advanced Calculation Engine",
        page_icon="⚡",
        layout="wide"
    )
    
    st.title("⚡ Advanced Calculation Engine")
    st.markdown("**Week 3-4: Per-vehicle, per-year calculations with real-time aggregation**")
    
    # Sidebar for navigation
    st.sidebar.title("Advanced Calculator")
    page = st.sidebar.selectbox(
        "Choose Section:",
        ["Overview", "Scenario Calculator", "Real-time Monitoring", "Constraint Analysis", "Performance Metrics"]
    )
    
    if page == "Overview":
        show_overview()
    elif page == "Scenario Calculator":
        show_scenario_calculator()
    elif page == "Real-time Monitoring":
        show_real_time_monitoring()
    elif page == "Constraint Analysis":
        show_constraint_analysis()
    elif page == "Performance Metrics":
        show_performance_metrics()

def show_overview():
    """Show overview of the advanced calculation engine"""
    
    st.header("🚀 Advanced Calculation Engine Overview")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### **Week 3-4 Implementation Features:**
        
        #### **🔧 Per-Vehicle, Per-Year Calculation Engine**
        - **Granular Analysis**: Individual vehicle calculations for each year
        - **Technology Progression**: Realistic adoption curves and technology evolution
        - **Multi-dimensional Calculations**: Emissions, costs, energy, infrastructure, health, and economic impacts
        
        #### **📊 Real-Time Aggregation System**
        - **Multi-level Aggregation**: Vehicle → Vehicle Type → Category → Total
        - **Live Updates**: Real-time progress monitoring and result updates
        - **Performance Optimization**: Efficient handling of large datasets
        
        #### **🎯 Constraint Management Framework**
        - **Technology Readiness**: TRL-based constraint validation
        - **Market Penetration**: Realistic adoption rate limits
        - **Infrastructure Capacity**: Infrastructure requirement validation
        - **Cost Constraints**: Budget and economic feasibility checks
        - **Policy Constraints**: Regulatory and policy compliance
        
        #### **📈 Advanced Analytics**
        - **Comprehensive Metrics**: 6 calculation types with detailed breakdowns
        - **Scenario Comparison**: Multi-scenario analysis and comparison
        - **Risk Assessment**: Constraint violation analysis and mitigation strategies
        - **Performance Monitoring**: Real-time engine performance metrics
        """)
    
    with col2:
        st.info("**Quick Start:**")
        st.markdown("""
        1. **Scenario Calculator**: Create and run advanced scenarios
        2. **Real-time Monitoring**: Watch calculations in progress
        3. **Constraint Analysis**: Analyze and validate constraints
        4. **Performance Metrics**: Monitor engine performance
        """)
        
        # Check engine health
        if st.button("🔍 Check Engine Health"):
            health_status = check_engine_health()
            if health_status.get('status') == 'healthy':
                st.success("✅ Advanced Calculation Engine is healthy!")
                st.json(health_status)
            else:
                st.error("❌ Engine health check failed")
                st.json(health_status)

def show_scenario_calculator():
    """Show the advanced scenario calculator"""
    
    st.header("🧮 Advanced Scenario Calculator")
    
    # Scenario configuration
    with st.expander("📋 Scenario Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            scenario_id = st.text_input("Scenario ID", value=f"advanced_scenario_{int(time.time())}")
            years = st.multiselect(
                "Analysis Years",
                options=list(range(2020, 2061)),
                default=[2025, 2030, 2035, 2040, 2045, 2050],
                help="Select years for analysis"
            )
            target_reduction = st.slider(
                "Target Emissions Reduction (%)",
                min_value=0,
                max_value=100,
                value=50,
                help="Target percentage reduction in emissions"
            )
        
        with col2:
            vehicle_types = st.multiselect(
                "Vehicle Types",
                options=["Passenger Cars", "Buses", "Heavy Goods Vehicles (HGVs)", 
                        "Vans / Light Goods Vehicles (LGVs)", "Motorcycles", "Specialist Vehicles"],
                default=["Passenger Cars", "Buses"],
                help="Select vehicle types to analyze"
            )
            
            calculation_types = st.multiselect(
                "Calculation Types",
                options=["emissions", "cost", "energy", "infrastructure", "health_impact", "economic_impact"],
                default=["emissions", "cost", "energy"],
                help="Select types of calculations to perform"
            )
            
            aggregation_levels = st.multiselect(
                "Aggregation Levels",
                options=["vehicle", "vehicle_type", "category", "year", "total"],
                default=["vehicle_type", "total"],
                help="Select levels for result aggregation"
            )
    
    # Constraints configuration
    with st.expander("🎯 Constraints Configuration"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Technology Readiness")
            min_trl = st.slider("Minimum TRL", 1, 9, 7, help="Minimum Technology Readiness Level")
            max_adoption_rate = st.slider("Max Annual Adoption Rate (%)", 5, 50, 20)
        
        with col2:
            st.subheader("Infrastructure & Cost")
            infrastructure_budget = st.number_input("Infrastructure Budget (£M)", value=1000.0, step=100.0)
            max_cost_increase = st.slider("Max Cost Increase (%)", 0, 100, 30)
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            real_time_updates = st.checkbox("Enable Real-time Updates", value=True)
            store_results = st.checkbox("Store Results", value=True)
            cache_enabled = st.checkbox("Enable Caching", value=True)
        
        with col2:
            max_workers = st.slider("Max Workers", 1, 8, 4)
            enable_constraints = st.checkbox("Enable Constraints", value=True)
            detailed_output = st.checkbox("Detailed Output", value=True)
    
    # Run calculation
    if st.button("🚀 Run Advanced Calculation", type="primary"):
        if not years or not vehicle_types:
            st.error("Please select years and vehicle types")
            return
        
        # Prepare scenario data
        scenario_data = {
            "scenario_id": scenario_id,
            "years": years,
            "vehicle_types": vehicle_types,
            "target_reduction": target_reduction / 100.0,
            "constraints": {
                "technology_readiness": {"min_trl": min_trl},
                "market_penetration": {"max_adoption_rate": max_adoption_rate / 100.0},
                "infrastructure_capacity": {"budget": infrastructure_budget * 1000000},
                "cost_constraints": {"max_increase": max_cost_increase / 100.0}
            },
            "calculation_types": calculation_types,
            "aggregation_levels": aggregation_levels,
            "real_time_updates": real_time_updates,
            "store_results": store_results
        }
        
        # Run calculation with progress tracking
        with st.spinner("Running advanced calculation..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Simulate calculation progress
                for i in range(101):
                    time.sleep(0.05)
                    progress_bar.progress(i)
                    if i < 25:
                        status_text.text("Initializing calculation engine...")
                    elif i < 50:
                        status_text.text("Processing per-vehicle calculations...")
                    elif i < 75:
                        status_text.text("Performing real-time aggregation...")
                    elif i < 90:
                        status_text.text("Analyzing constraints...")
                    else:
                        status_text.text("Finalizing results...")
                
                # Call API
                response = requests.post(f"{API_BASE}/advanced/calculate", json=scenario_data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Advanced calculation completed successfully!")
                    
                    # Display results
                    display_advanced_results(result)
                    
                else:
                    st.error(f"❌ Calculation failed: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error during calculation: {str(e)}")
            finally:
                progress_bar.empty()
                status_text.empty()

def display_advanced_results(result):
    """Display advanced calculation results"""
    
    st.header("📊 Advanced Calculation Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emissions", f"{result['summary']['total_emissions']:,.0f} kg CO₂e")
    
    with col2:
        st.metric("Total Cost", f"£{result['summary']['total_cost']:,.0f}")
    
    with col3:
        st.metric("Years Analyzed", result['summary']['years_analyzed'])
    
    with col4:
        st.metric("Vehicle Types", result['summary']['vehicle_types_analyzed'])
    
    # Detailed results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Summary", "🔍 Performance", "⚠️ Constraints", "📋 Details"])
    
    with tab1:
        st.subheader("Calculation Summary")
        st.json(result['summary'])
    
    with tab2:
        st.subheader("Performance Metrics")
        metrics = result['performance_metrics']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Calculation Time", f"{metrics.get('calculation_time', 'N/A')}")
            st.metric("Vehicles Processed", metrics.get('total_vehicles_processed', 0))
        
        with col2:
            st.metric("Cache Hit Rate", f"{metrics.get('cache_hit_rate', 0):.1%}")
            st.metric("Memory Usage", f"{metrics.get('memory_usage', {}).get('total_memory_mb', 0):.1f} MB")
    
    with tab3:
        st.subheader("Constraint Analysis")
        constraint_analysis = result['constraint_analysis']
        
        if constraint_analysis.get('overall_compliance'):
            st.success("✅ All constraints satisfied")
        else:
            st.warning("⚠️ Some constraint violations detected")
            violations = constraint_analysis.get('constraint_violations', [])
            for violation in violations:
                st.error(f"Year {violation['year']}: {violation['vehicle_type']} - {violation['violations']}")
    
    with tab4:
        st.subheader("Detailed Results")
        st.json(result)

def show_real_time_monitoring():
    """Show real-time monitoring dashboard"""
    
    st.header("📡 Real-time Monitoring Dashboard")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Enable Auto-refresh", value=True)
    
    if auto_refresh:
        st.empty()
        # This would normally use st.empty() with a timer for real-time updates
        st.info("Real-time monitoring would show live calculation progress here")
    
    # Mock real-time data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Calculations", "3")
        st.metric("Cache Hit Rate", "85.2%")
    
    with col2:
        st.metric("Memory Usage", "512 MB")
        st.metric("CPU Usage", "23%")
    
    with col3:
        st.metric("Queue Length", "2")
        st.metric("Avg Response Time", "2.3s")
    
    # Real-time updates chart
    st.subheader("📈 Real-time Updates")
    
    # Mock data for demonstration
    updates_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=20, freq='S'),
        'progress': [i * 5 for i in range(20)],
        'memory_usage': [400 + i * 2 for i in range(20)],
        'cpu_usage': [20 + i * 0.5 for i in range(20)]
    })
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Calculation Progress (%)', 'System Resources'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Scatter(x=updates_data['timestamp'], y=updates_data['progress'], 
                  name='Progress', line=dict(color='blue')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=updates_data['timestamp'], y=updates_data['memory_usage'], 
                  name='Memory (MB)', line=dict(color='green')),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=updates_data['timestamp'], y=updates_data['cpu_usage'], 
                  name='CPU (%)', line=dict(color='red')),
        row=2, col=1
    )
    
    fig.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

def show_constraint_analysis():
    """Show constraint analysis interface"""
    
    st.header("🎯 Constraint Analysis")
    
    # Constraint input
    with st.expander("📋 Constraint Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Technology Constraints")
            min_technology_readiness = st.slider("Min Technology Readiness Level", 1, 9, 7)
            max_adoption_rate = st.slider("Max Annual Adoption Rate (%)", 5, 50, 20)
            technology_maturity_threshold = st.slider("Technology Maturity Threshold", 1, 9, 6)
        
        with col2:
            st.subheader("Infrastructure Constraints")
            max_infrastructure_budget = st.number_input("Max Infrastructure Budget (£M)", value=1000.0)
            charging_station_capacity = st.number_input("Charging Station Capacity", value=1000)
            grid_capacity_mw = st.number_input("Grid Capacity (MW)", value=100.0)
    
    # Run constraint analysis
    if st.button("🔍 Analyze Constraints"):
        # Mock constraint analysis
        st.info("Running constraint analysis...")
        
        # Simulate analysis
        time.sleep(2)
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ Technology Readiness: PASS")
            st.success("✅ Market Penetration: PASS")
            st.warning("⚠️ Infrastructure Capacity: PARTIAL")
        
        with col2:
            st.success("✅ Cost Constraints: PASS")
            st.success("✅ Policy Constraints: PASS")
            st.error("❌ Grid Capacity: FAIL")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        st.markdown("""
        - **Grid Capacity**: Consider phased rollout to manage grid load
        - **Infrastructure**: Plan for additional charging infrastructure
        - **Technology**: Monitor technology readiness for emerging solutions
        """)

def show_performance_metrics():
    """Show performance metrics dashboard"""
    
    st.header("📊 Performance Metrics Dashboard")
    
    # Get performance metrics
    if st.button("🔄 Refresh Metrics"):
        try:
            response = requests.post(f"{API_BASE}/advanced/performance-metrics", 
                                   json={"include_cache_metrics": True, "include_memory_metrics": True})
            
            if response.status_code == 200:
                metrics = response.json()
                display_performance_metrics(metrics)
            else:
                st.error("Failed to fetch performance metrics")
        except Exception as e:
            st.error(f"Error fetching metrics: {str(e)}")
    
    # Mock performance metrics for demonstration
    st.subheader("📈 System Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cache Hit Rate", "85.2%", "2.1%")
        st.metric("Cache Size", "24 MB", "1.2 MB")
    
    with col2:
        st.metric("Memory Usage", "512 MB", "-15 MB")
        st.metric("Active Connections", "12", "3")
    
    with col3:
        st.metric("Avg Response Time", "2.3s", "-0.5s")
        st.metric("Requests/sec", "45", "8")
    
    with col4:
        st.metric("Error Rate", "0.2%", "-0.1%")
        st.metric("Uptime", "99.8%", "0.1%")
    
    # Performance charts
    st.subheader("📊 Performance Trends")
    
    # Mock performance data
    performance_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=24, freq='H'),
        'response_time': [2.1, 2.3, 2.0, 2.5, 2.2, 2.4, 2.1, 2.3, 2.0, 2.2, 2.4, 2.1,
                         2.3, 2.0, 2.2, 2.5, 2.1, 2.3, 2.0, 2.2, 2.4, 2.1, 2.3, 2.0],
        'memory_usage': [480, 485, 490, 495, 500, 505, 510, 515, 520, 525, 530, 535,
                        540, 545, 550, 555, 560, 565, 570, 575, 580, 585, 590, 595],
        'cache_hit_rate': [82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 98, 96,
                          94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72]
    })
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Response Time (seconds)', 'Memory Usage (MB)', 'Cache Hit Rate (%)'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Scatter(x=performance_data['timestamp'], y=performance_data['response_time'], 
                  name='Response Time', line=dict(color='blue')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=performance_data['timestamp'], y=performance_data['memory_usage'], 
                  name='Memory Usage', line=dict(color='green')),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=performance_data['timestamp'], y=performance_data['cache_hit_rate'], 
                  name='Cache Hit Rate', line=dict(color='orange')),
        row=3, col=1
    )
    
    fig.update_layout(height=800, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

def display_performance_metrics(metrics):
    """Display performance metrics"""
    st.json(metrics)

def check_engine_health():
    """Check the health of the advanced calculation engine"""
    try:
        response = requests.get(f"{API_BASE}/advanced/health")
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "unhealthy", "error": "Health check failed"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    show() 