"""
Fleet clustering algorithms
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import plotly.express as px
import plotly.graph_objects as go

class FleetClusterer:
    """Cluster vehicle fleets based on characteristics"""
    
    def __init__(self):
        self.kmeans_model = None
        self.dbscan_model = None
        self.hierarchical_model = None
        self.pca_model = None
        self.feature_columns = [
            'emissions_factor', 'technology_readiness', 
            'cost_factor', 'usage_intensity',
            'fuel_type_encoded', 'vehicle_category_encoded'
        ]
    
    def cluster_fleets_kmeans(self, df: pd.DataFrame, n_clusters: int = 4) -> Dict[str, Any]:
        """Cluster fleets using K-Means"""
        
        # Prepare features
        X = df[self.feature_columns].fillna(0)
        
        # Apply PCA for visualization
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        
        # Fit K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)
        
        # Calculate metrics
        silhouette_avg = silhouette_score(X, clusters)
        calinski_avg = calinski_harabasz_score(X, clusters)
        
        # Create results
        results = {
            'clusters': clusters,
            'cluster_centers': kmeans.cluster_centers_,
            'pca_components': X_pca,
            'silhouette_score': silhouette_avg,
            'calinski_score': calinski_avg,
            'cluster_labels': [f'Cluster {i+1}' for i in clusters],
            'model': kmeans,
            'pca_model': pca
        }
        
        # Add cluster analysis
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = clusters
        df_with_clusters['cluster_label'] = results['cluster_labels']
        
        results['cluster_analysis'] = self._analyze_clusters(df_with_clusters)
        
        return results
    
    def cluster_fleets_dbscan(self, df: pd.DataFrame, eps: float = 0.5, min_samples: int = 5) -> Dict[str, Any]:
        """Cluster fleets using DBSCAN"""
        
        X = df[self.feature_columns].fillna(0)
        
        # Apply PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        
        # Fit DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = dbscan.fit_predict(X)
        
        # Handle noise points
        n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
        
        results = {
            'clusters': clusters,
            'pca_components': X_pca,
            'n_clusters': n_clusters,
            'noise_points': np.sum(clusters == -1),
            'cluster_labels': [f'Cluster {i+1}' if i != -1 else 'Noise' for i in clusters],
            'model': dbscan,
            'pca_model': pca
        }
        
        # Add cluster analysis
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = clusters
        df_with_clusters['cluster_label'] = results['cluster_labels']
        
        results['cluster_analysis'] = self._analyze_clusters(df_with_clusters)
        
        return results
    
    def _analyze_clusters(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze cluster characteristics"""
        
        analysis = {}
        
        for cluster_id in df['cluster'].unique():
            if cluster_id == -1:  # Noise points
                continue
                
            cluster_data = df[df['cluster'] == cluster_id]
            
            analysis[f'cluster_{cluster_id}'] = {
                'size': len(cluster_data),
                'avg_emissions': cluster_data['emissions_factor'].mean(),
                'avg_cost': cluster_data['cost_factor'].mean(),
                'avg_technology_readiness': cluster_data['technology_readiness'].mean(),
                'fuel_type_distribution': cluster_data['fuel_type'].value_counts().to_dict(),
                'vehicle_category_distribution': cluster_data['vehicle_category'].value_counts().to_dict(),
                'representative_vehicles': cluster_data['vehicle_type'].head(3).tolist()
            }
        
        return analysis
    
    def create_clustering_visualization(self, results: Dict[str, Any], title: str = "Fleet Clustering") -> go.Figure:
        """Create interactive clustering visualization"""
        
        # Create scatter plot
        fig = go.Figure()
        
        # Add scatter points
        fig.add_trace(go.Scatter(
            x=results['pca_components'][:, 0],
            y=results['pca_components'][:, 1],
            mode='markers',
            marker=dict(
                color=results['clusters'],
                colorscale='Viridis',
                size=8,
                opacity=0.7
            ),
            text=results['cluster_labels'],
            hovertemplate='<b>%{text}</b><br>' +
                         'PCA1: %{x:.2f}<br>' +
                         'PCA2: %{y:.2f}<br>' +
                         '<extra></extra>',
            name='Fleet Clusters'
        ))
        
        # Add cluster centers if available
        if 'cluster_centers' in results:
            centers_pca = results['pca_model'].transform(results['cluster_centers'])
            fig.add_trace(go.Scatter(
                x=centers_pca[:, 0],
                y=centers_pca[:, 1],
                mode='markers',
                marker=dict(
                    color='red',
                    size=15,
                    symbol='x'
                ),
                name='Cluster Centers'
            ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title='Principal Component 1',
            yaxis_title='Principal Component 2',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def get_cluster_recommendations(self, cluster_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on cluster analysis"""
        
        recommendations = []
        
        for cluster_id, analysis in cluster_analysis.items():
            if cluster_id == 'cluster_-1':  # Skip noise
                continue
                
            rec = {
                'cluster_id': cluster_id,
                'priority': 'high' if analysis['avg_emissions'] > 0.3 else 'medium',
                'focus_area': self._determine_focus_area(analysis),
                'recommended_actions': self._generate_actions(analysis),
                'potential_impact': self._estimate_impact(analysis)
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _determine_focus_area(self, analysis: Dict[str, Any]) -> str:
        """Determine focus area for cluster"""
        if analysis['avg_emissions'] > 0.3:
            return 'High Emissions Reduction'
        elif analysis['avg_cost'] > 1.5:
            return 'Cost Optimization'
        elif analysis['avg_technology_readiness'] < 7:
            return 'Technology Development'
        else:
            return 'Operational Efficiency'
    
    def _generate_actions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommended actions"""
        actions = []
        
        if analysis['avg_emissions'] > 0.3:
            actions.append('Prioritize electrification for high-emission vehicles')
            actions.append('Implement emission reduction technologies')
        
        if analysis['avg_cost'] > 1.5:
            actions.append('Explore cost-effective alternative fuels')
            actions.append('Optimize fleet utilization')
        
        if analysis['avg_technology_readiness'] < 7:
            actions.append('Invest in technology development')
            actions.append('Pilot new technologies')
        
        return actions
    
    def _estimate_impact(self, analysis: Dict[str, Any]) -> str:
        """Estimate potential impact"""
        if analysis['avg_emissions'] > 0.3:
            return 'High emissions reduction potential'
        elif analysis['size'] > 100:
            return 'Large fleet impact'
        else:
            return 'Moderate impact' 