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
        
        # If no scenarios with vehicle data, create demo data
        if not fleet_data:
            demo_vehicles = [
                "Petrol Car (Medium)",
                "Diesel Car (Medium)", 
                "Electric Car (Medium)",
                "Hybrid Car (Full Petrol)",
                "Diesel Bus (Single Deck)",
                "Electric Bus (Single Deck)",
                "Diesel Rigid HGV (7.5-17t)",
                "Battery Electric HGV (Rigid 7.5-17t)",
                "Diesel Van (Medium)",
                "Electric Van (BEV)"
            ]
            
            for i, vehicle_type in enumerate(demo_vehicles):
                vehicle_data = {
                    'scenario_id': i + 1,
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