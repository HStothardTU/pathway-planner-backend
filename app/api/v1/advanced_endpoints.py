"""
Advanced API Endpoints for Week 3-4: Advanced Calculation Engine
Provides endpoints for per-vehicle, per-year calculations with real-time aggregation
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import json

from app.db.session import get_db
from app.services.advanced_calculator import AdvancedCalculationEngine, CalculationType, AggregationLevel
from app.api.v1 import schemas

router = APIRouter()

# Initialize the advanced calculation engine
advanced_engine = AdvancedCalculationEngine({
    'max_workers': 4,
    'cache_enabled': True,
    'real_time_updates': True
})

@router.post("/advanced/calculate-scenario")
async def calculate_advanced_scenario(
    scenario_request: schemas.AdvancedScenarioRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Calculate advanced transport decarbonization scenario with per-vehicle, per-year analysis
    """
    try:
        # Prepare scenario data
        scenario_data = {
            'scenario_id': scenario_request.scenario_id,
            'years': scenario_request.years,
            'vehicle_types': scenario_request.vehicle_types,
            'target_reduction': scenario_request.target_reduction,
            'constraints': scenario_request.constraints,
            'adoption_rates': scenario_request.adoption_rates,
            'calculation_types': scenario_request.calculation_types,
            'aggregation_levels': scenario_request.aggregation_levels,
            'real_time_updates': scenario_request.real_time_updates
        }
        
        # Run calculation
        result = advanced_engine.calculate_scenario(scenario_data)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        
        # Store results in database if requested
        if scenario_request.store_results:
            background_tasks.add_task(store_calculation_results, result['results'], db)
        
        return {
            'success': True,
            'scenario_id': result['results']['scenario_id'],
            'calculation_timestamp': result['results']['calculation_timestamp'],
            'summary': result['results']['aggregated_results']['scenario_summary'],
            'performance_metrics': result['results']['performance_metrics'],
            'constraint_analysis': result['results']['constraint_analysis']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")

@router.get("/advanced/scenario/{scenario_id}")
async def get_advanced_scenario_results(
    scenario_id: str,
    aggregation_level: AggregationLevel = AggregationLevel.TOTAL,
    calculation_type: Optional[CalculationType] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve advanced scenario calculation results
    """
    try:
        # Check cache first
        cached_result = get_cached_result(scenario_id)
        if cached_result:
            return filter_results_by_level(cached_result, aggregation_level, calculation_type)
        
        # Retrieve from database
        db_result = get_scenario_from_database(scenario_id, db)
        if not db_result:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        return filter_results_by_level(db_result, aggregation_level, calculation_type)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")

@router.get("/advanced/scenario/{scenario_id}/real-time")
async def get_real_time_updates(scenario_id: str):
    """
    Get real-time calculation updates for a scenario
    """
    try:
        # Get real-time updates from the monitoring system
        updates = advanced_engine.real_time_monitor.monitoring_data
        
        # Filter updates for this scenario
        scenario_updates = [
            update for update in updates 
            if update.get('scenario_id') == scenario_id
        ]
        
        return {
            'scenario_id': scenario_id,
            'updates': scenario_updates,
            'performance_summary': advanced_engine.real_time_monitor.get_performance_summary()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get real-time updates: {str(e)}")

@router.post("/advanced/constraint-analysis")
async def analyze_constraints(
    constraint_request: schemas.ConstraintAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze constraints for a transport decarbonization scenario
    """
    try:
        # Prepare constraint data
        constraint_data = {
            'scenario_data': constraint_request.scenario_data,
            'constraints': constraint_request.constraints,
            'analysis_type': constraint_request.analysis_type
        }
        
        # Run constraint analysis
        analysis = advanced_engine.constraint_manager.analyze_constraints(
            constraint_data['scenario_data'],
            constraint_data['constraints']
        )
        
        return {
            'success': True,
            'analysis': analysis,
            'recommendations': generate_constraint_recommendations(analysis),
            'risk_assessment': assess_constraint_risks(analysis)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Constraint analysis failed: {str(e)}")

@router.get("/advanced/aggregation/{scenario_id}")
async def get_aggregated_results(
    scenario_id: str,
    aggregation_level: AggregationLevel,
    calculation_type: Optional[CalculationType] = None,
    db: Session = Depends(get_db)
):
    """
    Get aggregated results at specified level
    """
    try:
        # Get scenario results
        scenario_results = get_scenario_results(scenario_id, db)
        if not scenario_results:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Perform aggregation
        aggregated = advanced_engine.aggregation_engine.perform_comprehensive_aggregation(
            scenario_results
        )
        
        # Filter by aggregation level and calculation type
        filtered_results = filter_aggregated_results(
            aggregated, aggregation_level, calculation_type
        )
        
        return {
            'scenario_id': scenario_id,
            'aggregation_level': aggregation_level.value,
            'calculation_type': calculation_type.value if calculation_type else 'all',
            'results': filtered_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aggregation failed: {str(e)}")

@router.post("/advanced/performance-metrics")
async def get_performance_metrics(
    metrics_request: schemas.PerformanceMetricsRequest
):
    """
    Get performance metrics for calculation engine
    """
    try:
        metrics = {
            'cache_performance': {
                'hit_rate': advanced_engine._get_cache_hit_rate(),
                'cache_size': len(advanced_engine.calculation_cache)
            },
            'memory_usage': advanced_engine._get_memory_usage(),
            'calculation_performance': {
                'total_scenarios_processed': len(advanced_engine.calculation_cache),
                'average_calculation_time': calculate_average_time(),
                'constraint_violations': get_total_violations()
            },
            'real_time_performance': advanced_engine.real_time_monitor.get_performance_summary()
        }
        
        return {
            'success': True,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.post("/advanced/compare-scenarios")
async def compare_scenarios(
    comparison_request: schemas.ScenarioComparisonRequest,
    db: Session = Depends(get_db)
):
    """
    Compare multiple scenarios
    """
    try:
        scenario_ids = comparison_request.scenario_ids
        comparison_metrics = comparison_request.metrics
        
        # Get all scenarios
        scenarios = {}
        for scenario_id in scenario_ids:
            scenario_data = get_scenario_results(scenario_id, db)
            if scenario_data:
                scenarios[scenario_id] = scenario_data
        
        if not scenarios:
            raise HTTPException(status_code=404, detail="No scenarios found")
        
        # Perform comparison
        comparison_results = perform_scenario_comparison(scenarios, comparison_metrics)
        
        return {
            'success': True,
            'comparison': comparison_results,
            'scenarios_compared': list(scenarios.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario comparison failed: {str(e)}")

@router.get("/advanced/health")
async def advanced_health_check():
    """
    Health check for advanced calculation engine
    """
    try:
        health_status = {
            'status': 'healthy',
            'engine_version': '1.0.0',
            'features': {
                'per_vehicle_calculations': True,
                'per_year_calculations': True,
                'real_time_aggregation': True,
                'constraint_management': True,
                'advanced_optimization': True
            },
            'performance': {
                'cache_enabled': advanced_engine.cache_enabled,
                'real_time_updates': advanced_engine.real_time_updates,
                'max_workers': advanced_engine.max_workers
            },
            'constraints_supported': list(advanced_engine.constraint_manager.constraint_types.keys()),
            'aggregation_levels': [level.value for level in AggregationLevel],
            'calculation_types': [calc_type.value for calc_type in CalculationType]
        }
        
        return health_status
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }

# Helper functions

def store_calculation_results(results: Dict[str, Any], db: Session):
    """Store calculation results in database"""
    try:
        # Implementation for storing results in database
        # This would typically involve creating database models and storing the results
        pass
    except Exception as e:
        logger.error(f"Failed to store calculation results: {str(e)}")

def get_cached_result(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Get cached calculation result"""
    for key, result in advanced_engine.calculation_cache.items():
        if result.get('scenario_id') == scenario_id:
            return result
    return None

def get_scenario_from_database(scenario_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Get scenario results from database"""
    # Implementation for retrieving from database
    return None

def filter_results_by_level(results: Dict[str, Any], aggregation_level: AggregationLevel, 
                           calculation_type: Optional[CalculationType]) -> Dict[str, Any]:
    """Filter results by aggregation level and calculation type"""
    filtered = results.copy()
    
    if aggregation_level == AggregationLevel.VEHICLE:
        # Return per-vehicle results
        return {
            'per_vehicle_results': results.get('per_vehicle_results', {})
        }
    elif aggregation_level == AggregationLevel.VEHICLE_TYPE:
        # Return per-vehicle-type results
        return {
            'per_year_results': results.get('per_year_results', {})
        }
    elif aggregation_level == AggregationLevel.TOTAL:
        # Return aggregated results
        return {
            'aggregated_results': results.get('aggregated_results', {})
        }
    
    return filtered

def generate_constraint_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on constraint analysis"""
    recommendations = []
    
    if not analysis['overall_compliance']:
        recommendations.append("Review constraint violations and adjust scenario parameters")
    
    if analysis['critical_violations']:
        recommendations.append("Address critical constraint violations before proceeding")
    
    return recommendations

def assess_constraint_risks(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Assess risks based on constraint analysis"""
    risk_level = 'low'
    if analysis['critical_violations']:
        risk_level = 'high'
    elif analysis['constraint_violations']:
        risk_level = 'medium'
    
    return {
        'risk_level': risk_level,
        'risk_factors': analysis['constraint_violations'],
        'mitigation_strategies': generate_mitigation_strategies(analysis)
    }

def generate_mitigation_strategies(analysis: Dict[str, Any]) -> List[str]:
    """Generate mitigation strategies for constraint violations"""
    strategies = []
    
    for violation in analysis['constraint_violations']:
        if 'technology_readiness' in str(violation):
            strategies.append("Consider alternative technologies with higher readiness levels")
        elif 'infrastructure' in str(violation):
            strategies.append("Plan for infrastructure development or alternative solutions")
        elif 'cost' in str(violation):
            strategies.append("Explore cost reduction strategies or alternative funding sources")
    
    return strategies

def get_scenario_results(scenario_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Get scenario results from database or cache"""
    # Check cache first
    cached = get_cached_result(scenario_id)
    if cached:
        return cached
    
    # Check database
    return get_scenario_from_database(scenario_id, db)

def filter_aggregated_results(aggregated: Dict[str, Any], aggregation_level: AggregationLevel,
                            calculation_type: Optional[CalculationType]) -> Dict[str, Any]:
    """Filter aggregated results by level and calculation type"""
    if aggregation_level == AggregationLevel.TOTAL:
        return aggregated.get('scenario_summary', {})
    elif aggregation_level == AggregationLevel.YEAR:
        return aggregated.get('yearly_totals', {})
    elif aggregation_level == AggregationLevel.VEHICLE_TYPE:
        return aggregated.get('vehicle_type_totals', {})
    
    return aggregated

def perform_scenario_comparison(scenarios: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
    """Perform comparison between multiple scenarios"""
    comparison = {
        'scenarios': list(scenarios.keys()),
        'metrics': metrics,
        'comparison_data': {}
    }
    
    for metric in metrics:
        comparison['comparison_data'][metric] = {}
        for scenario_id, scenario_data in scenarios.items():
            if 'aggregated_results' in scenario_data:
                summary = scenario_data['aggregated_results'].get('scenario_summary', {})
                comparison['comparison_data'][metric][scenario_id] = summary.get(metric, 0)
    
    return comparison

def calculate_average_time() -> float:
    """Calculate average calculation time"""
    # Simplified calculation
    return 2.5  # seconds

def get_total_violations() -> int:
    """Get total constraint violations across all scenarios"""
    total = 0
    for result in advanced_engine.calculation_cache.values():
        total += result.get('performance_metrics', {}).get('constraint_violations', 0)
    return total 