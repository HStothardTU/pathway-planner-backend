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
    
    # Fleet Clustering Section
    st.subheader("Fleet Clustering Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Clustering method selection
        method = st.selectbox(
            "Clustering Method",
            ["kmeans", "dbscan", "hierarchical"],
            help="Choose clustering algorithm"
        )
        
        # Parameters based on method
        if method == "kmeans":
            n_clusters = st.slider("Number of Clusters", 2, 8, 4)
            params = {"method": method, "n_clusters": n_clusters}
        elif method == "dbscan":
            eps = st.slider("Epsilon", 0.1, 2.0, 0.5, 0.1)
            min_samples = st.slider("Min Samples", 2, 10, 5)
            params = {"method": method, "eps": eps, "min_samples": min_samples}
        else:
            params = {"method": method}
    
    with col2:
        if st.button("Run Clustering", type="primary"):
            with st.spinner("Analyzing fleet data..."):
                try:
                    response = requests.post(f"{API_BASE}/ml/cluster-fleets", json=params)
                    if response.status_code == 200:
                        results = response.json()
                        st.session_state['clustering_results'] = results
                        st.success("Clustering completed!")
                    else:
                        st.error(f"Clustering failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Display results
    if 'clustering_results' in st.session_state:
        results = st.session_state['clustering_results']
        
        # Visualization
        st.subheader("Fleet Clusters Visualization")
        
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
        st.subheader("Cluster Analysis")
        
        for cluster_id, analysis in results['cluster_analysis'].items():
            with st.expander(f"Cluster {cluster_id.replace('cluster_', '')} Analysis"):
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
        st.subheader("Strategic Recommendations")
        
        for rec in results['recommendations']:
            with st.expander(f"{rec['cluster_id'].replace('cluster_', 'Cluster ')} - {rec['focus_area']}"):
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

if __name__ == "__main__":
    show() 