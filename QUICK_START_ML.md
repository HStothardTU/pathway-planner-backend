# Quick Start: ML Implementation
## Getting Started with Fleet Clustering

### 🚀 **Start Here: Implement Fleet Clustering in 2 Hours**

---

## **Step 1: Setup (15 minutes)**

### **1.1 Install Dependencies**
```bash
pip install scikit-learn pandas numpy matplotlib seaborn plotly
```

### **1.2 Create ML Directory**
```bash
mkdir -p app/ml
mkdir -p app/ml/models
mkdir -p app/ml/data
```

### **1.3 Create `app/ml/__init__.py`**
```python
"""
Machine Learning Module for Pathway Planner
"""

from .clustering import FleetClusterer
from .data_preprocessing import DataPreprocessor

__all__ = ['FleetClusterer', 'DataPreprocessor']
```

---

## **Step 2: Data Preprocessing (30 minutes)**

### **2.1 Create `app/ml/data_preprocessing.py`**
```python
"""
Data preprocessing for ML models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder

class DataPreprocessor:
    """Preprocess vehicle and scenario data for ML models"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def prepare_fleet_data(self, scenarios: List[Dict]) -> pd.DataFrame:
        """Prepare fleet data for clustering"""
        
        # Extract vehicle data from scenarios
        fleet_data = []
        
        for scenario in scenarios:
            if 'parameters' in scenario and 'vehicle_types' in scenario['parameters']:
                vehicle_types = scenario['parameters']['vehicle_types']
                
                for vehicle_type in vehicle_types:
                    # Extract vehicle characteristics
                    vehicle_data = {
                        'scenario_id': scenario['id'],
                        'vehicle_type': vehicle_type,
                        'emissions_factor': self._get_emissions_factor(vehicle_type),
                        'fuel_type': self._get_fuel_type(vehicle_type),
                        'vehicle_category': self._get_category(vehicle_type),
                        'technology_readiness': self._get_technology_readiness(vehicle_type),
                        'cost_factor': self._get_cost_factor(vehicle_type),
                        'usage_intensity': self._get_usage_intensity(vehicle_type)
                    }
                    fleet_data.append(vehicle_data)
        
        return pd.DataFrame(fleet_data)
    
    def _get_emissions_factor(self, vehicle_type: str) -> float:
        """Get emissions factor for vehicle type"""
        # Use existing VEHICLE_EMISSIONS data
        from app.api.v1.endpoints import VEHICLE_EMISSIONS
        
        for category, vehicles in VEHICLE_EMISSIONS.items():
            for vehicle, data in vehicles.items():
                if vehicle_type.lower() in vehicle.lower():
                    return data.get('tailpipe', 0.0)
        return 0.2  # Default
    
    def _get_fuel_type(self, vehicle_type: str) -> str:
        """Extract fuel type from vehicle type"""
        vehicle_lower = vehicle_type.lower()
        if 'electric' in vehicle_lower:
            return 'electric'
        elif 'hydrogen' in vehicle_lower:
            return 'hydrogen'
        elif 'hybrid' in vehicle_lower:
            return 'hybrid'
        elif 'diesel' in vehicle_lower:
            return 'diesel'
        elif 'petrol' in vehicle_lower:
            return 'petrol'
        else:
            return 'unknown'
    
    def _get_category(self, vehicle_type: str) -> str:
        """Extract vehicle category"""
        vehicle_lower = vehicle_type.lower()
        if 'car' in vehicle_lower:
            return 'passenger'
        elif 'bus' in vehicle_lower:
            return 'public_transport'
        elif 'hgv' in vehicle_lower or 'lorry' in vehicle_lower:
            return 'freight'
        elif 'van' in vehicle_lower:
            return 'light_commercial'
        else:
            return 'other'
    
    def _get_technology_readiness(self, vehicle_type: str) -> int:
        """Get technology readiness level (1-9)"""
        vehicle_lower = vehicle_type.lower()
        if 'electric' in vehicle_lower:
            return 8
        elif 'hydrogen' in vehicle_lower:
            return 6
        elif 'hybrid' in vehicle_lower:
            return 9
        else:
            return 9  # Conventional vehicles
    
    def _get_cost_factor(self, vehicle_type: str) -> float:
        """Get relative cost factor"""
        vehicle_lower = vehicle_type.lower()
        if 'electric' in vehicle_lower:
            return 1.3
        elif 'hydrogen' in vehicle_lower:
            return 1.8
        elif 'hybrid' in vehicle_lower:
            return 1.2
        else:
            return 1.0
    
    def _get_usage_intensity(self, vehicle_type: str) -> float:
        """Get usage intensity factor"""
        vehicle_lower = vehicle_type.lower()
        if 'bus' in vehicle_lower:
            return 0.8
        elif 'hgv' in vehicle_lower:
            return 0.9
        elif 'car' in vehicle_lower:
            return 0.3
        else:
            return 0.5
    
    def encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        categorical_cols = ['fuel_type', 'vehicle_category']
        
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        return df
    
    def scale_features(self, df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
        """Scale numerical features"""
        df_scaled = df.copy()
        df_scaled[feature_cols] = self.scaler.fit_transform(df[feature_cols])
        return df_scaled
```

