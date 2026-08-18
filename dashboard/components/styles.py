"""
Custom CSS/styling for the Streamlit Dashboard.
Provides premium glassmorphism dark-theme styling, custom fonts, animations, and styled components.
"""
import streamlit as st

def apply_premium_styles():
    """Injects custom CSS to style the Streamlit interface."""
    st.markdown(
        """
        <style>
        /* Import Outfit or Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', 'Segoe UI', sans-serif;
            background-color: #0f111a;
            color: #e2e8f0;
        }
        
        /* Main background dark styling */
        .stApp {
            background: linear-gradient(135deg, #0a0c14 0%, #151926 100%);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0c0e17 !important;
            border-right: 1px solid #1f293d;
        }
        
        /* Glassmorphic Cards */
        .glass-card {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-4px);
            border-color: rgba(99, 102, 241, 0.4);
        }
        
        /* Premium Gradient Headers */
        .gradient-text {
            background: linear-gradient(90deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        
        /* KPI Cards Grid styling */
        .kpi-container {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        .kpi-card {
            flex: 1;
            min-width: 200px;
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-left: 4px solid #6366f1;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        
        .kpi-card.red-border { border-left-color: #ef4444; }
        .kpi-card.green-border { border-left-color: #10b981; }
        .kpi-card.yellow-border { border-left-color: #f59e0b; }
        
        .kpi-card:hover {
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
            background: rgba(30, 41, 59, 0.75);
        }
        
        .kpi-title {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #f8fafc;
        }
        
        /* Status Badges */
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
        }
        
        .status-green { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
        .status-yellow { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
        .status-red { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }

        /* Animation */
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .pulse-element {
            animation: pulse 2s infinite;
        }
        
        /* Override Streamlit element visual defaults */
        div[data-testid="stMetricValue"] {
            font-weight: 700;
        }
        
        /* Pretty tables */
        .dataframe {
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px;
            background-color: transparent !important;
        }
        
        /* Primary buttons */
        .stButton>button {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            color: white !important;
            border: none !important;
            padding: 8px 20px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton>button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 6px 16px rgba(79, 70, 229, 0.5) !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
