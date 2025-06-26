import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
import requests
from io import StringIO
from datetime import datetime, timezone, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Marketing Sourced Meeting Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Premium CSS with Dynamic Background and Perfect Text Visibility
st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables for theme management */
    :root {
        --primary-gradient: linear-gradient(135deg, #4A90E2 0%, #5B9BD5 50%, #7B68EE 100%);
        --secondary-gradient: linear-gradient(45deg, #4169E1 0%, #6495ED 100%);
        --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --dark-bg: rgba(13, 17, 23, 0.95);
        --light-bg: rgba(255, 255, 255, 0.95);
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
        --text-primary: #1a202c;
        --text-secondary: #4a5568;
        --text-light: #ffffff;
    }
    
    /* Dark mode support with enhanced visibility */
    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #ffffff;
            --text-secondary: #e2e8f0;
            --text-light: #1a202c;
            --glass-bg: rgba(255, 255, 255, 0.08);
            --glass-border: rgba(255, 255, 255, 0.15);
        }
        
        /* Enhanced dark mode text visibility for sidebar - MAXIMUM CONTRAST */
        .stSelectbox label, .stDateInput label, .stRadio label {
            color: #ffffff !important;
            text-shadow: 3px 3px 8px rgba(0,0,0,0.9), 1px 1px 4px rgba(0,0,0,0.8) !important;
            font-weight: 900 !important;
            font-size: 1.2rem !important;
            background: rgba(30, 58, 138, 0.7) !important;
            padding: 0.5rem 0.8rem !important;
            border-radius: 8px !important;
            margin-bottom: 0.8rem !important;
            border: 2px solid rgba(147, 197, 253, 0.6) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .sidebar .stMarkdown h3 {
            color: #ffffff !important;
            text-shadow: 3px 3px 8px rgba(0,0,0,0.9), 1px 1px 4px rgba(0,0,0,0.8) !important;
            font-weight: 900 !important;
            background: rgba(30, 58, 138, 0.8) !important;
            padding: 1rem !important;
            border-radius: 10px !important;
            border: 2px solid rgba(147, 197, 253, 0.6) !important;
            margin-bottom: 1.5rem !important;
        }
        
        .sidebar .stMarkdown p, .sidebar .stMarkdown div {
            color: #ffffff !important;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.8), 1px 1px 3px rgba(0,0,0,0.7) !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
            background: rgba(30, 58, 138, 0.6) !important;
            padding: 0.4rem 0.6rem !important;
            border-radius: 6px !important;
            margin: 0.3rem 0 !important;
        }
        
        /* Dark mode dropdown styling with MAXIMUM contrast */
        .stSelectbox div[data-baseweb="select"],
        .stSelectbox div[data-baseweb="select"] > div,
        .stSelectbox div[data-baseweb="select"] > div > div {
            background-color: rgba(30, 58, 138, 0.95) !important;
            color: #ffffff !important;
            border: 3px solid rgba(147, 197, 253, 0.8) !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.7) !important;
        }
        
        /* Dark mode input fields with better visibility */
        .stDateInput input, .stTextInput input, .stNumberInput input {
            background-color: rgba(30, 58, 138, 0.95) !important;
            color: #ffffff !important;
            border: 3px solid rgba(147, 197, 253, 0.8) !important;
            font-weight: 700 !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.7) !important;
        }
        
        /* Dark mode radio buttons with enhanced visibility */
        .stRadio > div > label > div[data-testid="stMarkdownContainer"] > p {
            color: #ffffff !important;
            text-shadow: 3px 3px 8px rgba(0,0,0,0.9), 1px 1px 4px rgba(0,0,0,0.8) !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
            background: rgba(30, 58, 138, 0.6) !important;
            padding: 0.4rem 0.6rem !important;
            border-radius: 6px !important;
            margin: 0.2rem 0 !important;
        }
        
        /* Enhanced glass cards for dark mode - NO GREY */
        .glass-card {
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.8), rgba(59, 130, 246, 0.6)) !important;
            border: 2px solid rgba(147, 197, 253, 0.3) !important;
        }
        
        .chart-container {
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.8), rgba(59, 130, 246, 0.6)) !important;
            border: 2px solid rgba(147, 197, 253, 0.3) !important;
        }
        
        .chart-container h3, .chart-container h4 {
            color: #ffffff !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
        }
        
        /* Enhanced sidebar background for dark mode - MAXIMUM VISIBILITY */
        .css-1d391kg {
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.98), rgba(59, 130, 246, 0.95)) !important;
            border-right: 3px solid rgba(147, 197, 253, 0.8) !important;
        }
        
        /* Enhanced sidebar elements with strong backgrounds */
        .sidebar .stSelectbox > div > div,
        .sidebar .stDateInput > div > div > input,
        .sidebar .stRadio > div {
            background: rgba(30, 58, 138, 0.9) !important;
            border-radius: 10px !important;
            border: 3px solid rgba(147, 197, 253, 0.7) !important;
            color: #ffffff !important;
            backdrop-filter: blur(15px) !important;
            padding: 0.5rem !important;
            margin: 0.3rem 0 !important;
        }
        
        /* Force visibility for ALL sidebar text elements */
        .sidebar * {
            color: #ffffff !important;
        }
        
        .sidebar label, .sidebar p, .sidebar div, .sidebar span {
            color: #ffffff !important;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.8) !important;
            font-weight: 700 !important;
        }
    }
    
    /* Universal enhanced text visibility - WORKS IN BOTH MODES */
    .stSelectbox label, .stDateInput label, .stRadio label {
        color: var(--text-primary) !important;
        font-weight: 900 !important;
        font-size: 1.2rem !important;
        font-family: 'Inter', sans-serif !important;
        text-shadow: 0 3px 6px rgba(0,0,0,0.3) !important;
        margin-bottom: 0.8rem !important;
        background: rgba(59, 130, 246, 0.1) !important;
        padding: 0.5rem 0.8rem !important;
        border-radius: 8px !important;
        border: 2px solid rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Enhanced dropdown visibility - WORKS IN BOTH MODES */
    .stSelectbox div[data-baseweb="select"] {
        border: 3px solid rgba(59, 130, 246, 0.5) !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        background: rgba(255,255,255,0.98) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Enhanced radio button visibility - WORKS IN BOTH MODES */
    .stRadio > div > label > div[data-testid="stMarkdownContainer"] > p {
        color: var(--text-primary) !important;
        font-weight: 800 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        font-size: 1.1rem !important;
        background: rgba(59, 130, 246, 0.1) !important;
        padding: 0.4rem 0.6rem !important;
        border-radius: 6px !important;
        margin: 0.3rem 0 !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Sidebar enhancement - WORKS IN BOTH MODES */
    .sidebar .stMarkdown h3 {
        color: var(--text-primary) !important;
        font-weight: 900 !important;
        text-shadow: 0 3px 6px rgba(0,0,0,0.3) !important;
        font-size: 1.4rem !important;
        margin-bottom: 1.5rem !important;
        background: rgba(59, 130, 246, 0.15) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        border: 2px solid rgba(59, 130, 246, 0.3) !important;
    }
    
    .sidebar .stMarkdown p, .sidebar .stMarkdown div {
        color: var(--text-secondary) !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    
    /* Dynamic Background with Animated Particles */
    .stApp {
        background: linear-gradient(135deg, #4A90E2 0%, #5B9BD5 25%, #7B68EE 50%, #6495ED 75%, #4169E1 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        position: relative;
        min-height: 100vh;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(70, 130, 180, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(100, 149, 237, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(135, 206, 250, 0.2) 0%, transparent 50%);
        z-index: -1;
        animation: floatingBubbles 20s ease-in-out infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes floatingBubbles {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-30px) rotate(120deg); }
        66% { transform: translateY(20px) rotate(240deg); }
    }
    
    /* Font Family Override */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Enhanced Main Header */
    .main-header {
        background: linear-gradient(135deg, rgba(0,0,0,0.4) 0%, rgba(255,255,255,0.1) 100%);
        backdrop-filter: blur(30px);
        padding: 3rem 2rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        border: 2px solid rgba(255,255,255,0.2);
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shine 4s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(30deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(30deg); }
    }
    
    .main-header h1 {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #ffffff, #e2e8f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        font-size: 1.2rem !important;
        margin-top: 1rem !important;
        color: rgba(255,255,255,0.9) !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .brand-tag {
        position: absolute;
        top: 15px;
        left: 20px;
        background: linear-gradient(135deg, rgba(255,255,255,0.25), rgba(255,255,255,0.1));
        backdrop-filter: blur(15px);
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 700;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Enhanced Glass Cards - Elegant and Professional */
    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.9));
        backdrop-filter: blur(25px);
        border: 2px solid rgba(59, 130, 246, 0.2);
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        margin-bottom: 0.5rem;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .glass-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 45px rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,250,252,0.95));
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
        transition: left 0.6s ease;
    }
    
    .glass-card:hover::before {
        left: 100%;
    }
    
    /* Success card styling - elegant green */
    .success-card {
        background: linear-gradient(135deg, rgba(236, 253, 245, 0.95), rgba(220, 252, 231, 0.9)) !important;
        border: 2px solid rgba(16, 185, 129, 0.3) !important;
    }
    
    .success-card:hover {
        border-color: rgba(16, 185, 129, 0.5) !important;
        box-shadow: 0 15px 45px rgba(16, 185, 129, 0.15) !important;
    }
    
    /* Enhanced hover effects for dropdowns */
    .stSelectbox div[data-baseweb="select"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    /* Enhanced button hover effects */
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4) !important;
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    }
    
    /* Smooth transitions for all interactive elements */
    .stSelectbox, .stDateInput, .stRadio, .stButton {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Enhanced Metrics - Smaller and Cleaner */
    .metric-number {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        background: linear-gradient(135deg, #1e3a8a, #3b82f6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-shadow: none !important;
        animation: countUp 1.5s ease-out;
        line-height: 1.2 !important;
    }
    
    .metric-label {
        font-weight: 600 !important;
        color: #1e40af !important;
        margin: 0.5rem 0 0 0 !important;
        font-size: 0.9rem !important;
        text-shadow: none !important;
        line-height: 1.3 !important;
    }
    
    .success-card {
        background: linear-gradient(135deg, rgba(236, 253, 245, 0.95), rgba(220, 252, 231, 0.9)) !important;
        border: 2px solid rgba(16, 185, 129, 0.3) !important;
    }
    
    .success-card .metric-number {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    
    .success-card .metric-label {
        color: #065f46 !important;
        font-weight: 700 !important;
    }
    
    /* Animated Elements */
    .pulse-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #10b981;
        animation: pulse 2s infinite;
        margin-right: 8px;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    @keyframes countUp {
        from { opacity: 0; transform: translateY(30px) scale(0.8); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    /* Enhanced Chart Containers */
    .chart-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(249,250,251,0.95));
        backdrop-filter: blur(30px);
        padding: 2.5rem;
        border-radius: 25px;
        box-shadow: 0 20px 60px rgba(59, 130, 246, 0.08);
        margin-bottom: 2rem;
        border: 2px solid rgba(59, 130, 246, 0.15);
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .chart-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 25px 70px rgba(59, 130, 246, 0.12);
        border-color: rgba(59, 130, 246, 0.25);
    }
    
    .chart-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #6366f1, #8b5cf6);
        border-radius: 25px 25px 0 0;
    }
    
    .chart-container::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 70%);
        animation: subtleGlow 8s ease-in-out infinite;
        pointer-events: none;
    }
    
    @keyframes subtleGlow {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }
    
    .chart-container h3, .chart-container h4 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        text-shadow: none !important;
        position: relative;
        z-index: 2;
    }
    
    /* Enhanced Text Visibility for Charts and Legends */
    .js-plotly-plot .plotly .legend text,
    .js-plotly-plot .plotly .legendtext,
    .js-plotly-plot .plotly .legend .traces text {
        fill: #1a202c !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .xaxislayer-above text,
    .js-plotly-plot .plotly .yaxislayer-above text {
        fill: #1a202c !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .js-plotly-plot .plotly .xtitle,
    .js-plotly-plot .plotly .ytitle {
        fill: #1a202c !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .js-plotly-plot .plotly .gtitle {
        fill: #1a202c !important;
        font-weight: 800 !important;
        font-size: 18px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Sidebar Enhancements - LIGHT MODE */
    .css-1d391kg {
        background: linear-gradient(135deg, rgba(239, 246, 255, 0.98), rgba(219, 234, 254, 0.95)) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 3px solid rgba(59, 130, 246, 0.3) !important;
    }
    
    .sidebar .stSelectbox > div > div,
    .sidebar .stDateInput > div > div > input,
    .sidebar .stRadio > div {
        background: rgba(255,255,255,0.98) !important;
        border-radius: 10px !important;
        border: 3px solid rgba(59, 130, 246, 0.3) !important;
        color: var(--text-primary) !important;
        backdrop-filter: blur(15px) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1) !important;
        padding: 0.5rem !important;
        margin: 0.3rem 0 !important;
    }
    
    .sidebar .stMarkdown h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        text-shadow: none !important;
        font-size: 1.2rem !important;
    }
    
    .sidebar .stMarkdown p, .sidebar .stMarkdown div {
        color: var(--text-secondary) !important;
        text-shadow: none !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Enhanced selectbox and input styling */
    .stSelectbox label, .stDateInput label, .stRadio label {
        color: #1a202c !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        border: 2px solid rgba(30, 64, 175, 0.3) !important;
        font-weight: 600 !important;
        color: #1a202c !important;
    }
    
    /* Enhanced info/success/warning text */
    .stInfo, .stSuccess, .stWarning, .stError {
        color: #1a202c !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stInfo p, .stSuccess p, .stWarning p, .stError p {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    /* Status Indicators */
    .status-connected {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        padding: 1.2rem !important;
        border-radius: 12px !important;
        text-align: center !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.25) !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(15px) !important;
        transition: all 0.3s ease !important;
    }
    
    .status-connected:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 35px rgba(16, 185, 129, 0.35) !important;
    }
    
    /* Data Table Styling */
    .stDataFrame {
        background: rgba(255,255,255,0.95) !important;
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
    }
    
    .stDataFrame table {
        color: #1a202c !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stDataFrame th {
        background-color: rgba(30, 64, 175, 0.1) !important;
        color: #1a202c !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    
    .stDataFrame td {
        color: #1a202c !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    
    /* Enhanced Metric Styling */
    .stMetric {
        background: rgba(255,255,255,0.9) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        border: 1px solid rgba(30, 64, 175, 0.2) !important;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        color: #1a202c !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stMetric [data-testid="metric-container"] .metric-value {
        color: #1a202c !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
    }
    
    .stMetric [data-testid="metric-container"] .metric-label {
        color: #4a5568 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* Strong Metric Text Visibility */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.95) !important;
        padding: 1.2rem !important;
        border-radius: 12px !important;
        border: 2px solid rgba(30, 64, 175, 0.2) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #1a202c !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        font-family: 'Inter', sans-serif !important;
        text-shadow: none !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #1a202c !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        text-shadow: none !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        color: #10b981 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Override any conflicting styles */
    .stMetric * {
        color: #1a202c !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Button Enhancements */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Alert and Info Boxes */
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 15px !important;
        backdrop-filter: blur(15px) !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
    }
    
    /* Footer Enhancement */
    .footer-enhanced {
        background: linear-gradient(135deg, rgba(0,0,0,0.4), rgba(255,255,255,0.1));
        backdrop-filter: blur(25px);
        border: 2px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        color: white !important;
        margin-top: 3rem;
        position: relative;
        overflow: hidden;
    }
    
    .footer-enhanced::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #f5576c, #4facfe);
        animation: rainbow 3s linear infinite;
    }
    
    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2.5rem !important; }
        .metric-number { font-size: 2rem !important; }
        .glass-card { padding: 1.5rem !important; }
        .chart-container { padding: 1.5rem !important; }
    }
    
    /* Loading Animation */
    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }
    
    .loading-shimmer {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200px 100%;
        animation: shimmer 1.5s infinite;
    }




