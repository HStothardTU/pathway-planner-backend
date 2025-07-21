import streamlit as st
import os

# Configure page
st.set_page_config(
    page_title="Pathway Planner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("Pathway Planner")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    (
        "Dashboard",
        "Scenario Builder", 
        "Parameter Editor",
        "Visualize Pathways",
        "Uncertainty Explorer",
        "Reports & Export"
    )
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Teesside Transport Decarbonization Tool**")

# Page routing
if page == "Dashboard":
    from pages import dashboard
    dashboard.show()
elif page == "Scenario Builder":
    from pages import scenario_builder
    scenario_builder.show()
elif page == "Parameter Editor":
    from pages import parameter_editor
    parameter_editor.show()
elif page == "Visualize Pathways":
    from pages import visualize_pathways
    visualize_pathways.show()
elif page == "Uncertainty Explorer":
    from pages import uncertainty_explorer
    uncertainty_explorer.show()
elif page == "Reports & Export":
    from pages import reports_export
    reports_export.show() 