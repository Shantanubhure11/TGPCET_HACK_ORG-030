"""
Sleek Plotly visualization components for the Streamlit dashboard.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def plot_demand_forecast(forecast_res: dict) -> go.Figure:
    """
    Renders forecast quantiles (P10, P50, P90) shaded bands over time.
    """
    points = forecast_res.get("forecast", [])
    if not points:
        return go.Figure()

    df = pd.DataFrame(points)
    df["forecast_date"] = pd.to_datetime(df["forecast_date"])

    fig = go.Figure()

    # P90 line (Upper bounds)
    fig.add_trace(go.Scatter(
        x=df["forecast_date"], y=df["p90"],
        line=dict(width=0),
        showlegend=False,
        name="P90 (Upper Band)"
    ))

    # P10 line (Lower bounds) - fills down to P10 with light purple transparency
    fig.add_trace(go.Scatter(
        x=df["forecast_date"], y=df["p10"],
        fill='tonexty',
        fillcolor='rgba(129, 140, 248, 0.12)', # transparent indigo
        line=dict(width=0),
        showlegend=False,
        name="P10 (Lower Band)"
    ))

    # P50 line (Median Expected Demand)
    fig.add_trace(go.Scatter(
        x=df["forecast_date"], y=df["p50"],
        line=dict(color='#818cf8', width=3, dash='solid'), # indigo
        name="P50 Median Forecast",
        mode='lines+markers'
    ))

    # Layout styling matching dark theme
    fig.update_layout(
        title={
            'text': f"30-Day Probabilistic Demand Forecast (SKU: {forecast_res['sku_id']})",
            'font': {'size': 16, 'color': '#f8fafc'}
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True, gridcolor='#1e293b', 
            tickfont=dict(color='#94a3b8'), 
            title_text="Date", title_font=dict(color='#94a3b8')
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#1e293b', 
            tickfont=dict(color='#94a3b8'), 
            title_text="Units Demanded", title_font=dict(color='#94a3b8')
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            font=dict(color='#f8fafc'),
            bgcolor='rgba(15, 23, 42, 0.6)',
            bordercolor='rgba(255,255,255,0.05)'
        ),
        hovermode="x unified"
    )
    return fig

def plot_simulation_curve(sim_data: dict) -> go.Figure:
    """
    Plots the average daily inventory path during simulation,
    with ROP and Safety Stock horizontal lines.
    """
    curve = sim_data.get("inventory_curve", [])
    if not curve:
        return go.Figure()

    df = pd.DataFrame(curve)

    fig = go.Figure()

    # Safety Stock shaded band
    ss = sim_data.get("safety_stock", 0.0)
    rop = sim_data.get("rop", 0.0)

    # Shaded safety stock buffer range
    fig.add_trace(go.Scatter(
        x=df["day"], y=[ss] * len(df),
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.08)', # light transparent red
        line=dict(color='#ef4444', width=1.5, dash='dash'),
        name="Safety Stock Buffer"
    ))

    # Reorder Point (ROP) horizontal trigger line
    fig.add_trace(go.Scatter(
        x=df["day"], y=[rop] * len(df),
        line=dict(color='#fbbf24', width=1.5, dash='longdashdot'),
        name="Reorder Point (ROP)"
    ))

    # P90 Upper bound curve
    fig.add_trace(go.Scatter(
        x=df["day"], y=df["p90_inventory"],
        line=dict(width=0),
        showlegend=False,
        name="P90 Upper Stock"
    ))

    # P10 Lower bound curve
    fig.add_trace(go.Scatter(
        x=df["day"], y=df["p10_inventory"],
        fill='tonexty',
        fillcolor='rgba(16, 185, 129, 0.08)', # light green trans
        line=dict(width=0),
        showlegend=False,
        name="P10 Lower Stock"
    ))

    # Average Inventory Path
    fig.add_trace(go.Scatter(
        x=df["day"], y=df["avg_inventory"],
        line=dict(color='#10b981', width=3), # emerald green
        name="Mean Stock Level"
    ))

    fig.update_layout(
        title={
            'text': f"Projected Replenishment Inventory Curve (Avg of {sim_data.get('num_runs')} runs)",
            'font': {'size': 16, 'color': '#f8fafc'}
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True, gridcolor='#1e293b', 
            tickfont=dict(color='#94a3b8'), 
            title_text="Simulation Day", title_font=dict(color='#94a3b8')
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#1e293b', 
            tickfont=dict(color='#94a3b8'), 
            title_text="Warehouse Stock Balance", title_font=dict(color='#94a3b8')
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            font=dict(color='#f8fafc'),
            bgcolor='rgba(15, 23, 42, 0.6)',
            bordercolor='rgba(255,255,255,0.05)'
        ),
        hovermode="x unified"
    )
    return fig

def plot_cost_pie_chart(sim_data: dict) -> go.Figure:
    """Pie chart showing breakdown of total supply chain costs."""
    costs = {
        "Holding Cost": sim_data.get("holding_cost", 0.0),
        "Stockout Shortage": sim_data.get("shortage_cost", 0.0),
        "PO Ordering Cost": sim_data.get("ordering_cost", 0.0)
    }

    labels = list(costs.keys())
    values = list(costs.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.4,
        marker=dict(colors=['#10b981', '#ef4444', '#6366f1']) # green, red, indigo
    )])

    fig.update_layout(
        title={
            'text': "Projected Cost Breakdown",
            'font': {'size': 14, 'color': '#f8fafc'}
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8fafc'),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(font=dict(size=11))
    )
    return fig

def plot_comparison_chart(base: dict, scen: dict) -> go.Figure:
    """Compares average stock paths side-by-side."""
    base_curve = base.get("inventory_curve", [])
    scen_curve = scen.get("inventory_curve", [])

    fig = go.Figure()

    if base_curve:
        df_b = pd.DataFrame(base_curve)
        fig.add_trace(go.Scatter(
            x=df_b["day"], y=df_b["avg_inventory"],
            line=dict(color='#94a3b8', width=2, dash='solid'),
            name="Baseline Scenario"
        ))

    if scen_curve:
        df_s = pd.DataFrame(scen_curve)
        fig.add_trace(go.Scatter(
            x=df_s["day"], y=df_s["avg_inventory"],
            line=dict(color='#a855f7', width=3, dash='solid'), # purple
            name="What-If Scenario"
        ))

    fig.update_layout(
        title={
            'text': "Inventory Path Comparison: Baseline vs Scenario",
            'font': {'size': 16, 'color': '#f8fafc'}
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#1e293b', tickfont=dict(color='#94a3b8')),
        yaxis=dict(showgrid=True, gridcolor='#1e293b', tickfont=dict(color='#94a3b8')),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            font=dict(color='#f8fafc'),
            bgcolor='rgba(15, 23, 42, 0.6)'
        ),
        hovermode="x unified"
    )
    return fig
