from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime

class ScenarioCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Scenario name")
    description: Optional[str] = Field(None, max_length=500, description="Scenario description")
    parameters: Dict[str, Any] = Field(..., description="Scenario parameters")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Scenario name cannot be empty')
        return v.strip()
    
    @validator('parameters')
    def validate_parameters(cls, v):
        required_keys = ['years', 'target_emissions_reduction', 'max_annual_change', 'vehicle_types']
        for key in required_keys:
            if key not in v:
                raise ValueError(f'Missing required parameter: {key}')
        
        # Validate years
        years = v.get('years', [])
        if len(years) < 2:
            raise ValueError('At least 2 years must be specified')
        if len(years) > 10:
            raise ValueError('Maximum 10 years allowed')
        
        # Validate target reduction
        target = v.get('target_emissions_reduction', 0)
        if not 0 <= target <= 1:
            raise ValueError('Target emissions reduction must be between 0 and 1')
        
        # Validate max annual change
        max_change = v.get('max_annual_change', 0)
        if not 0.05 <= max_change <= 0.3:
            raise ValueError('Maximum annual change must be between 0.05 and 0.3')
        
        # Validate vehicle types
        vehicle_types = v.get('vehicle_types', [])
        if not vehicle_types:
            raise ValueError('At least one vehicle type must be specified')
        if len(vehicle_types) > 10:
            raise ValueError('Maximum 10 vehicle types allowed')
        
        return v

class ScenarioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Scenario name")
    description: Optional[str] = Field(None, max_length=500, description="Scenario description")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Scenario parameters")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Scenario name cannot be empty')
        return v.strip() if v else v

class ScenarioRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OptimizationRequest(BaseModel):
    scenario_id: int = Field(..., description="ID of the scenario to optimize")
    include_usage_patterns: bool = Field(True, description="Include vehicle usage patterns in calculations")
    enable_constraints: bool = Field(True, description="Enable realistic technology adoption constraints")
    custom_parameters: Optional[Dict[str, Any]] = Field(None, description="Override scenario parameters")

class OptimizationResponse(BaseModel):
    scenario_id: int
    success: bool
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    computation_time: Optional[float] = None

class VehicleTypeInfo(BaseModel):
    category: str
    vehicle_types: List[str]
    emissions_factors: Dict[str, Dict[str, float]]
    usage_patterns: Optional[Dict[str, int]] = None

class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []

class ExportRequest(BaseModel):
    scenario_id: int
    format: str = Field(..., pattern="^(csv|pdf|excel)$")
    include_charts: bool = True
    include_summary: bool = True
    custom_title: Optional[str] = None

# Advanced Calculation Engine Schemas (Week 3-4)

class AdvancedScenarioRequest(BaseModel):
    scenario_id: str
    years: List[int] = Field(..., min_items=2, description="Years to analyze")
    vehicle_types: List[str] = Field(..., min_items=1, description="Vehicle types to include")
    target_reduction: float = Field(..., ge=0, le=1, description="Target emissions reduction (0-1)")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Constraint definitions")
    adoption_rates: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Adoption rates by vehicle type")
    calculation_types: List[str] = Field(default=["emissions", "cost", "energy"], description="Types of calculations to perform")
    aggregation_levels: List[str] = Field(default=["vehicle", "vehicle_type", "total"], description="Aggregation levels")
    real_time_updates: bool = True
    store_results: bool = True

class ConstraintAnalysisRequest(BaseModel):
    scenario_data: Dict[str, Any] = Field(..., description="Scenario data to analyze")
    constraints: Dict[str, Any] = Field(..., description="Constraints to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")

class PerformanceMetricsRequest(BaseModel):
    include_cache_metrics: bool = True
    include_memory_metrics: bool = True
    include_calculation_metrics: bool = True
    include_real_time_metrics: bool = True

class ScenarioComparisonRequest(BaseModel):
    scenario_ids: List[str] = Field(..., min_items=2, description="Scenario IDs to compare")
    metrics: List[str] = Field(default=["total_emissions", "total_cost"], description="Metrics to compare")

class AdvancedCalculationResult(BaseModel):
    scenario_id: str
    calculation_timestamp: str
    success: bool
    summary: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    constraint_analysis: Dict[str, Any]
    per_vehicle_results: Optional[Dict[str, Any]] = None
    per_year_results: Optional[Dict[str, Any]] = None
    aggregated_results: Optional[Dict[str, Any]] = None

class RealTimeUpdate(BaseModel):
    scenario_id: str
    timestamp: str
    year: int
    progress: float
    metrics: Dict[str, Any]

class ConstraintViolation(BaseModel):
    year: int
    vehicle_type: str
    constraint_type: str
    violation_description: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")

class AggregationResult(BaseModel):
    scenario_id: str
    aggregation_level: str
    calculation_type: str
    results: Dict[str, Any]

# ML Schemas
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