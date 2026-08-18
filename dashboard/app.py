"""
Main Streamlit application entry point.
Uses a unified sidebar navigation structure to route through the 6 core dashboard pages,
injecting premium styles and handling global page states.
"""
import streamlit as st

# Set Streamlit Page Configuration BEFORE any other st commands!
st.set_page_config(
    page_title="Supply Chain Digital Twin Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Components
from dashboard.components.styles import apply_premium_styles
from dashboard.pages.01_overview import show_overview
from dashboard.pages.02_forecast import show_forecast
from dashboard.pages.03_inventory import show_inventory
from dashboard.pages.04_simulation import show_simulation
from dashboard.pages.05_whatif import show_whatif
from dashboard.pages.06_procurement import show_procurement

def main():
    # 1. Apply visual styling elements
    apply_premium_styles()

    # 2. Sidebar Navigation Router
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0px;">
            <h2 style="color: #818cf8; font-weight: 700; margin-bottom: 5px;">⛓️ TwinTwin</h2>
            <p style="color: #94a3b8; font-size: 13px; margin-top: 0px;">Supply Chain Digital Twin Sandbox</p>
        </div>
        <hr style="border-color: #1f293d; margin-top: 5px; margin-bottom: 20px;"/>
        """,
        unsafe_allow_html=True
    )
    
    pages = {
        "Executive Overview": show_overview,
        "Demand Forecasting": show_forecast,
        "Inventory Health Grid": show_inventory,
        "Replenishment Simulator": show_simulation,
        "What-If Risk Analyzer": show_whatif,
        "Procurement Suggestions": show_procurement
    }

    selected_page_name = st.sidebar.radio(
        "Navigation Menu", 
        list(pages.keys())
    )

    st.sidebar.markdown(
        """
        <hr style="border-color: #1f293d; margin-top: 30px; margin-bottom: 15px;"/>
        <div style="font-size: 11px; color: #64748b;">
            Team: TGPCET Hackathon 2026<br/>
            Version: MVP v1.0.0<br/>
            Status: Seeding Mode Active
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Dispatch to selected page
    try:
        pages[selected_page_name]()
    except Exception as e:
        st.error(f"Error loading page: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()
