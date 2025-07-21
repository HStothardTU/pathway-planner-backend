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