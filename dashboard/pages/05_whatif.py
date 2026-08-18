"""
Dashboard Page: What-If Scenarios.
Performs side-by-side comparison of baseline vs modified supply chain parameters.
"""
import streamlit as st
import pandas as pd
from dashboard.components.utils import fetch_api
from dashboard.components.charts import plot_comparison_chart

def show_whatif():
    st.markdown("<h1 class='gradient-text'>What-If Scenario Risk Analyzer</h1>", unsafe_allow_html=True)
    st.write("Compare inventory trajectories and cost trade-offs under varying supplier lead times and demand surges.")

    # 1. Select SKU to compare
    inventory_items = fetch_api("/api/inventory/list")
    sku_list = [item["sku_id"] for item in inventory_items]
    if not sku_list:
        sku_list = ["SKU-9902", "SKU-1234", "SKU-4567"]

    selected_sku = st.selectbox("SKU Group for Scenario Testing", sku_list)
    
    st.markdown("### 📊 Scenario Parameters Configuration")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Baseline Parameters")
        base_lt = st.slider("Baseline Lead Time (Days)", 1.0, 30.0, 3.0, key="base_lt")
        base_std = st.slider("Baseline Lead Time Std", 0.0, 10.0, 0.5, key="base_std")
        base_rel = st.slider("Baseline Reliability (%)", 50, 100, 95, key="base_rel")
        base_demand_mult = st.slider("Baseline Demand Mult", 0.5, 3.0, 1.0, key="base_dem")

    with col2:
        st.subheader("What-If Scenario Parameters")
        scen_lt = st.slider("Scenario Lead Time (Days)", 1.0, 30.0, 6.0, key="scen_lt")
        scen_std = st.slider("Scenario Lead Time Std", 0.0, 10.0, 1.5, key="scen_std")
        scen_rel = st.slider("Scenario Reliability (%)", 50, 100, 80, key="scen_rel")
        scen_demand_mult = st.slider("Scenario Demand Mult", 0.5, 3.0, 1.5, key="scen_dem")

    # 2. Run scenario comparison trigger
    if st.button("⚖️ Compare Scenarios"):
        # Build baseline request payload
        base_req = {
            "scenario_name": "baseline",
            "sku_id": selected_sku,
            "lead_time_mean": float(base_lt),
            "lead_time_std": float(base_std),
            "demand_multiplier": float(base_demand_mult),
            "supplier_reliability_pct": float(base_rel),
            "service_level": 95.0,
            "num_runs": 100,
            "horizon_days": 60
        }

        # Build modified scenario payload
        scen_req = {
            "scenario_name": "what_if_scenario",
            "sku_id": selected_sku,
            "lead_time_mean": float(scen_lt),
            "lead_time_std": float(scen_std),
            "demand_multiplier": float(scen_demand_mult),
            "supplier_reliability_pct": float(scen_rel),
            "service_level": 95.0,
            "num_runs": 100,
            "horizon_days": 60
        }

        with st.spinner("Running side-by-side simulations..."):
            res = fetch_api(
                "/api/simulation/compare",
                method="POST",
                json_data={
                    "baseline_req": base_req,
                    "scenario_req": scen_req
                }
            )

        if res:
            base_data = res.get("baseline", {})
            scen_data = res.get("scenario", {})

            # Render comparison metric delta tables
            st.markdown("### 📈 Key Metric Comparison & Deltas")
            
            # Format delta signs
            cost_delta = res.get('delta_total_cost', 0.0)
            cost_sign = "+" if cost_delta > 0 else ""
            
            prob_delta = res.get('delta_stockout_probability', 0.0) * 100
            prob_sign = "+" if prob_delta > 0 else ""

            st.markdown(
                f"""
                <div class="kpi-container">
                    <div class="kpi-card">
                        <div class="kpi-title">Baseline Service Level</div>
                        <div class="kpi-value">{base_data.get('service_level_achieved', 0.0)*100:.1f}%</div>
                    </div>
                    <div class="kpi-card yellow-border">
                        <div class="kpi-title">Scenario Service Level</div>
                        <div class="kpi-value">{scen_data.get('service_level_achieved', 0.0)*100:.1f}%</div>
                    </div>
                    <div class="kpi-card red-border">
                        <div class="kpi-title">Stockout Probability Delta</div>
                        <div class="kpi-value" style="color: {'#f87171' if prob_delta > 0 else '#34d399'}">{prob_sign}{prob_delta:.1f}%</div>
                    </div>
                </div>
                <div class="kpi-container">
                    <div class="kpi-card">
                        <div class="kpi-title">Baseline Avg Cost</div>
                        <div class="kpi-value">₹{base_data.get('total_cost', 0.0):,.2f}</div>
                    </div>
                    <div class="kpi-card yellow-border">
                        <div class="kpi-title">Scenario Avg Cost</div>
                        <div class="kpi-value">₹{scen_data.get('total_cost', 0.0):,.2f}</div>
                    </div>
                    <div class="kpi-card red-border">
                        <div class="kpi-title">Total Cost Delta</div>
                        <div class="kpi-value" style="color: {'#f87171' if cost_delta > 0 else '#34d399'}">{cost_sign}₹{cost_delta:,.2f}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Renders side-by-side Plotly chart
            fig_comp = plot_comparison_chart(base_data, scen_data)
            st.plotly_chart(fig_comp, use_container_width=True)

        else:
            st.error("Scenario evaluation failure on backend.")