---

## **Step 3: Fleet Clustering (45 minutes)**

### **3.1 Create `app/ml/clustering.py`**
```python
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
```

---

## **Step 4: API Integration (30 minutes)**

### **4.1 Add to `app/api/v1/schemas.py`**
```python
# Add these schemas to the existing file

class ClusteringRequest(BaseModel):
    method: str = Field(..., description="Clustering method: 'kmeans', 'dbscan', 'hierarchical'")
    n_clusters: Optional[int] = Field(4, description="Number of clusters for K-Means")
    eps: Optional[float] = Field(0.5, description="Epsilon for DBSCAN")
    min_samples: Optional[int] = Field(5, description="Min samples for DBSCAN")

class ClusteringResult(BaseModel):
    clusters: List[int]
    cluster_labels: List[str]
    silhouette_score: Optional[float]
    calinski_score: Optional[float]
    cluster_analysis: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    visualization_data: Dict[str, Any]
```

### **4.2 Add to `app/api/v1/endpoints.py`**
```python
# Add these imports at the top
from app.ml.clustering import FleetClusterer
from app.ml.data_preprocessing import DataPreprocessor
from .schemas import ClusteringRequest, ClusteringResult

# Add this endpoint
@router.post("/ml/cluster-fleets", response_model=ClusteringResult)
def cluster_fleets(request: ClusteringRequest, db: Session = Depends(get_db)):
    """Cluster vehicle fleets based on characteristics"""
    
    try:
        # Get all scenarios
        scenarios = db.query(Scenario).all()
        scenarios_data = [scenario.__dict__ for scenario in scenarios]
        
        # Preprocess data
        preprocessor = DataPreprocessor()
        fleet_data = preprocessor.prepare_fleet_data(scenarios_data)
        fleet_data = preprocessor.encode_categorical_features(fleet_data)
        
        # Cluster fleets
        clusterer = FleetClusterer()
        
        if request.method == 'kmeans':
            results = clusterer.cluster_fleets_kmeans(fleet_data, request.n_clusters)
        elif request.method == 'dbscan':
            results = clusterer.cluster_fleets_dbscan(fleet_data, request.eps, request.min_samples)
        else:
            raise HTTPException(status_code=400, detail="Unsupported clustering method")
        
        # Generate recommendations
        recommendations = clusterer.get_cluster_recommendations(results['cluster_analysis'])
        
        # Prepare visualization data
        viz_data = {
            'x': results['pca_components'][:, 0].tolist(),
            'y': results['pca_components'][:, 1].tolist(),
            'clusters': results['clusters'].tolist(),
            'labels': results['cluster_labels']
        }
        
        return ClusteringResult(
            clusters=results['clusters'].tolist(),
            cluster_labels=results['cluster_labels'],
            silhouette_score=results.get('silhouette_score'),
            calinski_score=results.get('calinski_score'),
            cluster_analysis=results['cluster_analysis'],
            recommendations=recommendations,
            visualization_data=viz_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")
```

---

## **Step 5: Frontend Integration (30 minutes)**

### **5.1 Create `pathway-planner-frontend/pages/ai_insights.py`**
```python
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
```

### **5.2 Update `pathway-planner-frontend/app.py`**
```python
# Add to the navigation options
page = st.sidebar.radio(
    "Navigation",
    (
        "Dashboard",
        "Scenario Builder",
        "Parameter Editor",
        "Visualize Pathways",
        "Uncertainty Explorer",
        "Reports & Export",
        "Advanced Calculator",
        "Analysis & Insights",
        "AI Insights"  # Add this line
    )
)

# Add to the routing
elif page == "AI Insights":
    from pages import ai_insights
    ai_insights.show()
```

---

## **🎯 What You'll Have After 2 Hours**

### **✅ Core ML Capability**
- **Fleet Clustering**: Groups vehicles by emissions, cost, and technology characteristics
- **Interactive Visualization**: PCA-based cluster visualization
- **Strategic Recommendations**: AI-generated recommendations for each cluster
- **Quality Metrics**: Silhouette and Calinski-Harabasz scores

### **✅ User Interface**
- **AI Insights Dashboard**: Professional gradient design
- **Interactive Controls**: Method selection and parameter tuning
- **Cluster Analysis**: Detailed breakdown of each cluster
- **Recommendations**: Actionable insights for decarbonization

### **✅ API Integration**
- **RESTful Endpoint**: `/api/v1/ml/cluster-fleets`
- **Multiple Algorithms**: K-Means, DBSCAN support
- **Structured Response**: Comprehensive clustering results
- **Error Handling**: Robust error management

---

## **🚀 Next Steps**

### **Immediate (Same Day)**
1. **Test the clustering** with your existing scenarios
2. **Tune parameters** for better results
3. **Add more vehicle data** for richer analysis

### **This Week**
1. **Implement anomaly detection**
2. **Add pattern detection**
3. **Create regression models**
4. **Build comprehensive AI dashboard**

---

*This quick start guide gets you from zero to a working ML system in 2 hours. The fleet clustering provides immediate value and serves as a foundation for more advanced AI capabilities.* 