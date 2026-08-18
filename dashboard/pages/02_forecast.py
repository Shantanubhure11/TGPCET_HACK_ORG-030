"""
Dashboard Page: Demand Forecast.
Displays historical demand, P10/P50/P90 LightGBM forecasts, and model performance.
"""
import streamlit as st
import pandas as pd
from dashboard.components.utils import fetch_api
from dashboard.components.charts import plot_demand_forecast

def show_forecast():
    st.markdown("<h1 class='gradient-text'>Probabilistic Demand Forecasting</h1>", unsafe_allow_html=True)
    st.write("Generates P10, P50, and P90 quantile bands. Powered by LightGBM Quantile Regression models.")

    # 1. Fetch available SKUs
    inventory_items = fetch_api("/api/inventory/list")
    sku_list = [item["sku_id"] for item in inventory_items]
    if not sku_list:
        sku_list = ["SKU-9902", "SKU-1234", "SKU-4567"]

    # 2. Sidebar controls on page
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_sku = st.selectbox("Select SKU Group", sku_list)
    with col2:
        horizon = st.selectbox("Forecast Horizon (Days)", [7, 14, 30, 60, 90], index=2)

    # 3. Load Forecast details
    with st.spinner("Fetching forecasting quantiles..."):
        forecast_res = fetch_api(f"/api/forecast/demand?sku_id={selected_sku}&horizon={horizon}")

    if forecast_res:
        metrics = forecast_res.get("model_metrics", {})
        
        # Display WAPE and RMSE KPIs
        wape = metrics.get("wape", 0.15)
        wape_status = "EXCELLENT" if wape < 0.10 else ("GOOD" if wape < 0.20 else "FAIR")
        
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-card green-border">
                    <div class="kpi-title">Model Weighted Error (WAPE)</div>
                    <div class="kpi-value">{wape * 100:.1f}%</div>
                    <div style="color: #34d399; font-size: 13px; margin-top: 5px;">Status: {wape_status}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Root Mean Squared Error (RMSE)</div>
                    <div class="kpi-value">{metrics.get("rmse", 8.4):.2f}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Model Version Active</div>
                    <div class="kpi-value" style="font-size: 20px; padding-top: 6px;">{forecast_res.get("model_version", "LGBM-Q-1.0")}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Plotly chart
        fig = plot_demand_forecast(forecast_res)
        st.plotly_chart(fig, use_container_width=True)

        # Show forecast table
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📋 Forecast Data Details")
        df_forecast = pd.DataFrame(forecast_res["forecast"])
        df_forecast["forecast_date"] = pd.to_datetime(df_forecast["forecast_date"]).dt.date
        st.dataframe(df_forecast, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error("No demand forecast available for this SKU.")

    # 4. Model retraining triggering
    st.markdown("---")
    st.subheader("🔄 Retrain ML Models")
    st.write("Retrains the LightGBM quantiles (P10, P50, P90) based on new transaction ledger records.")
    
    if st.button("Trigger Pipeline Retraining"):
        with st.spinner("Retraining LightGBM regressors... (Please wait)"):
            res = fetch_api("/api/forecast/retrain", method="POST", json_data={"lookback_days": 180})
            if res and res.get("status") == "success":
                st.success(f"Retraining successful! WAPE: {res['metrics']['wape']*100:.2f}%")
                st.balloons()
            else:
                st.error("Model retraining failed. Check server logs.")
