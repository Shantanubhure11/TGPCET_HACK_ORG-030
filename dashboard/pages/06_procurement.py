"""
Dashboard Page: Procurement Recommendations.
Displays explainable PO suggestions, ordering metrics, and CSV/JSON export actions.
"""
import json
import streamlit as st
import pandas as pd
from dashboard.components.utils import fetch_api

def show_procurement():
    st.markdown("<h1 class='gradient-text'>Explainable Procurement Recommendations</h1>", unsafe_allow_html=True)
    st.write("Calculates safety stock replenishment trigger points, rounding up to supplier MOQ thresholds.")

    # 1. Slider to configure service level
    col_sl, col_sort = st.columns([2, 1])
    with col_sl:
        service_level = st.slider("Target Service Level Z-Factor (%)", 80, 99, 95)
    with col_sort:
        sort_by = st.selectbox("Sort Recommendations By", ["Urgency", "Estimated Cost", "SKU ID"])

    # 2. Query recommendations from API
    with st.spinner("Analyzing inventory and generating PO recommendations..."):
        recs = fetch_api(f"/api/purchases/recommendations?service_level={service_level}")

    if not recs:
        st.success("All inventory levels are healthy. No replenishment orders needed!")
        return

    # Convert to DataFrame for sorting
    df = pd.DataFrame(recs)
    
    if sort_by == "Urgency":
        # Sort CRITICAL first, then HIGH
        df["urgency_rank"] = df["urgency"].map({"CRITICAL": 0, "HIGH": 1, "LOW": 2})
        df = df.sort_values("urgency_rank").drop(columns=["urgency_rank"])
    elif sort_by == "Estimated Cost":
        df = df.sort_values("estimated_cost", ascending=False)
    elif sort_by == "SKU ID":
        df = df.sort_values("sku_id")

    # 3. Renders individual PO recommendation cards
    st.subheader(f"💡 Recommended Orders ({len(df)} suggestions)")
    
    for idx, row in df.iterrows():
        urgency_class = "status-red" if row["urgency"] in ["CRITICAL", "HIGH"] else "status-yellow"
        cost_str = f"₹{row['estimated_cost']:,.2f}" if row["estimated_cost"] else "N/A"
        
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 18px; font-weight: 700; color: #f8fafc;">{row['sku_id']} - {row['sku_name']}</span>
                    <span class="status-badge {urgency_class}">{row['urgency']}</span>
                </div>
                <div style="font-size: 14px; color: #94a3b8; margin-bottom: 8px;">
                    Supplier: <strong style="color: #cbd5e1;">{row['supplier_id']} ({row['supplier_name']})</strong> | 
                    MOQ: <strong style="color: #cbd5e1;">{row['supplier_moq']}</strong>
                </div>
                <div style="border-left: 3px solid #818cf8; padding-left: 10px; margin: 15px 0;">
                    <div style="font-size: 13px; color: #94a3b8; text-transform: uppercase;">Decision Justification</div>
                    <div style="font-size: 14px; color: #f1f5f9; font-style: italic;">"{row['reason']}"</div>
                </div>
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 15px;">
                    <div>
                        <span style="font-size: 12px; color: #94a3b8; display: block;">RECOMMENDED QTY</span>
                        <strong style="font-size: 16px; color: #818cf8;">{row['recommended_qty']} units</strong>
                    </div>
                    <div>
                        <span style="font-size: 12px; color: #94a3b8; display: block;">ESTIMATED COST</span>
                        <strong style="font-size: 16px; color: #818cf8;">{cost_str}</strong>
                    </div>
                    <div>
                        <span style="font-size: 12px; color: #94a3b8; display: block;">STOCKOUT PROBABILITY</span>
                        <strong style="font-size: 16px; color: #f87171;">{row['stockout_probability']*100:.1f}%</strong>
                    </div>
                    <div>
                        <span style="font-size: 12px; color: #94a3b8; display: block;">PROJECTED RUNOUT DATE</span>
                        <strong style="font-size: 16px; color: #fbbf24;">{row['projected_stockout_date'] or 'N/A'}</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Action button to trigger PO generation
        if st.button(f"Approve & Create Purchase Order", key=f"btn_po_{row['sku_id']}_{idx}"):
            payload = {
                "supplier_id": row["supplier_id"],
                "sku_id": row["sku_id"],
                "order_qty": float(row["recommended_qty"]),
                "unit_cost": float(row["estimated_cost"] / row["recommended_qty"]) if row["estimated_cost"] else None,
                "notes": f"Automated dynamic recommendation. Urgency: {row['urgency']}"
            }
            po_res = fetch_api("/api/purchases/create", method="POST", json_data=payload)
            if po_res:
                st.success(f"Successfully generated Purchase Order: {po_res.get('po_number')}!")
                st.balloons()
                time.sleep(1)
                st.rerun()

    # 4. Exports
    st.markdown("---")
    st.subheader("📥 Export Recommendations")
    
    col_csv, col_json = st.columns(2)
    with col_csv:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download as CSV File",
            csv_data,
            "procurement_recommendations.csv",
            "text/csv",
            key='download-csv'
        )
    with col_json:
        json_data = json.dumps(recs, indent=2)
        st.download_button(
            "Download as JSON File",
            json_data,
            "procurement_recommendations.json",
            "application/json",
            key='download-json'
        )

import time
