import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import requests
import json

def show():
    """Show the Analysis & Insights dashboard"""
    
    # Main header with gradient design
    st.markdown('<div class="main-header"><h1>Analysis & Insights Dashboard</h1></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for filters
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Filters</div>', unsafe_allow_html=True)
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Emissions & Cost Summary", "Emission Intensity vs Cost", "Carbon-Intensive Segments", "Low-Efficiency Analysis"]
        )
        
        # Vehicle category filter
        categories = ["All Categories", "Cars", "Vans", "Trucks", "Buses", "Motorcycles", "Other"]
        selected_category = st.selectbox("Vehicle Category", categories)
        
        # Year range
        year_range = st.slider("Year Range", 2020, 2050, (2020, 2050))
        
        # Cost threshold
        cost_threshold = st.slider("Cost Threshold (£/km)", 0.0, 2.0, 0.5, 0.1)
        
        # Emissions threshold
        emissions_threshold = st.slider("Emissions Threshold (kg CO₂e/km)", 0.0, 1.0, 0.2, 0.05)
    
    # Main content based on analysis type
    if analysis_type == "Emissions & Cost Summary":
        show_emissions_cost_summary(selected_category, year_range)
    elif analysis_type == "Emission Intensity vs Cost":
        show_emission_intensity_cost(selected_category, year_range)
    elif analysis_type == "Carbon-Intensive Segments":
        show_carbon_intensive_segments(selected_category, year_range, emissions_threshold)
    elif analysis_type == "Low-Efficiency Analysis":
        show_low_efficiency_analysis(selected_category, year_range, cost_threshold)

def show_emissions_cost_summary(category: str, year_range: Tuple[int, int]):
    """Show emissions and cost summary dashboard by vehicle type and fuel"""
    
    st.markdown('<div class="main-header"><h2>Emissions & Cost Summary Dashboard</h2></div>', unsafe_allow_html=True)
    st.markdown("Comprehensive analysis of emissions and costs by vehicle type and fuel")
    
    # Generate sample data for demonstration
    data = generate_emissions_cost_data(category, year_range)
    
    # Key metrics with gradient cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_emissions = data['total_emissions'].sum()
        st.markdown(f'<div class="metric-card"><h4>Total Emissions</h4><h2>{total_emissions:,.0f} kg CO₂e</h2><p style="color: #2E8B57;">+{total_emissions * 0.05:,.0f} kg CO₂e</p></div>', unsafe_allow_html=True)
    
    with col2:
        total_cost = data['total_cost'].sum()
        st.markdown(f'<div class="metric-card"><h4>Total Cost</h4><h2>£{total_cost:,.0f}</h2><p style="color: #4682B4;">+£{total_cost * 0.03:,.0f}</p></div>', unsafe_allow_html=True)
    
    with col3:
        avg_emissions = data['emissions_per_km'].mean()
        st.markdown(f'<div class="metric-card"><h4>Avg Emissions/km</h4><h2>{avg_emissions:.3f} kg CO₂e/km</h2></div>', unsafe_allow_html=True)
    
    with col4:
        avg_cost = data['cost_per_km'].mean()
        st.markdown(f'<div class="metric-card"><h4>Avg Cost/km</h4><h2>£{avg_cost:.3f}/km</h2></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Emissions by Vehicle Type")
        fig_emissions = px.bar(
            data.groupby('vehicle_type')['total_emissions'].sum().reset_index(),
            x='vehicle_type',
            y='total_emissions',
            title="Total Emissions by Vehicle Type",
            color='total_emissions',
            color_continuous_scale='Greens'
        )
        fig_emissions.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_emissions, use_container_width=True)
    
    with col2:
        st.subheader("Cost by Vehicle Type")
        fig_cost = px.bar(
            data.groupby('vehicle_type')['total_cost'].sum().reset_index(),
            x='vehicle_type',
            y='total_cost',
            title="Total Cost by Vehicle Type",
            color='total_cost',
            color_continuous_scale='Blues'
        )
        fig_cost.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_cost, use_container_width=True)
    
    # Detailed table
    st.subheader("Detailed Analysis Table")
    
    # Aggregate data for table
    summary_data = data.groupby(['vehicle_type', 'fuel_type']).agg({
        'total_emissions': 'sum',
        'total_cost': 'sum',
        'emissions_per_km': 'mean',
        'cost_per_km': 'mean',
        'vehicle_count': 'sum'
    }).reset_index()
    
    # Add efficiency metrics
    summary_data['emissions_efficiency'] = summary_data['emissions_per_km'].rank(ascending=True)
    summary_data['cost_efficiency'] = summary_data['cost_per_km'].rank(ascending=True)
    summary_data['overall_efficiency'] = (summary_data['emissions_efficiency'] + summary_data['cost_efficiency']) / 2
    
    # Format for display
    display_data = summary_data.copy()
    display_data['total_emissions'] = display_data['total_emissions'].apply(lambda x: f"{x:,.0f}")
    display_data['total_cost'] = display_data['total_cost'].apply(lambda x: f"£{x:,.0f}")
    display_data['emissions_per_km'] = display_data['emissions_per_km'].apply(lambda x: f"{x:.3f}")
    display_data['cost_per_km'] = display_data['cost_per_km'].apply(lambda x: f"£{x:.3f}")
    display_data['overall_efficiency'] = display_data['overall_efficiency'].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(display_data, use_container_width=True)

