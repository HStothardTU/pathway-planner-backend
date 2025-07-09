import streamlit as st
import os

# Sidebar navigation
st.sidebar.title("Pathway Planner")
page = st.sidebar.radio(
    "Go to",
    (
        "Dashboard Overview",
        "Scenario Builder",
        "Parameter Editor",
        "Visualize Pathways",
        "Uncertainty Explorer",
        "Reports & Export"
    )
)

# Page routing
if page == "Dashboard Overview":
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