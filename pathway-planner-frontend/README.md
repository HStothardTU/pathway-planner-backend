# Pathway Planner Frontend (Streamlit)

This is the frontend for the Pathway Planner – Teesside Transport Decarbonization tool, built with Streamlit.

## Features
- Sidebar navigation for all main modules
- Modular page structure for easy expansion
- Ready for integration with backend API

## Directory Structure
```
app.py
pages/
  dashboard.py
  scenario_builder.py
  parameter_editor.py
  visualize_pathways.py
  uncertainty_explorer.py
  reports_export.py
assets/
requirements.txt
```

## Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Next Steps
- Build out each page in `pages/`
- Connect to backend API for data and analytics
- Add custom theming and branding 