def show_emission_intensity_cost(category: str, year_range: Tuple[int, int]):
    """Visualize emission intensity vs cost for quick insights"""
    
    st.markdown('<div class="main-header"><h2>Emission Intensity vs Cost Analysis</h2></div>', unsafe_allow_html=True)
    st.markdown("Scatter plot analysis showing the relationship between emissions and costs")
    
    # Generate data
    data = generate_emissions_cost_data(category, year_range)
    
    # Create scatter plot with green and blue theme
    fig = px.scatter(
        data,
        x='emissions_per_km',
        y='cost_per_km',
        size='vehicle_count',
        color='vehicle_type',
        hover_data=['fuel_type', 'vehicle_count'],
        title="Emission Intensity vs Cost per Kilometer",
        labels={
            'emissions_per_km': 'Emissions (kg CO₂e/km)',
            'cost_per_km': 'Cost (£/km)',
            'vehicle_count': 'Number of Vehicles'
        },
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Add trend line
    z = np.polyfit(data['emissions_per_km'], data['cost_per_km'], 1)
    p = np.poly1d(z)
    fig.add_trace(
        go.Scatter(
            x=data['emissions_per_km'],
            y=p(data['emissions_per_km']),
            mode='lines',
            name='Trend Line',
            line=dict(color='#2E8B57', dash='dash')
        )
    )
    
    fig.update_layout(
        xaxis_title="Emissions per Kilometer (kg CO₂e/km)",
        yaxis_title="Cost per Kilometer (£/km)",
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    st.subheader("Key Insights")
    
    # Calculate correlations
    correlation = data['emissions_per_km'].corr(data['cost_per_km'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="metric-card"><h4>Correlation</h4><h2>{correlation:.3f}</h2></div>', unsafe_allow_html=True)
        if correlation > 0.7:
            st.success("Strong positive correlation: Higher emissions generally mean higher costs")
        elif correlation > 0.3:
            st.warning("Moderate correlation: Some relationship between emissions and costs")
        else:
            st.info("Weak correlation: Emissions and costs are largely independent")
    
    with col2:
        # Find most efficient and least efficient
        most_efficient = data.loc[data['cost_per_km'].idxmin()]
        least_efficient = data.loc[data['cost_per_km'].idxmax()]
        
        st.markdown(f'<div class="metric-card"><h4>Most Cost-Efficient</h4><p>{most_efficient["vehicle_type"]} ({most_efficient["fuel_type"]}) - £{most_efficient["cost_per_km"]:.3f}/km</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><h4>Least Cost-Efficient</h4><p>{least_efficient["vehicle_type"]} ({least_efficient["fuel_type"]}) - £{least_efficient["cost_per_km"]:.3f}/km</p></div>', unsafe_allow_html=True)
    
    # Quadrant analysis
    st.subheader("Quadrant Analysis")
    
    # Calculate medians for quadrants
    emissions_median = data['emissions_per_km'].median()
    cost_median = data['cost_per_km'].median()
    
    # Categorize into quadrants
    data['quadrant'] = data.apply(
        lambda row: 'High Emissions, High Cost' if row['emissions_per_km'] > emissions_median and row['cost_per_km'] > cost_median
        else 'High Emissions, Low Cost' if row['emissions_per_km'] > emissions_median and row['cost_per_km'] <= cost_median
        else 'Low Emissions, High Cost' if row['emissions_per_km'] <= emissions_median and row['cost_per_km'] > cost_median
        else 'Low Emissions, Low Cost',
        axis=1
    )
    
    quadrant_summary = data.groupby('quadrant').agg({
        'vehicle_count': 'sum',
        'total_emissions': 'sum',
        'total_cost': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Quadrant Distribution:**")
        fig_quadrant = px.pie(
            quadrant_summary,
            values='vehicle_count',
            names='quadrant',
            title="Vehicle Distribution by Quadrant",
            color_discrete_sequence=['#2E8B57', '#4682B4', '#FF6B6B', '#4ECDC4']
        )
        st.plotly_chart(fig_quadrant, use_container_width=True)
    
    with col2:
        st.markdown("**Quadrant Analysis:**")
        for _, row in quadrant_summary.iterrows():
            if row['quadrant'] == 'High Emissions, High Cost':
                st.error(f"**{row['quadrant']}**: {row['vehicle_count']} vehicles - Priority for replacement")
            elif row['quadrant'] == 'High Emissions, Low Cost':
                st.warning(f"**{row['quadrant']}**: {row['vehicle_count']} vehicles - Consider cost-effective alternatives")
            elif row['quadrant'] == 'Low Emissions, High Cost':
                st.info(f"**{row['quadrant']}**: {row['vehicle_count']} vehicles - Evaluate cost-benefit")
            else:
                st.success(f"**{row['quadrant']}**: {row['vehicle_count']} vehicles - Optimal performance")

def show_carbon_intensive_segments(category: str, year_range: Tuple[int, int], emissions_threshold: float):
    """Identify carbon-intensive segments for decarbonization focus"""
    
    st.markdown('<div class="main-header"><h2>Carbon-Intensive Segments Analysis</h2></div>', unsafe_allow_html=True)
    st.markdown("Identify high-emission segments that should be prioritized for decarbonization")
    
    # Generate data
    data = generate_emissions_cost_data(category, year_range)
    
    # Filter high-emission segments
    high_emission_data = data[data['emissions_per_km'] > emissions_threshold].copy()
    
    if high_emission_data.empty:
        st.success(f"No vehicle types exceed the emissions threshold of {emissions_threshold} kg CO₂e/km")
        return
    
    # Key metrics with gradient cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_high_emission_vehicles = high_emission_data['vehicle_count'].sum()
        st.markdown(f'<div class="metric-card"><h4>High-Emission Vehicles</h4><h2>{total_high_emission_vehicles:,}</h2></div>', unsafe_allow_html=True)
    
    with col2:
        total_high_emission_emissions = high_emission_data['total_emissions'].sum()
        st.markdown(f'<div class="metric-card"><h4>High-Emission CO₂e</h4><h2>{total_high_emission_emissions:,.0f} kg</h2></div>', unsafe_allow_html=True)
    
    with col3:
        avg_high_emission = high_emission_data['emissions_per_km'].mean()
        st.markdown(f'<div class="metric-card"><h4>Avg High-Emission Rate</h4><h2>{avg_high_emission:.3f} kg CO₂e/km</h2></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top carbon-intensive segments
    st.subheader("Top Carbon-Intensive Segments")
    
    # Sort by emissions per km
    top_emitters = high_emission_data.nlargest(10, 'emissions_per_km')
    
    fig = px.bar(
        top_emitters,
        x='vehicle_type',
        y='emissions_per_km',
        color='fuel_type',
        title="Top 10 Carbon-Intensive Vehicle Types",
        labels={'emissions_per_km': 'Emissions (kg CO₂e/km)'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed analysis table
    st.subheader("High-Emission Segment Details")
    
    analysis_data = high_emission_data.copy()
    analysis_data['emissions_contribution'] = (analysis_data['total_emissions'] / analysis_data['total_emissions'].sum()) * 100
    analysis_data['replacement_priority'] = analysis_data['emissions_per_km'].rank(ascending=False)
    
    # Format for display
    display_data = analysis_data[['vehicle_type', 'fuel_type', 'emissions_per_km', 'total_emissions', 
                                 'emissions_contribution', 'vehicle_count', 'replacement_priority']].copy()
    display_data['emissions_per_km'] = display_data['emissions_per_km'].apply(lambda x: f"{x:.3f}")
    display_data['total_emissions'] = display_data['total_emissions'].apply(lambda x: f"{x:,.0f}")
    display_data['emissions_contribution'] = display_data['emissions_contribution'].apply(lambda x: f"{x:.1f}%")
    display_data['replacement_priority'] = display_data['replacement_priority'].apply(lambda x: f"{x:.0f}")
    
    st.dataframe(display_data, use_container_width=True)
    
    # Decarbonization recommendations
    st.subheader("Decarbonization Recommendations")
    
    # Group by vehicle type for recommendations
    vehicle_recommendations = high_emission_data.groupby('vehicle_type').agg({
        'emissions_per_km': 'mean',
        'total_emissions': 'sum',
        'vehicle_count': 'sum'
    }).sort_values('total_emissions', ascending=False)
    
    for vehicle_type, data in vehicle_recommendations.iterrows():
        with st.expander(f"{vehicle_type} - {data['vehicle_count']:.0f} vehicles"):
            st.markdown(f"**Current Emissions**: {data['emissions_per_km']:.3f} kg CO₂e/km")
            st.markdown(f"**Total Impact**: {data['total_emissions']:,.0f} kg CO₂e")
            
            # Generate recommendations based on vehicle type
            if 'truck' in vehicle_type.lower():
                st.markdown("**Recommended Actions:**")
                st.markdown("- Transition to electric or hydrogen fuel cell trucks")
                st.markdown("- Implement route optimization to reduce mileage")
                st.markdown("- Consider rail freight for long-distance transport")
            elif 'bus' in vehicle_type.lower():
                st.markdown("**Recommended Actions:**")
                st.markdown("- Electrify bus fleet with battery electric buses")
                st.markdown("- Implement hydrogen fuel cell buses for longer routes")
                st.markdown("- Optimize bus routes and frequency")
            elif 'car' in vehicle_type.lower():
                st.markdown("**Recommended Actions:**")
                st.markdown("- Accelerate electric vehicle adoption")
                st.markdown("- Implement car-sharing and ride-sharing programs")
                st.markdown("- Improve public transport alternatives")
            else:
                st.markdown("**Recommended Actions:**")
                st.markdown("- Evaluate electric alternatives")
                st.markdown("- Consider operational efficiency improvements")
                st.markdown("- Assess modal shift opportunities")

def show_low_efficiency_analysis(category: str, year_range: Tuple[int, int], cost_threshold: float):
    """Flag low-efficiency, high-cost fuel types for replacement"""
    
    st.markdown('<div class="main-header"><h2>Low-Efficiency, High-Cost Analysis</h2></div>', unsafe_allow_html=True)
    st.markdown("Identify inefficient and expensive fuel types that should be replaced")
    
    # Generate data
    data = generate_emissions_cost_data(category, year_range)
    
    # Filter high-cost segments
    high_cost_data = data[data['cost_per_km'] > cost_threshold].copy()
    
    if high_cost_data.empty:
        st.success(f"No vehicle types exceed the cost threshold of £{cost_threshold}/km")
        return
    
    # Key metrics with gradient cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_high_cost_vehicles = high_cost_data['vehicle_count'].sum()
        st.markdown(f'<div class="metric-card"><h4>High-Cost Vehicles</h4><h2>{total_high_cost_vehicles:,}</h2></div>', unsafe_allow_html=True)
    
    with col2:
        total_high_cost_expense = high_cost_data['total_cost'].sum()
        st.markdown(f'<div class="metric-card"><h4>High-Cost Expense</h4><h2>£{total_high_cost_expense:,.0f}</h2></div>', unsafe_allow_html=True)
    
    with col3:
        avg_high_cost = high_cost_data['cost_per_km'].mean()
        st.markdown(f'<div class="metric-card"><h4>Avg High-Cost Rate</h4><h2>£{avg_high_cost:.3f}/km</h2></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Efficiency analysis
    st.subheader("Cost Efficiency Analysis")
    
    # Calculate efficiency metrics
    data['cost_efficiency'] = 1 / data['cost_per_km']  # Higher is better
    data['emissions_efficiency'] = 1 / data['emissions_per_km']  # Higher is better
    data['overall_efficiency'] = (data['cost_efficiency'] + data['emissions_efficiency']) / 2
    
    # Find least efficient
    least_efficient = data.nsmallest(10, 'overall_efficiency')
    
    fig = px.scatter(
        data,
        x='cost_per_km',
        y='emissions_per_km',
        size='vehicle_count',
        color='overall_efficiency',
        hover_data=['vehicle_type', 'fuel_type'],
        title="Cost vs Emissions Efficiency",
        labels={
            'cost_per_km': 'Cost (£/km)',
            'emissions_per_km': 'Emissions (kg CO₂e/km)',
            'overall_efficiency': 'Overall Efficiency'
        },
        color_continuous_scale='RdYlGn'
    )
    
    # Highlight least efficient
    fig.add_trace(
        go.Scatter(
            x=least_efficient['cost_per_km'],
            y=least_efficient['emissions_per_km'],
            mode='markers',
            marker=dict(size=15, color='#FF6B6B', symbol='x'),
            name='Least Efficient (Top 10)'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top inefficient segments
    st.subheader("Top Inefficient Segments")
    
    fig_inefficient = px.bar(
        least_efficient,
        x='vehicle_type',
        y='cost_per_km',
        color='fuel_type',
        title="Top 10 Most Expensive Vehicle Types",
        labels={'cost_per_km': 'Cost (£/km)'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_inefficient.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_inefficient, use_container_width=True)
    
    # Replacement analysis
    st.subheader("Replacement Analysis")
    
    # Calculate potential savings
    high_cost_data['potential_savings'] = high_cost_data['cost_per_km'] - cost_threshold
    high_cost_data['annual_savings'] = high_cost_data['potential_savings'] * high_cost_data['vehicle_count'] * 15000  # Assume 15k km/year
    
    total_potential_savings = high_cost_data['annual_savings'].sum()
    
    st.info(f"**Total Potential Annual Savings**: £{total_potential_savings:,.0f}")
    
    # Show replacement candidates
    replacement_candidates = high_cost_data.nlargest(10, 'annual_savings')
    
    fig_savings = px.bar(
        replacement_candidates,
        x='vehicle_type',
        y='annual_savings',
        color='fuel_type',
        title="Top 10 Replacement Candidates by Potential Savings",
        labels={'annual_savings': 'Potential Annual Savings (£)'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_savings.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_savings, use_container_width=True)
    
    # Detailed replacement table
    st.subheader("Replacement Candidate Details")
    
    replacement_data = high_cost_data[['vehicle_type', 'fuel_type', 'cost_per_km', 'emissions_per_km', 
                                      'vehicle_count', 'annual_savings']].copy()
    replacement_data['replacement_priority'] = replacement_data['annual_savings'].rank(ascending=False)
    
    # Format for display
    display_data = replacement_data.copy()
    display_data['cost_per_km'] = display_data['cost_per_km'].apply(lambda x: f"£{x:.3f}")
    display_data['emissions_per_km'] = display_data['emissions_per_km'].apply(lambda x: f"{x:.3f}")
    display_data['annual_savings'] = display_data['annual_savings'].apply(lambda x: f"£{x:,.0f}")
    display_data['replacement_priority'] = display_data['replacement_priority'].apply(lambda x: f"{x:.0f}")
    
    st.dataframe(display_data, use_container_width=True)

def generate_emissions_cost_data(category: str, year_range: Tuple[int, int]) -> pd.DataFrame:
    """Generate sample emissions and cost data for analysis"""
    
    # Vehicle types and their characteristics
    vehicle_data = {
        'Petrol Car (Small)': {'emissions': 0.12, 'cost': 0.15, 'category': 'Cars'},
        'Petrol Car (Medium)': {'emissions': 0.15, 'cost': 0.18, 'category': 'Cars'},
        'Petrol Car (Large)': {'emissions': 0.20, 'cost': 0.25, 'category': 'Cars'},
        'Diesel Car (Small)': {'emissions': 0.13, 'cost': 0.14, 'category': 'Cars'},
        'Diesel Car (Medium)': {'emissions': 0.16, 'cost': 0.17, 'category': 'Cars'},
        'Diesel Car (Large)': {'emissions': 0.22, 'cost': 0.23, 'category': 'Cars'},
        'Electric Car (Small)': {'emissions': 0.05, 'cost': 0.08, 'category': 'Cars'},
        'Electric Car (Medium)': {'emissions': 0.06, 'cost': 0.10, 'category': 'Cars'},
        'Electric Car (Large)': {'emissions': 0.08, 'cost': 0.12, 'category': 'Cars'},
        'Hybrid Car (Small)': {'emissions': 0.08, 'cost': 0.12, 'category': 'Cars'},
        'Hybrid Car (Medium)': {'emissions': 0.10, 'cost': 0.15, 'category': 'Cars'},
        'Hybrid Car (Large)': {'emissions': 0.13, 'cost': 0.18, 'category': 'Cars'},
        
        'Diesel Van (Small)': {'emissions': 0.18, 'cost': 0.22, 'category': 'Vans'},
        'Diesel Van (Medium)': {'emissions': 0.25, 'cost': 0.30, 'category': 'Vans'},
        'Diesel Van (Large)': {'emissions': 0.35, 'cost': 0.40, 'category': 'Vans'},
        'Electric Van (Small)': {'emissions': 0.07, 'cost': 0.12, 'category': 'Vans'},
        'Electric Van (Medium)': {'emissions': 0.09, 'cost': 0.15, 'category': 'Vans'},
        'Electric Van (Large)': {'emissions': 0.12, 'cost': 0.18, 'category': 'Vans'},
        
        'Diesel Truck (Rigid)': {'emissions': 0.45, 'cost': 0.55, 'category': 'Trucks'},
        'Diesel Truck (Articulated)': {'emissions': 0.65, 'cost': 0.75, 'category': 'Trucks'},
        'Electric Truck (Rigid)': {'emissions': 0.15, 'cost': 0.25, 'category': 'Trucks'},
        'Electric Truck (Articulated)': {'emissions': 0.22, 'cost': 0.35, 'category': 'Trucks'},
        'Hydrogen Truck (Rigid)': {'emissions': 0.08, 'cost': 0.30, 'category': 'Trucks'},
        'Hydrogen Truck (Articulated)': {'emissions': 0.12, 'cost': 0.45, 'category': 'Trucks'},
        
        'Diesel Bus (Single Deck)': {'emissions': 0.40, 'cost': 0.50, 'category': 'Buses'},
        'Diesel Bus (Double Deck)': {'emissions': 0.55, 'cost': 0.65, 'category': 'Buses'},
        'Electric Bus (Single Deck)': {'emissions': 0.12, 'cost': 0.20, 'category': 'Buses'},
        'Electric Bus (Double Deck)': {'emissions': 0.18, 'cost': 0.28, 'category': 'Buses'},
        'Hydrogen Bus (Single Deck)': {'emissions': 0.06, 'cost': 0.25, 'category': 'Buses'},
        'Hydrogen Bus (Double Deck)': {'emissions': 0.09, 'cost': 0.35, 'category': 'Buses'},
        
        'Petrol Motorcycle (Small)': {'emissions': 0.08, 'cost': 0.10, 'category': 'Motorcycles'},
        'Petrol Motorcycle (Large)': {'emissions': 0.12, 'cost': 0.15, 'category': 'Motorcycles'},
        'Electric Motorcycle (Small)': {'emissions': 0.03, 'cost': 0.06, 'category': 'Motorcycles'},
        'Electric Motorcycle (Large)': {'emissions': 0.05, 'cost': 0.08, 'category': 'Motorcycles'},
    }
    
    # Filter by category if specified
    if category != "All Categories":
        vehicle_data = {k: v for k, v in vehicle_data.items() if v['category'] == category}
    
    # Generate data
    data = []
    for vehicle_type, specs in vehicle_data.items():
        # Extract fuel type from vehicle name
        fuel_type = vehicle_type.split(' ')[0]
        
        # Generate realistic vehicle counts
        vehicle_count = np.random.randint(100, 10000)
        
        # Calculate totals
        total_emissions = specs['emissions'] * vehicle_count * 15000  # Assume 15k km/year
        total_cost = specs['cost'] * vehicle_count * 15000
        
        data.append({
            'vehicle_type': vehicle_type,
            'fuel_type': fuel_type,
            'emissions_per_km': specs['emissions'],
            'cost_per_km': specs['cost'],
            'vehicle_count': vehicle_count,
            'total_emissions': total_emissions,
            'total_cost': total_cost
        })
    
    return pd.DataFrame(data) 