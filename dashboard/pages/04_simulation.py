"""
Dashboard Page: Supply Chain Simulation.
Allows configuring stochastic lead time, supplier reliability, and running discrete-event warehouse simulations.
"""
import streamlit as st
from dashboard.components.utils import fetch_api
from dashboard.components.charts import plot_simulation_curve, plot_cost_pie_chart

def show_simulation():
    st.markdown("<h1 class='gradient-text'>Supply Chain Simulation Sandbox</h1>", unsafe_allow_html=True)
    st.write("Discrete-event SimPy digital twin simulating lead times, order points, and holding/shortage costs.")

    # 1. Fetch available SKUs
    inventory_items = fetch_api("/api/inventory/list")
    sku_list = [item["sku_id"] for item in inventory_items]
    if not sku_list:
        sku_list = ["SKU-9902", "SKU-1234", "SKU-4567"]

    selected_sku = st.selectbox("Select SKU to Simulate", sku_list)
    
    # Resolve initial parameters for selected SKU
    sku_data = next((item for item in inventory_items if item["sku_id"] == selected_sku), None)
    initial_rop = sku_data.get("rop", 100.0) if sku_data else 100.0
    initial_ss = sku_data.get("safety_stock", 40.0) if sku_data else 40.0

    st.markdown("### ⚙️ Stochastic Environment Sliders")
    col1, col2 = st.columns(2)

    with col1:
        lead_time_mean = st.slider("Mean Supplier Lead Time (Days)", 1.0, 30.0, 3.5, 0.5)
        lead_time_std = st.slider("Lead Time Standard Deviation (Days)", 0.0, 10.0, 0.8, 0.1)
        demand_multiplier = st.slider("Demand Scale Multiplier (What-If)", 0.5, 3.0, 1.0, 0.1)

    with col2:
        supplier_reliability = st.slider("Supplier Delivery Reliability (%)", 50, 100, 95)
        service_level = st.slider("Target Service Level Z-Factor (%)", 80, 99, 95)
        num_runs = st.select_slider("Monte Carlo Runs", [10, 50, 100, 250, 500], value=100)

    # 2. Run simulation trigger
    if st.button("🚀 Run Monte Carlo Digital Twin"):
        payload = {
            "scenario_name": "live_simulation",
            "sku_id": selected_sku,
            "lead_time_mean": float(lead_time_mean),
            "lead_time_std": float(lead_time_std),
            "demand_multiplier": float(demand_multiplier),
            "supplier_reliability_pct": float(supplier_reliability),
            "service_level": float(service_level),
            "num_runs": int(num_runs),
            "horizon_days": 90
        }

        with st.spinner(f"Running SimPy model ({num_runs} trajectories)..."):
            res = fetch_api("/api/simulation/run", method="POST", json_data=payload)

        if res and res.get("status") == "COMPLETED":
            st.success("Simulation finished successfully!")
            
            # Display metrics
            st.markdown(
                f"""
                <div class="kpi-container">
                    <div class="kpi-card green-border">
                        <div class="kpi-title">Achieved Service Level</div>
                        <div class="kpi-value">{res.get('service_level_achieved', 0.0)*100:.1f}%</div>
                    </div>
                    <div class="kpi-card red-border">
                        <div class="kpi-title">Total Project Cost</div>
                        <div class="kpi-value">₹{res.get('total_cost', 0.0):,.2f}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Stockout Events (Avg)</div>
                        <div class="kpi-value">{res.get('stockout_events', 0)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Columns for plots
            plot_col1, plot_col2 = st.columns([2, 1])
            with plot_col1:
                fig_curve = plot_simulation_curve(res)
                st.plotly_chart(fig_curve, use_container_width=True)
            with plot_col2:
                fig_cost = plot_cost_pie_chart(res)
                st.plotly_chart(fig_cost, use_container_width=True)
        else:
            st.error("Simulation run aborted by backend.")
