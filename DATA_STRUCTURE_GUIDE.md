# 📊 Fleet Data Structure Guide for AI Analysis

## Overview

This guide explains the data structure required for AI-powered fleet clustering analysis in the Pathway Planner. The AI analyzes your vehicle fleet across **6 key dimensions** to identify patterns, opportunities, and strategic recommendations for decarbonization.

## 🎯 What the AI Analyzes

### Core Dimensions (Required)
1. **Emissions Factor** (kg CO₂e/km): Environmental impact
2. **Technology Readiness Level** (1-9): Maturity of vehicle technology
3. **Cost Factor**: Relative cost compared to conventional vehicles
4. **Usage Intensity** (0-1): How frequently the vehicle type is used
5. **Fuel Type**: Primary energy source (Petrol, Diesel, Electric, etc.)
6. **Vehicle Category**: Broad vehicle classification

### Additional Context (Optional)
- **Annual Mileage**: Distance traveled per year
- **Fleet Size**: Number of vehicles of each type
- **Year Introduced**: When the vehicle type was first adopted
- **Expected Replacement Year**: Planned replacement timeline
- **Notes**: Additional information or comments

---

## 📋 Data Structure

### Required Fields

| Field Name | Type | Description | Validation | Example |
|------------|------|-------------|------------|---------|
| `Vehicle_ID` | Text | Unique identifier for each vehicle type | Required, unique | V001, V002 |
| `Vehicle_Type` | Text | Specific vehicle model or type | Required, descriptive | "Petrol Car (Medium)" |
| `Vehicle_Category` | Dropdown | Broad category of vehicle | Required, from list | Passenger, Freight |
| `Fuel_Type` | Dropdown | Primary fuel or energy source | Required, from list | Petrol, Electric |
| `Emissions_Factor_kgCO2e_per_km` | Decimal | CO₂ equivalent emissions per kilometer | Required, 0-10 | 0.180 |
| `Technology_Readiness_Level` | Integer | Maturity level of vehicle technology | Required, 1-9 | 9 |
| `Cost_Factor` | Decimal | Relative cost compared to conventional vehicles | Required, 0.1-5.0 | 1.0 |
| `Usage_Intensity` | Decimal | How frequently the vehicle type is used | Required, 0-1 | 0.3 |

### Optional Fields

| Field Name | Type | Description | Validation | Example |
|------------|------|-------------|------------|---------|
| `Annual_Mileage_km` | Integer | Average annual distance traveled | Optional, positive | 12000 |
| `Fleet_Size` | Integer | Number of vehicles of this type | Optional, positive | 150 |
| `Year_Introduced` | Integer | When this vehicle type was introduced | Optional, 4-digit year | 2020 |
| `Expected_Replacement_Year` | Integer | Planned replacement year | Optional, 4-digit year | 2030 |
| `Notes` | Text | Additional information or comments | Optional, free text | "Standard fleet vehicles" |

---

## 🔍 Field Definitions

### Vehicle_ID
- **Purpose**: Unique identifier for each vehicle type in your analysis
- **Format**: Any text string (e.g., V001, CAR001, BUS_ELECTRIC)
- **Best Practice**: Use consistent naming convention (e.g., V001, V002, V003)

### Vehicle_Type
- **Purpose**: Specific description of the vehicle model or type
- **Format**: Descriptive text
- **Examples**: 
  - "Petrol Car (Medium)"
  - "Diesel Bus (Single Deck)"
  - "Electric HGV (Rigid 7.5-17t)"
  - "Hybrid Van (Medium)"

### Vehicle_Category
- **Purpose**: Broad classification for grouping similar vehicles
- **Options**: Passenger, Public Transport, Freight, Light Commercial, Other
- **Guidance**:
  - **Passenger**: Cars, motorcycles, personal vehicles
  - **Public Transport**: Buses, trams, trains
  - **Freight**: HGVs, trucks, delivery vehicles
  - **Light Commercial**: Vans, small delivery vehicles
  - **Other**: Specialized vehicles, construction equipment

### Fuel_Type
- **Purpose**: Primary energy source or propulsion method
- **Options**: Petrol, Diesel, Electric, Hydrogen, Hybrid, Other
- **Guidance**:
  - **Petrol**: Gasoline-powered vehicles
  - **Diesel**: Diesel-powered vehicles
  - **Electric**: Battery electric vehicles (BEV)
  - **Hydrogen**: Fuel cell electric vehicles (FCEV) or hydrogen ICE
  - **Hybrid**: Any hybrid combination (petrol-electric, diesel-electric)
  - **Other**: Alternative fuels (biofuel, LPG, etc.)

### Emissions_Factor_kgCO2e_per_km
- **Purpose**: Environmental impact measurement
- **Unit**: kg CO₂ equivalent per kilometer
- **Range**: 0-10 kg CO₂e/km
- **Guidance**:
  - **0.0**: Zero-emission vehicles (electric, hydrogen)
  - **0.1-0.3**: Low-emission vehicles (hybrids, small cars)
  - **0.3-0.6**: Medium-emission vehicles (standard cars, vans)
  - **0.6-1.0**: High-emission vehicles (large cars, small buses)
  - **1.0+**: Very high-emission vehicles (HGVs, large buses)

