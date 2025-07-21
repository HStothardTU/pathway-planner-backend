"""
AI Insights Dashboard
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

API_BASE = "http://localhost:8000/api/v1"

def show():
    """Display AI insights dashboard"""
    
    # Main header with gradient design
    st.markdown('<div class="main-header"><h1>AI Insights</h1><h3>Machine learning analysis for transport decarbonization</h3></div>', unsafe_allow_html=True)
    
    # Explanation Section
    with st.expander("📚 Understanding Fleet Clustering Analysis", expanded=True):
        st.markdown("""
        ### What is Fleet Clustering?
        Fleet clustering uses **machine learning algorithms** to automatically group vehicles based on their characteristics, 
        helping identify patterns and opportunities for targeted decarbonization strategies.
        
        ### What Data Are We Analyzing?
        Our AI analyzes each vehicle across **6 key dimensions**:
        - **Emissions Factor** (kg CO₂e/km): Environmental impact
        - **Technology Readiness** (1-9 scale): Maturity of vehicle technology
        - **Cost Factor**: Relative cost compared to conventional vehicles
        - **Usage Intensity**: How frequently the vehicle type is used
        - **Fuel Type**: Petrol, diesel, electric, hydrogen, hybrid
        - **Vehicle Category**: Passenger, freight, public transport, etc.
        
        ### Clustering Methods Explained:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔵 K-Means Clustering**
            - **How it works**: Groups vehicles into a fixed number of clusters based on similarity
            - **Best for**: When you know how many groups you want to analyze
            - **Parameters**:
              - **Number of Clusters**: How many groups to create (2-8 recommended)
            - **Use case**: Strategic planning with predefined categories
            """)
            
            st.markdown("""
            **🟢 DBSCAN Clustering**
            - **How it works**: Discovers clusters of varying shapes and sizes automatically
            - **Best for**: Finding natural groupings without assuming cluster count
            - **Parameters**:
              - **Epsilon**: Maximum distance between points in a cluster (0.1-2.0)
              - **Min Samples**: Minimum points needed to form a cluster (2-10)
            - **Use case**: Discovering unexpected patterns in fleet composition
            """)
        
        with col2:
            st.markdown("""
            **🟡 Hierarchical Clustering**
            - **How it works**: Creates a tree-like structure of nested clusters
            - **Best for**: Understanding relationships between different vehicle groups
            - **Parameters**: Automatically determined based on data structure
            - **Use case**: Detailed analysis of fleet hierarchy and relationships
            """)
            
            st.markdown("""
            **📊 Quality Metrics**
            - **Silhouette Score** (0-1): How well-separated clusters are (higher = better)
            - **Calinski-Harabasz Score**: Ratio of between-cluster to within-cluster variance
            - **Cluster Size**: Number of vehicles in each group
            - **Representative Vehicles**: Typical examples from each cluster
            """)
        
        st.markdown("""
        ### How to Use This Analysis:
        1. **Choose a clustering method** based on your analysis goals
        2. **Adjust parameters** to fine-tune the grouping
        3. **Run clustering** to see how vehicles are grouped
        4. **Review cluster analysis** to understand each group's characteristics
        5. **Follow recommendations** for targeted decarbonization strategies
        
        ### Strategic Value:
        - **Identify high-emission clusters** for immediate action
        - **Discover cost-effective opportunities** for fleet electrification
        - **Prioritize technology investments** based on readiness levels
        - **Optimize policy interventions** for maximum impact
        """)
    
    # Fleet Clustering Section
    st.subheader("Fleet Clustering Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Clustering method selection
        method = st.selectbox(
            "Clustering Method",
            ["kmeans", "dbscan", "hierarchical"],
            help="Choose clustering algorithm",
            index=0
        )
        
        # Parameters based on method
        if method == "kmeans":
            st.markdown("**K-Means Parameters:**")
            n_clusters = st.slider(
                "Number of Clusters", 
                2, 8, 4,
                help="How many groups to create. More clusters = more detailed analysis but may be harder to interpret."
            )
            params = {"method": method, "n_clusters": n_clusters}
            
        elif method == "dbscan":
            st.markdown("**DBSCAN Parameters:**")
            eps = st.slider(
                "Epsilon (Distance Threshold)", 
                0.1, 2.0, 0.5, 0.1,
                help="Maximum distance between points to be considered neighbors. Lower = stricter clustering."
            )
            min_samples = st.slider(
                "Minimum Samples per Cluster", 
                2, 10, 5,
                help="Minimum number of vehicles needed to form a cluster. Higher = more robust clusters."
            )
            params = {"method": method, "eps": eps, "min_samples": min_samples}
            
        else:  # hierarchical
            st.markdown("**Hierarchical Clustering:**")
            st.info("Parameters are automatically optimized based on the data structure.")
            params = {"method": method}
    
    with col2:
        # Data overview
        st.markdown("**📊 Current Data:**")
        try:
            response = requests.get(f"{API_BASE}/scenarios/")
            if response.status_code == 200:
                scenarios = response.json()
                if scenarios:
                    st.success(f"✅ Analyzing {len(scenarios)} scenarios")
                    vehicle_count = sum(len(s.get('parameters', {}).get('vehicle_types', [])) for s in scenarios)
                    st.info(f"📈 {vehicle_count} vehicle types across all scenarios")
                else:
                    st.info("📈 Using demo vehicle data (10 vehicle types)")
            else:
                st.info("📈 Using demo vehicle data (10 vehicle types)")
        except:
            st.info("📈 Using demo vehicle data (10 vehicle types)")
        
        st.markdown("---")
        
        if st.button("🚀 Run Clustering Analysis", type="primary"):
            with st.spinner("🤖 AI is analyzing your fleet data..."):
                try:
                    response = requests.post(f"{API_BASE}/ml/cluster-fleets", json=params)
                    if response.status_code == 200:
                        results = response.json()
                        st.session_state['clustering_results'] = results
                        st.success("✅ Clustering completed successfully!")
                    else:
                        st.error(f"❌ Clustering failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display results
    if 'clustering_results' in st.session_state:
        results = st.session_state['clustering_results']
        
        # Results summary
        st.markdown("---")
        st.subheader("🎯 Clustering Results Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            n_clusters = len(set(results['clusters']))
            st.metric("Clusters Found", n_clusters)
        with col2:
            if results.get('silhouette_score'):
                st.metric("Clustering Quality", f"{results['silhouette_score']:.3f}", 
                         help="Silhouette Score: 0-1 scale, higher = better separation")
        with col3:
            if results.get('calinski_score'):
                st.metric("Cluster Separation", f"{results['calinski_score']:.1f}",
                         help="Calinski-Harabasz Score: Higher = better cluster separation")
        
        # Visualization
        st.subheader("📊 Fleet Clusters Visualization")
        st.markdown("""
        **Understanding the Plot:**
        - Each point represents a vehicle type
        - Points are positioned using PCA (Principal Component Analysis) for 2D visualization
        - Colors indicate cluster membership
        - Closer points = more similar vehicles
        """)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=results['visualization_data']['x'],
            y=results['visualization_data']['y'],
            mode='markers',
            marker=dict(
                color=results['visualization_data']['clusters'],
                colorscale='Viridis',
                size=8,
                opacity=0.7
            ),
            text=results['visualization_data']['labels'],
            hovertemplate='<b>%{text}</b><br>' +
                         'PCA1: %{x:.2f}<br>' +
                         'PCA2: %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title="Fleet Clusters (PCA Visualization)",
            xaxis_title="Principal Component 1",
            yaxis_title="Principal Component 2",
            template='plotly_white',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Cluster Analysis
        st.subheader("🔍 Detailed Cluster Analysis")
        st.markdown("""
        **What Each Cluster Tells Us:**
        - **Size**: How many vehicle types are in this group
        - **Avg Emissions**: Environmental impact of this cluster
        - **Avg Cost Factor**: Relative cost compared to conventional vehicles
        - **Technology Readiness**: Maturity level of technologies in this cluster
        - **Fuel Types**: Distribution of fuel technologies
        - **Representative Vehicles**: Typical examples from this cluster
        """)
        
        for cluster_id, analysis in results['cluster_analysis'].items():
            cluster_num = cluster_id.replace('cluster_', '')
            with st.expander(f"🔵 Cluster {cluster_num} - {analysis['representative_vehicles'][0] if analysis['representative_vehicles'] else 'Analysis'}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Size", analysis['size'])
                    st.metric("Avg Emissions", f"{analysis['avg_emissions']:.3f}")
                    st.metric("Avg Cost Factor", f"{analysis['avg_cost']:.2f}")
                
                with col2:
                    st.metric("Technology Readiness", f"{analysis['avg_technology_readiness']:.1f}")
                    st.write("**Fuel Types:**")
                    for fuel, count in analysis['fuel_type_distribution'].items():
                        st.write(f"- {fuel}: {count}")
                
                st.write("**Representative Vehicles:**")
                for vehicle in analysis['representative_vehicles']:
                    st.write(f"- {vehicle}")
        
        # Recommendations
        st.subheader("💡 Strategic Recommendations")
        st.markdown("""
        **How to Use These Recommendations:**
        - **Priority**: High priority clusters need immediate attention
        - **Focus Area**: The main strategic direction for this cluster
        - **Recommended Actions**: Specific steps to take
        - **Potential Impact**: Expected outcomes of following these recommendations
        """)
        
        for rec in results['recommendations']:
            cluster_num = rec['cluster_id'].replace('cluster_', '')
            priority_color = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            
            with st.expander(f"{priority_color} Cluster {cluster_num} - {rec['focus_area']}"):
                st.write(f"**Priority:** {rec['priority'].title()}")
                st.write(f"**Potential Impact:** {rec['potential_impact']}")
                st.write("**Recommended Actions:**")
                for action in rec['recommended_actions']:
                    st.write(f"- {action}")
        
        # Metrics
        if results.get('silhouette_score'):
            st.metric("Clustering Quality (Silhouette)", f"{results['silhouette_score']:.3f}")
        if results.get('calinski_score'):
            st.metric("Clustering Quality (Calinski-Harabasz)", f"{results['calinski_score']:.1f}")
        
        # Next steps
        st.markdown("---")
        st.subheader("🚀 Next Steps")
        st.markdown("""
        **What You Can Do Next:**
        1. **Try different clustering methods** to see different perspectives
        2. **Adjust parameters** to fine-tune the analysis
        3. **Create scenarios** in Scenario Builder to analyze your own fleet data
        4. **Export results** for stakeholder presentations
        5. **Use recommendations** to inform decarbonization strategies
        
        **Coming Soon:**
        - Anomaly detection for data quality
        - Regression models for emissions forecasting
        - Policy impact analysis
        - Advanced visualization options
        """)

if __name__ == "__main__":
    show() 