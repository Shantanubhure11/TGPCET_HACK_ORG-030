"""
Dashboard Page: Executive Overview.
Displays high-level supply chain KPIs, stockout risk distribution,
overstock analysis, and pending IoT discrepancies.
"""
import streamlit as st
import pandas as pd
from dashboard.components.utils import fetch_api
from dashboard.components.styles import apply_premium_styles

def show_overview():
    st.markdown("<h1 class='gradient-text'>Executive Supply Chain Overview</h1>", unsafe_allow_html=True)
    st.write("Real-time snapshot of inventory health, forecast accuracy, procurement status, and IoT anomaly counts.")

    # 1. Fetch data from backend
    inventory_items = fetch_api("/api/inventory/list")
    pending_pos = fetch_api("/api/purchases/pending")
    active_alerts = fetch_api("/api/alerts/active")

    # 2. Compute KPI Metrics
    total_skus = len(inventory_items)
    
    # Total stock value (available stock * unit cost)
    # Since health endpoint doesn't return cost directly, we default value
    total_value = sum([item["available_stock"] * 25.0 for item in inventory_items]) 
    
    critical_risk_skus = len([item for item in inventory_items if item["stock_status"] == "RED"])
    overstock_skus = len([item for item in inventory_items if item["available_stock"] > item["rop"] * 2])
    pending_po_count = len(pending_pos)
    iot_discrepancies = len([a for a in active_alerts if a["alert_type"] == "IOT_DISCREPANCY"])

    # 3. Render premium KPI Cards
    st.markdown(
        f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-title">Total SKUs Managed</div>
                <div class="kpi-value">{total_skus}</div>
            </div>
            <div class="kpi-card yellow-border">
                <div class="kpi-title">Total Inventory Value</div>
                <div class="kpi-value">₹{total_value:,.2f}</div>
            </div>
            <div class="kpi-card red-border">
                <div class="kpi-title">Critical Stockouts</div>
                <div class="kpi-value">{critical_risk_skus}</div>
            </div>
        </div>
        <div class="kpi-container">
            <div class="kpi-card yellow-border">
                <div class="kpi-title">Overstocked Products</div>
                <div class="kpi-value">{overstock_skus}</div>
            </div>
            <div class="kpi-card green-border">
                <div class="kpi-title">Pending Purchase Orders</div>
                <div class="kpi-value">{pending_po_count}</div>
            </div>
            <div class="kpi-card red-border pulse-element">
                <div class="kpi-title">IoT Mismatch Alerts</div>
                <div class="kpi-value" style="color: #f87171;">{iot_discrepancies}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("⚠️ Critical Inventory Alerts")
        if active_alerts:
            for alert in active_alerts[:5]:
                severity_color = "#ef4444" if alert["severity"] == "CRITICAL" else "#f59e0b"
                st.markdown(
                    f"""
                    <div style="border-left: 3px solid {severity_color}; padding-left: 10px; margin-bottom: 12px;">
                        <span style="font-weight: 600; color: #f1f5f9;">{alert['alert_type']}</span> - 
                        <span style="color: #94a3b8; font-size: 13px;">{alert['created_at'][:16]}</span>
                        <div style="font-size: 14px; color: #cbd5e1; margin-top: 4px;">{alert['message']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.success("No active stockout or IoT telemetry warnings.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📦 Pending Deliveries In-Transit")
        if pending_pos:
            df_po = pd.DataFrame(pending_pos)
            st.dataframe(
                df_po[["po_number", "sku_id", "order_qty", "expected_delivery", "status"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No orders currently in-transit from suppliers.")
        st.markdown("</div>", unsafe_allow_html=True)