### Technology_Readiness_Level (TRL)
- **Purpose**: Maturity assessment of vehicle technology
- **Scale**: 1-9 (1=concept, 9=proven technology)
- **Guidance**:
  - **1-2**: Basic research, concept development
  - **3-4**: Proof of concept, laboratory validation
  - **5-6**: Prototype development, field testing
  - **7-8**: System prototype, demonstration
  - **9**: Proven technology, commercial deployment

### Cost_Factor
- **Purpose**: Relative cost compared to conventional vehicles
- **Scale**: 0.1-5.0 (1.0 = same cost as conventional)
- **Guidance**:
  - **0.8**: 20% cheaper than conventional
  - **1.0**: Same cost as conventional
  - **1.3**: 30% more expensive than conventional
  - **1.5**: 50% more expensive than conventional
  - **2.0+**: Significantly more expensive

### Usage_Intensity
- **Purpose**: How frequently the vehicle type is used
- **Scale**: 0-1 (0=never used, 1=constant use)
- **Guidance**:
  - **0.1-0.3**: Occasional use (backup vehicles, seasonal)
  - **0.3-0.5**: Moderate use (standard fleet vehicles)
  - **0.5-0.7**: Regular use (daily operations)
  - **0.7-0.9**: Heavy use (high-mileage operations)
  - **0.9-1.0**: Very heavy use (24/7 operations)

---

## 📊 Data Quality Guidelines

### Best Practices
1. **Consistency**: Use consistent naming conventions and units
2. **Accuracy**: Provide realistic, data-driven values
3. **Completeness**: Fill in all required fields
4. **Validation**: Check data against known ranges and standards
5. **Documentation**: Include notes for unusual or special cases

### Common Data Sources
- **Emissions Factors**: DEFRA, BEIS, IPCC, manufacturer data
- **Technology Readiness**: Industry reports, manufacturer specifications
- **Cost Data**: Fleet management systems, procurement records
- **Usage Patterns**: Telematics data, operational records
- **Fleet Information**: Asset management systems, registration data

### Data Validation Rules
- **Emissions Factor**: Must be 0-10 kg CO₂e/km
- **Technology Readiness**: Must be 1-9
- **Cost Factor**: Must be 0.1-5.0
- **Usage Intensity**: Must be 0-1
- **Vehicle_ID**: Must be unique
- **Categories & Fuel Types**: Must be from predefined lists

---

## 🚀 Upload Process

### Step 1: Download Template
1. Go to Scenario Builder in the Pathway Planner
2. Expand "Upload Fleet Data from Excel"
3. Click "Download Excel Template"
4. Save the template to your computer

### Step 2: Fill in Your Data
1. Open the downloaded Excel file
2. Review the example data in the "Fleet Data" sheet
3. Replace example data with your actual fleet information
4. Use the dropdown menus for categories and fuel types
5. Follow the validation rules for numeric fields
6. Add any additional information in the Notes column

### Step 3: Validate Your Data
1. Check that all required fields are filled
2. Verify that numeric values are within valid ranges
3. Ensure Vehicle_IDs are unique
4. Review the Instructions sheet for guidance
5. Check the Data Dictionary for field definitions

### Step 4: Upload and Analyze
1. Save your Excel file
2. Return to the Scenario Builder
3. Upload your completed Excel file
4. Review the validation results
5. Use the data for scenario creation and AI analysis

---

## 🎯 AI Analysis Output

### What You'll Get
1. **Fleet Clustering**: Groups of similar vehicles based on characteristics
2. **Pattern Recognition**: Identification of emerging trends and opportunities
3. **Strategic Recommendations**: Actionable insights for decarbonization
4. **Priority Assessment**: High-impact areas for immediate action
5. **Technology Roadmap**: Optimal pathways for fleet transition

### Example Insights
- **High-Emission Clusters**: Vehicles requiring immediate electrification
- **Cost-Optimization Opportunities**: Areas where cost-effective changes can be made
- **Technology Readiness Gaps**: Where investment in new technologies is needed
- **Usage Pattern Analysis**: Optimization opportunities based on usage intensity

---

## 📞 Support

### Getting Help
- **Template Issues**: Check the Instructions sheet in the Excel template
- **Validation Errors**: Review the error messages and correct the data
- **Data Questions**: Refer to this guide or the Data Dictionary sheet
- **Technical Support**: Contact the development team

### Additional Resources
- **DEFRA Emissions Factors**: UK government emissions data
- **BEIS Transport Statistics**: UK transport sector data
- **IPCC Guidelines**: International emissions calculation standards
- **Industry Reports**: Manufacturer and industry association data

---

**🎉 Ready to analyze your fleet data? Download the template and start your AI-powered decarbonization journey!** 