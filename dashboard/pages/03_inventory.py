"""
Dashboard Page: Inventory Health.
Displays tabular SKU health status including stock levels, dynamic safety stock, ROP, and stockout probability.
"""
import streamlit as st
import pandas as pd
from dashboard.components.utils import fetch_api

def show_inventory():
    st.markdown("<h1 class='gradient-text'>Inventory Health & Optimization</h1>", unsafe_allow_html=True)
    st.write("Dynamic ROP and safety stock indicators, current balances, and traffic light stockout warnings.")

    # 1. Load data
    with st.spinner("Fetching warehouse inventory balances..."):
        inventory_items = fetch_api("/api/inventory/list")

    if not inventory_items:
        st.warning("No inventory records found in database.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(inventory_items)

    # 2. Filters
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("🔍 Filter by Product SKU or Name", "")
    with col2:
        status_filter = st.multiselect(
            "Filter Stock Status", 
            ["GREEN", "YELLOW", "RED"], 
            default=["GREEN", "YELLOW", "RED"]
        )

    # Apply search and status filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["sku_id"].str.contains(search_query, case=False) | 
            filtered_df["sku_name"].str.contains(search_query, case=False)
        ]
    if status_filter:
        filtered_df = filtered_df[filtered_df["stock_status"].isin(status_filter)]

    # 3. Render clean tabular presentation
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader(f"Current Stocks Summary ({len(filtered_df)} items matching)")

    # Format dataframe for presentation
    disp_df = pd.DataFrame()
    disp_df["SKU"] = filtered_df["sku_id"]
    disp_df["Product Name"] = filtered_df["sku_name"]
    disp_df["Status"] = filtered_df["stock_status"]
    disp_df["Physical Stock"] = filtered_df["physical_stock"].astype(int)
    disp_df["Allocated"] = filtered_df["allocated_stock"].astype(int)
    disp_df["Available Net"] = filtered_df["available_stock"].astype(int)
    disp_df["Safety Stock (SS)"] = filtered_df["safety_stock"].round(0).astype(int)
    disp_df["Reorder Point (ROP)"] = filtered_df["rop"].round(0).astype(int)
    disp_df["Days of Inv."] = filtered_df["days_of_inventory"].round(1)
    disp_df["Stockout Risk"] = (filtered_df["stockout_probability"] * 100).round(1).astype(str) + "%"

    # Style table with status colors
    def style_status(val):
        color = '#00c851' if val == 'GREEN' else ('#fbbf24' if val == 'YELLOW' else '#f87171')
        return f'color: {color}; font-weight: bold;'

    st.dataframe(
        disp_df,
        use_container_width=True,
        hide_index=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Inventory Stock Adjustments
    st.markdown("---")
    st.subheader("🔧 Physical Stock Adjustments")
    st.write("Record physical counts, receive stock manually, or write off damaged items.")
    
    col_sku, col_qty, col_reason = st.columns(3)
    with col_sku:
        adj_sku = st.selectbox("Select SKU to Adjust", df["sku_id"].unique())
    with col_qty:
        adj_qty = st.number_input("Adjustment Quantity (+/-)", value=0)
    with col_reason:
        adj_reason = st.selectbox("Reason", ["MANUAL", "INITIAL", "CYCLE_COUNT", "DAMAGE_WRITE_OFF"])

    if st.button("Submit Stock Adjustment"):
        if adj_qty == 0:
            st.warning("Adjustment quantity must be non-zero.")
        else:
            payload = {
                "sku_id": adj_sku,
                "warehouse_id": "WH-01",
                "qty_change": float(adj_qty),
                "reason": adj_reason,
                "user_id": "manager",
                "notes": f"Manual adjustment via Streamlit UI"
            }
            res = fetch_api("/api/inventory/adjust", method="POST", json_data=payload)
            if res and res.get("status") == "success":
                st.success(f"Stock adjusted! New balance: {res.get('new_balance')}")
                st.rerun()
            else:
                st.error("Adjustment transaction failed.")
