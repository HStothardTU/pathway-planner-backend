import streamlit as st
import os

# Configure page
st.set_page_config(
    page_title="Pathway Planner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for green and blue gradient design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57 0%, #4682B4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #2E8B57 0%, #4682B4 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #E8F5E8 0%, #E6F3FF 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E8B57;
    }
    
    .action-button {
        background: linear-gradient(135deg, #2E8B57 0%, #4682B4 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
    
    .action-button:hover {
        background: linear-gradient(135deg, #3CB371 0%, #5F9EA0 100%);
    }
</style>
""", unsafe_allow_html=True)

# Handle session state navigation
if 'navigate_to' in st.session_state:
    page = st.session_state.navigate_to
    del st.session_state.navigate_to
else:
    # Sidebar navigation
    st.sidebar.markdown('<div class="sidebar-header">Pathway Planner</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")

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
            "AI Insights"
        )
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Transport Decarbonization Tool**")

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
elif page == "Advanced Calculator":
    from pages import advanced_calculator
    advanced_calculator.show()
elif page == "Analysis & Insights":
    from pages import analysis_insights
    analysis_insights.show()
elif page == "AI Insights":
    from pages import ai_insights
    ai_insights.show() 