</style>
""", unsafe_allow_html=True)

# Enhanced animated counter with better effects
def create_animated_metric(value, label, is_success=False):
    card_class = "glass-card success-card" if is_success else "glass-card"
    return f'''
    <div class="{card_class}">
        <div class="metric-number">{value}</div>
        <p class="metric-label">{label}</p>
    </div>
    '''

# Enhanced gauge chart with premium styling
def create_gauge_chart(value, title, max_value=100):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 22, 'color': '#1a202c', 'family': 'Inter'}},
        delta = {'reference': max_value/2, 'font': {'size': 16, 'color': '#4a5568'}},
        number = {'font': {'size': 32, 'color': '#1a202c', 'family': 'Inter'}},
        gauge = {
            'axis': {'range': [None, max_value], 'tickwidth': 2, 'tickcolor': "#4a5568", 'tickfont': {'size': 12}},
            'bar': {'color': "#667eea", 'thickness': 0.8},
            'bgcolor': "rgba(255,255,255,0.9)",
            'borderwidth': 3,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, max_value*0.3], 'color': '#fed7d7'},
                {'range': [max_value*0.3, max_value*0.7], 'color': '#fef5e7'},
                {'range': [max_value*0.7, max_value], 'color': '#dcfce7'}
            ],
            'threshold': {
                'line': {'color': "#dc2626", 'width': 5},
                'thickness': 0.8,
                'value': max_value*0.9
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        font={'color': "#1a202c", 'family': "Inter", 'size': 14, 'weight': 600},
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# Enhanced data loading with better error handling
@st.cache_data(ttl=300)
def load_google_sheets_data():
    """Load data from Google Sheets with auto-refresh every 5 minutes"""
    try:
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2-ynySfxqoXOra8yMSUO3x5AjlOp42soc2FhE4TySJ9to825OpNCODiIcF70pmv_jI0li4xE5qJ7r/pub?gid=0&single=true&output=csv"
        
        with st.spinner('🔄 Fetching latest data...'):
            response = requests.get(csv_url, timeout=15)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text))
                return df, None
            else:
                return None, f"Failed to fetch data. Status code: {response.status_code}"
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

# Enhanced sidebar with premium styling
with st.sidebar:
    st.markdown("### 🎛️ **Dashboard Controls**")
    st.markdown("---")
    
    # Data source selection with enhanced styling
    data_source = st.radio(
        "**📊 Data Source:**",
        ["Google Sheets (Auto-Update)", "Upload Excel File"],
        help="Choose your preferred data source for real-time analytics"
    )
    
    if data_source == "Google Sheets (Auto-Update)":
        st.markdown('<div class="status-connected"><span class="pulse-dot"></span>Live Connection Active</div>', unsafe_allow_html=True)
        
        # Enhanced status display with IST time
        ist = timezone(timedelta(hours=5, minutes=30))
        current_time_ist = datetime.now(ist).strftime("%H:%M:%S")
        st.info(f"🕐 **Auto-refresh:** Every 5 minutes\n\n⏰ **Last check (IST):** {current_time_ist}\n\n📡 **Status:** Connected")
        
        # Premium refresh button
        if st.button("🔄 **Refresh Data**", type="primary", help="Manually refresh data from Google Sheets"):
            st.cache_data.clear()
            st.rerun()
        
        # Load data with progress
        df, error = load_google_sheets_data()
        
        if error:
            st.error(f"❌ {error}")
            st.info("💡 **Tip:** Check your internet connection and try again")
            st.stop()
        elif df is None:
            st.error("❌ No data loaded from Google Sheets")
            st.stop()
        else:
            st.success(f"✅ **{len(df):,} records** loaded successfully")
    
    else:
        uploaded_file = st.file_uploader(
            "📁 **Upload Excel File**", 
            type=["xlsx", "xls"],
            help="Upload your Excel file containing sales data"
        )
        if uploaded_file:
            with st.spinner('📊 Processing Excel file...'):
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ **{len(df):,} records** loaded from file")
        else:
            df = None

    # Enhanced filters section
    if df is not None and not df.empty:
        # Data validation
        if 'Date' not in df.columns:
            st.error("❌ Missing 'Date' column in data")
            st.stop()

        if 'SDR' not in df.columns:
            st.error("❌ Missing 'SDR' column in data")
            st.stop()

        # Enhanced date parsing
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Week'] = df['Date'].dt.isocalendar().week
        df['Month'] = df['Date'].dt.month_name()
        df['Quarter'] = df['Date'].dt.quarter

        # Premium filters
        st.markdown("---")
        st.markdown("### 🎯 **Smart Filters**")
        
        # Multi-select filters with enhanced styling
        sdrs = sorted(df['SDR'].dropna().unique())
        selected_sdr = st.selectbox("👤 **Sales Development Rep**", options=["All"] + sdrs, help="Filter by specific SDR")

        statuses = sorted(df['Status'].dropna().unique())
        selected_status = st.selectbox("📋 **Demo Status**", options=["All"] + statuses, help="Filter by demo status")

        # Conditional filters based on available columns
        if 'Source' in df.columns:
            sources = sorted(df['Source'].dropna().unique())
            selected_source = st.selectbox("🔗 **Lead Source**", options=["All"] + sources, help="Filter by lead source")
        else:
            selected_source = "All"

        if 'Sales Team' in df.columns:
            sales_teams = sorted(df['Sales Team'].dropna().unique())
            selected_sales_team = st.selectbox("👥 **Sales Team**", options=["All"] + sales_teams, help="Filter by sales team")
        else:
            selected_sales_team = "All"

        if 'AE' in df.columns:
            aes = sorted(df['AE'].dropna().unique())
            selected_ae = st.selectbox("🎯 **Account Executive**", options=["All"] + aes, help="Filter by AE")
        else:
            selected_ae = "All"

        if 'Industry' in df.columns:
            industries = sorted(df['Industry'].dropna().unique())
            selected_industry = st.selectbox("🏭 **Industry**", options=["All"] + industries, help="Filter by industry")
        else:
            selected_industry = "All"

        if 'Employee Size' in df.columns:
            employee_sizes = sorted(df['Employee Size'].dropna().unique())
            selected_employee_size = st.selectbox("👥 **Employee Size**", options=["All"] + employee_sizes, help="Filter by employee size")
        else:
            selected_employee_size = "All"

        # Enhanced date range filters
        st.markdown("---")
        st.markdown("### 📅 **Date Range**")
        
        col1, col2 = st.columns(2)
        with col1:
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            from_date = st.date_input("📅 **From**", min_value=min_date, max_value=max_date, value=min_date)
        
        with col2:
            to_date = st.date_input("📅 **To**", min_value=min_date, max_value=max_date, value=max_date)

        # Apply all filters
        filtered_df = df[
            (df['Date'].dt.date >= from_date) &
            (df['Date'].dt.date <= to_date)
        ]

        if selected_sdr != "All":
            filtered_df = filtered_df[filtered_df['SDR'] == selected_sdr]

        if selected_status != "All":
            filtered_df = filtered_df[filtered_df['Status'] == selected_status]

        if selected_source != "All" and 'Source' in df.columns:
            filtered_df = filtered_df[filtered_df['Source'] == selected_source]

        if selected_sales_team != "All" and 'Sales Team' in df.columns:
            filtered_df = filtered_df[filtered_df['Sales Team'] == selected_sales_team]

        if selected_ae != "All" and 'AE' in df.columns:
            filtered_df = filtered_df[filtered_df['AE'] == selected_ae]

        if selected_industry != "All" and 'Industry' in df.columns:
            filtered_df = filtered_df[filtered_df['Industry'] == selected_industry]

        if selected_employee_size != "All" and 'Employee Size' in df.columns:
            filtered_df = filtered_df[filtered_df['Employee Size'] == selected_employee_size]

        # Filter summary
        st.markdown("---")
        st.markdown("### 📊 **Filter Summary**")
        st.info(f"📈 **Showing {len(filtered_df):,} of {len(df):,} records**\n\n📅 **Date Range:** {from_date} to {to_date}")

    else:
        filtered_df = None

# Premium main header
st.markdown('''
<div class="main-header">
    <div class="brand-tag">Analytics</div>
    <h1>📊 Marketing Sourced Meeting Dashboard</h1>
    <p></p>
</div>
''', unsafe_allow_html=True)

# Enhanced KPI section
if df is not None:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if data_source == "Google Sheets (Auto-Update)":
            st.markdown(create_animated_metric("📡", "Live Data"), unsafe_allow_html=True)
        else:
            st.markdown(create_animated_metric("📁", "File Data"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_animated_metric(f"{len(df):,}", "Total Records"), unsafe_allow_html=True)
    
    with col3:
        filtered_count = len(filtered_df) if filtered_df is not None else 0
        st.markdown(create_animated_metric(f"{filtered_count:,}", "Filtered"), unsafe_allow_html=True)
    
    with col4:
        if filtered_df is not None and not filtered_df.empty:
            completion_rate = len(filtered_df[filtered_df['Status'].str.lower() == 'done']) / len(filtered_df) * 100
            st.markdown(create_animated_metric(f"{completion_rate:.1f}%", "Completion", True), unsafe_allow_html=True)
        else:
            st.markdown(create_animated_metric("0%", "Completion"), unsafe_allow_html=True)

st.markdown("---")

# Main dashboard content
if df is not None and filtered_df is not None:
    # Enhanced data overview
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📋 **Data Overview & Insights**")
    
    if not filtered_df.empty:
        # Summary metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_demos = len(filtered_df)
            st.metric("Total Demos", f"{total_demos:,}", delta=None)
        
        with col2:
            completed = len(filtered_df[filtered_df['Status'].str.lower() == 'done'])
            st.metric("Completed", f"{completed:,}", delta=f"{completed/total_demos*100:.1f}%" if total_demos > 0 else "0%")
        
        with col3:
            scheduled = len(filtered_df[filtered_df['Status'].str.lower().isin(['scheduled', 'rescheduled'])])
            st.metric("Scheduled", f"{scheduled:,}", delta=f"{scheduled/total_demos*100:.1f}%" if total_demos > 0 else "0%")
        
        with col4:
            avg_per_sdr = total_demos / filtered_df['SDR'].nunique() if filtered_df['SDR'].nunique() > 0 else 0
            st.metric("Avg per SDR", f"{avg_per_sdr:.1f}", delta=None)
        
        st.markdown("---")
        
        # Enhanced data table - keep original structure
        if 'SDR' in filtered_df.columns:
            cols_to_drop = ['SDR','Contact Name','Title','Sales Accepted?','Remarks','Meeting Transcript','Week']
            cols_to_drop = [col for col in cols_to_drop if col in filtered_df.columns]
            display_df = filtered_df.drop(columns=cols_to_drop)
            st.dataframe(display_df, height=350, use_container_width=True, hide_index=True)
        else:
            st.dataframe(filtered_df, height=350, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    if not filtered_df.empty:
        # Premium Performance Dashboard
        st.markdown("### 🎯 **Meeting Status Overview**")
        
        # Top row metrics with gauges
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            completed_count = filtered_df[filtered_df['Status'].str.lower() == 'done'].shape[0]
            st.markdown(create_animated_metric(completed_count, "Successful Demos", True), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            scheduled_statuses = ['done', 'scheduled', 'rescheduled']
            scheduled_count = filtered_df[filtered_df['Status'].str.lower().isin(scheduled_statuses)].shape[0]
            st.markdown(create_animated_metric(scheduled_count, "Scheduled Demos"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if len(filtered_df) > 0:
                completion_rate = (completed_count / len(filtered_df)) * 100
                gauge_fig = create_gauge_chart(completion_rate, "Completion Rate %", 100)
                st.plotly_chart(gauge_fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Advanced Analytics Section
        st.markdown("---")
        st.markdown("### 📊 **Detailed Meeting Analytics**")

        # Row 1: SDR Performance Analysis
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # SDR performance summary
        sdr_summary = filtered_df.groupby('SDR').agg({
            'Status': ['count', lambda x: (x.str.lower() == 'done').sum()]
        }).round(2)
        
        sdr_summary.columns = ['Total_Demos', 'Completed_Demos']
        sdr_summary['Success_Rate'] = (sdr_summary['Completed_Demos'] / sdr_summary['Total_Demos'] * 100).round(1)
        sdr_summary = sdr_summary.reset_index()
        
        # SDR performance chart
        sdr_status_counts = filtered_df.groupby(['SDR', 'Status']).size().reset_index(name='Count')
        fig_sdr = px.bar(
            sdr_status_counts, 
            x='SDR', 
            y='Count', 
            color='Status',
            barmode='group', 
            color_discrete_sequence=['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe', '#eff6ff'],
            title="SDR Performance Overview",
            text='Count'
        )
        fig_sdr.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1a202c', family='Inter', size=14, weight=600),
            title_font_size=18,
            title_font_color='#1a202c',
            title_font_weight=800,
            margin=dict(l=50, r=50, t=100, b=50),
            xaxis=dict(
                tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600), 
                title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                showgrid=False
            ),
            yaxis=dict(
                tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600), 
                title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                showgrid=False
            ),
            legend=dict(
                bgcolor='rgba(255,255,255,0.95)', 
                font=dict(color='#1a202c', size=14, family='Inter', weight=600),
                bordercolor='#1a202c',
                borderwidth=1
            )
        )
        fig_sdr.update_traces(
            hovertemplate="<b>%{x}</b><br>Status: %{fullData.name}<br>Count: %{y}<extra></extra>",
            textposition='outside',
            textfont=dict(size=12, color='#1a202c', family='Inter', weight=600)
        )
        st.plotly_chart(fig_sdr, use_container_width=True)
        
        # SDR summary table
        st.markdown("**📊 SDR Summary Metrics**")
        st.dataframe(sdr_summary, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Row 2: Lead Source Performance Analytics
        if 'Source' in filtered_df.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Create source performance summary
            source_summary = filtered_df.groupby('Source').agg({
                'Status': ['count', lambda x: (x.str.lower() == 'done').sum()]
            }).round(2)
            
            source_summary.columns = ['Total_Demos', 'Completed_Demos']
            source_summary['Completion_Rate'] = (source_summary['Completed_Demos'] / source_summary['Total_Demos'] * 100).round(1)
            source_summary = source_summary.reset_index()
            
            # Enhanced grouped bar chart for source
            source_status_counts = filtered_df.groupby(['Source', 'Status']).size().reset_index(name='Count')
            fig_source = px.bar(
                source_status_counts, 
                x='Source', 
                y='Count', 
                color='Status',
                barmode='group', 
                color_discrete_sequence=['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe', '#eff6ff'],
                title="Lead Source Overview",
                text='Count'
            )
            fig_source.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1a202c', family='Inter', size=14, weight=600),
                title_font_size=18,
                title_font_color='#1a202c',
                title_font_weight=800,
                margin=dict(l=50, r=50, t=100, b=50),
                xaxis=dict(
                    tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600), 
                    tickangle=45,
                    title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                    showgrid=False
                ),
                yaxis=dict(
                    tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600),
                    title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                    showgrid=False
                ),
                legend=dict(
                    bgcolor='rgba(255,255,255,0.95)', 
                    font=dict(color='#1a202c', size=14, family='Inter', weight=600),
                    bordercolor='#1a202c',
                    borderwidth=1
                )
            )
            fig_source.update_traces(
                hovertemplate="<b>%{x}</b><br>Status: %{fullData.name}<br>Count: %{y}<extra></extra>",
                textposition='outside',
                textfont=dict(size=12, color='#1a202c', family='Inter', weight=600)
            )
            st.plotly_chart(fig_source, use_container_width=True)
            
            # Source summary table
            st.markdown("**📊 Lead Source Summary Metrics**")
            st.dataframe(source_summary, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Row 3: Team Performance Analytics
        if 'Sales Team' in filtered_df.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Create team performance summary
            team_summary = filtered_df.groupby('Sales Team').agg({
                'Status': ['count', lambda x: (x.str.lower() == 'done').sum()]
            }).round(2)
            
            team_summary.columns = ['Total_Demos', 'Completed_Demos']
            team_summary['Completion_Rate'] = (team_summary['Completed_Demos'] / team_summary['Total_Demos'] * 100).round(1)
            team_summary = team_summary.reset_index()
            
            # Enhanced grouped bar chart
            sales_status_counts = filtered_df.groupby(['Sales Team', 'Status']).size().reset_index(name='Count')
            fig_sales = px.bar(
                sales_status_counts, 
                x='Sales Team', 
                y='Count', 
                color='Status',
                barmode='group', 
                color_discrete_sequence=['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe', '#eff6ff'],
                title="Sales Team Meeting Breakdown",
                text='Count'
            )
            fig_sales.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1a202c', family='Inter', size=14, weight=600),
                title_font_size=18,
                title_font_color='#1a202c',
                title_font_weight=800,
                margin=dict(l=50, r=50, t=100, b=50),
                xaxis=dict(
                    tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600),
                    title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                    showgrid=False
                ),
                yaxis=dict(
                    tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600),
                    title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                    showgrid=False
                ),
                legend=dict(
                    bgcolor='rgba(255,255,255,0.95)', 
                    font=dict(color='#1a202c', size=14, family='Inter', weight=600),
                    bordercolor='#1a202c',
                    borderwidth=1
                )
            )
            fig_sales.update_traces(
                hovertemplate="<b>%{x}</b><br>Status: %{fullData.name}<br>Count: %{y}<extra></extra>",
                textposition='outside',
                textfont=dict(size=12, color='#1a202c', family='Inter', weight=600)
            )
            st.plotly_chart(fig_sales, use_container_width=True)
            
            # Team summary table
            st.markdown("**📊 Team Summary Metrics**")
            st.dataframe(team_summary, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Row 4: Account Executive Analysis
        if 'AE' in filtered_df.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Check if Company column exists for more robust analysis
            company_col = 'Company' if 'Company' in filtered_df.columns else None
            
            # AE performance metrics - handle missing Company column
            if company_col:
                ae_summary = filtered_df.groupby('AE').agg({
                    'Status': ['count', lambda x: (x.str.lower() == 'done').sum()],
                    company_col: 'nunique'
                }).round(2)
                ae_summary.columns = ['Total_Demos', 'Completed_Demos', 'Unique_Companies']
            else:
                ae_summary = filtered_df.groupby('AE').agg({
                    'Status': ['count', lambda x: (x.str.lower() == 'done').sum()]
                }).round(2)
                ae_summary.columns = ['Total_Demos', 'Completed_Demos']
            
            ae_summary['Success_Rate'] = (ae_summary['Completed_Demos'] / ae_summary['Total_Demos'] * 100).round(1)
            ae_summary = ae_summary.reset_index()
            
            ae_status_counts = filtered_df.groupby(['AE', 'Status']).size().reset_index(name='Count')
            fig_ae = px.bar(
                ae_status_counts, 
                x='AE', 
                y='Count', 
                color='Status',
                barmode='group', 
                color_discrete_sequence=['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe', '#eff6ff'],
                title="AE Meeting Breakdown",
                text='Count'
            )
            fig_ae.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1a202c', family='Inter', size=14, weight=600),
                title_font_size=18,
                title_font_color='#1a202c',
                title_font_weight=800,
                margin=dict(l=50, r=50, t=100, b=50),
                xaxis=dict(
                    tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600), 
                    tickangle=45,
                    title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                    showgrid=False
                ),
                yaxis=dict(
                    tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600),
                    title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                    showgrid=False
                ),
                legend=dict(
                    bgcolor='rgba(255,255,255,0.95)', 
                    font=dict(color='#1a202c', size=14, family='Inter', weight=600),
                    bordercolor='#1a202c',
                    borderwidth=1
                )
            )
            fig_ae.update_traces(
                hovertemplate="<b>%{x}</b><br>Status: %{fullData.name}<br>Count: %{y}<extra></extra>",
                textposition='outside',
                textfont=dict(size=12, color='#1a202c', family='Inter', weight=600)
            )
            st.plotly_chart(fig_ae, use_container_width=True)
            
            # AE leaderboard
            st.markdown("**🏆 AE Summary Metrics**")
            leaderboard = ae_summary.sort_values('Success_Rate', ascending=False).head(10)
            st.dataframe(leaderboard, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Row 5: Time-based Analysis
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Create time-based metrics
        daily_data = filtered_df.groupby(filtered_df['Date'].dt.date).agg({
            'Status': ['count', lambda x: (x.str.lower() == 'done').sum()]
        }).reset_index()
        daily_data.columns = ['Date', 'Total_Demos', 'Completed_Demos']
        daily_data['Completion_Rate'] = (daily_data['Completed_Demos'] / daily_data['Total_Demos'] * 100).round(1)
        
        # Time series chart
        fig_timeline = go.Figure()
        
        # Add total demos line
        fig_timeline.add_trace(go.Scatter(
            x=daily_data['Date'],
            y=daily_data['Total_Demos'],
            mode='lines+markers',
            name='Total Demos',
            line=dict(color='#1e40af', width=3),
            marker=dict(size=6)
        ))
        
        # Add completed demos line
        fig_timeline.add_trace(go.Scatter(
            x=daily_data['Date'],
            y=daily_data['Completed_Demos'],
            mode='lines+markers',
            name='Completed Demos',
            line=dict(color='#10b981', width=3),
            marker=dict(size=6)
        ))
        
        fig_timeline.update_layout(
            title="Daily Demo Activity Trends",
            title_font_size=18,
            title_font_color='#1a202c',
            title_font_weight=800,
            xaxis_title="Date",
            yaxis_title="Number of Demos",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1a202c', family='Inter', size=14, weight=600),
            margin=dict(l=50, r=50, t=100, b=50),
            xaxis=dict(
                tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600),
                title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                showgrid=False
            ),
            yaxis=dict(
                tickfont=dict(size=13, color='#1a202c', family='Inter', weight=600),
                title_font=dict(color='#1a202c', size=14, family='Inter', weight=700),
                showgrid=False
            ),
            legend=dict(
                bgcolor='rgba(255,255,255,0.95)', 
                x=0.02, 
                y=0.98,
                font=dict(color='#1a202c', size=14, family='Inter', weight=600),
                bordercolor='#1a202c',
                borderwidth=1
            )
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.warning("⚠️ **No data matches your current filters**\n\nTry adjusting your filter criteria to see results.")
        st.markdown("**💡 Suggestions:**")
        st.markdown("- Expand your date range")
        st.markdown("- Select 'All' for some filters")
        st.markdown("- Check data source connectivity")
        st.markdown('</div>', unsafe_allow_html=True)
        
elif data_source == "Upload Excel File":
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📁 **File Upload Center**")
    st.info("🚀 **Ready to analyze your data!**\n\nUpload your Excel file using the sidebar to get started with advanced analytics.")
    st.markdown("**📋 Required columns for full functionality:**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- **Date** (required)")
        st.markdown("- **SDR** (required)")
        st.markdown("- **Status** (required)")
        st.markdown("- **Company**")
    with col2:
        st.markdown("- **Industry**")
        st.markdown("- **Source**")
        st.markdown("- **Sales Team**")
        st.markdown("- **AE** (Account Executive)")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.info("📊 **Connecting to Google Sheets...**\n\nPlease wait while we load your data.")
    st.markdown('</div>', unsafe_allow_html=True)

# Simple footer for file mode only
if data_source != "Google Sheets (Auto-Update)":
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: #1e40af; font-size: 0.9rem;">
        📊 Marketing Sourced Meeting Dashboard
    </div>
    """, unsafe_allow_html=True)