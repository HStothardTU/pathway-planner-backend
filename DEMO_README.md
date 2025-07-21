# Pathway Planner Demo

**Teesside Transport Decarbonization Tool**

## Quick Start for Demo

### Option 1: Automated Startup (Recommended)
```bash
python demo_startup.py
```

### Option 2: Manual Startup
1. **Start Backend:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend (in new terminal):**
   ```bash
   cd pathway-planner-frontend
   streamlit run app.py --server.port 8501
   ```

## Demo Flow

### 1. Dashboard Overview
- **URL:** http://localhost:8501
- **Features:** Key metrics, recent scenarios, sample visualization
- **Demo:** Shows the overall tool capabilities

### 2. Scenario Builder
- **Action:** Click "Load Demo Scenarios"
- **Features:** Create, view, and manage decarbonization scenarios with real vehicle types
- **Demo:** Shows 3 pre-built scenarios with different vehicle combinations:
  - **Conservative Pathway:** Passenger Cars + Buses
  - **Accelerated Transition:** Passenger Cars + Buses + Vans
  - **Net Zero by 2040:** All vehicle types (Cars, Buses, HGVs, Vans)

### 3. Visualize Pathways
- **Action:** Click "Load Demo Data for Optimization"
- **Action:** Click "Run Optimization"
- **Features:** Interactive charts, fuel mix breakdown by vehicle type, export options
- **Demo:** Shows optimization results with emissions and cost trends

## Key Features to Highlight

### ✅ Working Features
- **Real Vehicle Types:** Passenger Cars, Buses, HGVs, Vans with actual emissions factors
- **Emissions Factors:** Based on UK/DEFRA data (2025 lifecycle emissions)
- **Scenario Management:** Create, view, delete scenarios with vehicle type selection
- **Optimization Engine:** Linear programming solver for fuel mix optimization
- **Interactive Visualizations:** Plotly charts showing emissions and costs over time
- **Export Capabilities:** CSV and PDF export
- **Clean UI:** Professional interface with clear navigation and functionality

### 🔧 Technical Stack
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** Streamlit + Plotly
- **Optimization:** Linear programming solver (SciPy)
- **Database:** SQLite (for demo) / PostgreSQL (production)
- **Data Sources:** UK DEFRA/BEIS emissions factors

## Demo Script

### Opening (30 seconds)
"Today I'm showing you the Pathway Planner - a tool for planning Teesside's transport decarbonization using real UK emissions data. This tool helps us find optimal pathways to reduce emissions while considering costs and constraints."

### Dashboard Walkthrough (1 minute)
"Here's our dashboard showing key metrics. We can see total scenarios, optimized pathways, CO₂ reduction targets, and cost savings. The sample chart shows what a typical decarbonization pathway looks like."

### Scenario Builder Demo (2 minutes)
"Let me load some demo scenarios. We have three different approaches with different vehicle types:
- **Conservative Pathway:** Focuses on cars and buses with gradual transition
- **Accelerated Transition:** Adds vans for faster adoption of electric/hydrogen
- **Net Zero by 2040:** Includes all vehicle types for aggressive timeline

Notice how we can select specific vehicle types and see their real emissions factors from UK data."

### Optimization Demo (2 minutes)
"Now let's run optimization. This uses linear programming to find the optimal fuel mix that minimizes emissions while meeting our constraints. The tool considers the different emissions profiles of each vehicle type and fuel combination."

### Results Analysis (1 minute)
"Here are the results. We can see emissions decreasing over time, costs changing, and detailed fuel mix breakdowns for each vehicle type. The optimization considers real-world constraints like maximum annual change rates."

### Closing (30 seconds)
"This tool gives us data-driven insights for transport planning using real UK emissions data. We can compare different scenarios, understand trade-offs between vehicle types, and make informed decisions about Teesside's transport future."

## Vehicle Types & Emissions Data

### Passenger Cars
- Petrol Car: 0.210 kg CO₂e/km (lifecycle)
- Diesel Car: 0.200 kg CO₂e/km (lifecycle)
- Battery Electric Car: 0.065 kg CO₂e/km (lifecycle)
- Hydrogen Car (green): 0.040 kg CO₂e/km (lifecycle)

### Buses
- Diesel Bus: 1.000 kg CO₂e/km (lifecycle)
- Battery Electric Bus: 0.250 kg CO₂e/km (lifecycle)
- Hydrogen Bus (green): 0.200 kg CO₂e/km (lifecycle)

### Heavy Goods Vehicles (HGVs)
- Diesel Rigid HGV: 0.950 kg CO₂e/km (lifecycle)
- Battery Electric HGV: 0.325 kg CO₂e/km (lifecycle)
- Hydrogen HGV (green): 0.275 kg CO₂e/km (lifecycle)

### Vans / Light Goods Vehicles (LGVs)
- Diesel Van: 0.300 kg CO₂e/km (lifecycle)
- Electric Van: 0.120 kg CO₂e/km (lifecycle)
- Hydrogen Van (green): 0.140 kg CO₂e/km (lifecycle)

## Additional Pages

### Parameter Editor
- Edit vehicle emissions factors
- Adjust technology parameters
- Set policy constraints
- Configure budget limits

### Uncertainty Explorer
- Analyze data uncertainty
- Assess data quality
- Run sensitivity analysis
- Monte Carlo simulations

### Reports & Export
- Generate comprehensive reports
- Export in multiple formats
- Custom report templates
- Report history tracking

## Troubleshooting

### Common Issues
1. **Port already in use:** Change ports in the startup script
2. **Database errors:** The app will create a new SQLite database automatically
3. **Import errors:** Make sure virtual environment is activated

### Backend Health Check
- Visit: http://localhost:8000/api/v1/health
- Should return: `{"status": "ok"}`

### API Documentation
- Visit: http://localhost:8000/docs
- Interactive API documentation

## Next Steps After Demo

1. **Feedback Collection:** What features would be most valuable?
2. **Data Integration:** Connect to real Teesside transport data
3. **User Testing:** Get stakeholder input on usability
4. **Feature Development:** Prioritize based on feedback

---

**Demo Duration:** ~7-8 minutes total
**Questions:** Save for the end or ask during specific sections 