import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
import requests
from io import StringIO
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Interactive Dashboard", layout="wide")

# Function to load data from Google Sheets
@st.cache_data(ttl=300)  # Cache for 5 minutes (300 seconds) - auto-refresh
def load_google_sheets_data():
    """Load data from Google Sheets with auto-refresh every 5 minutes"""
    try:
        # Convert your Google Sheets URL to CSV export format
        sheet_id = "1vR2-ynySfxqoXOra8yMSUO3x5AjlOp42soc2FhE4TySJ9to825OpNCODiIcF70pmv_jI0li4xE5qJ7r"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        
        response = requests.get(csv_url)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df, None
        else:
            return None, "Failed to fetch data from Google Sheets"
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

# Sidebar - Data source and filters
with st.sidebar:
    st.title("📊 Data Source & Filters")
    
    # Data source selection
    data_source = st.radio(
        "Choose Data Source:",
        ["Google Sheets (Auto-Update)", "Upload Excel File"]
    )
    
    if data_source == "Google Sheets (Auto-Update)":
        st.success("✅ Connected to Google Sheets")
        
        # Show last update time
        current_time = datetime.now().strftime("%H:%M:%S")
        st.info(f"🕐 Auto-refreshes every 5 minutes\nLast checked: {current_time}")
        
        # Manual refresh button
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
        
        # Load data from Google Sheets
        df, error = load_google_sheets_data()
        
        if error:
            st.error(f"❌ {error}")
            st.stop()
        elif df is None:
            st.error("❌ No data loaded from Google Sheets")
            st.stop()
        else:
            st.success(f"✅ Loaded {len(df)} rows from Google Sheets")
    
    else:
        # Original file upload functionality
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
        else:
            df = None

    # Proceed only if data is available
    if df is not None and not df.empty:
        # Check for required columns
        if 'Date' not in df.columns:
            st.error("❌ The data does not contain a 'Date' column.")
            st.stop()

        if 'SDR' not in df.columns:
            st.error("❌ The data does not contain a 'SDR' column.")
            st.stop()

        # Parse dates and standardize format
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Formatted Date'] = df['Date'].dt.strftime('%d/%m/%Y')  # For optional display

        # Extract Month names safely (fix for TypeError)
        df['Month'] = df['Date'].dt.month
        df['Month'] = df['Month'].apply(lambda x: calendar.month_name[int(x)] if pd.notnull(x) else None)

        # Extract Week number
        df['Week'] = df['Date'].dt.isocalendar().week

        # Filters
        st.subheader("🔍 Filters")
        
        sdrs = sorted(df['SDR'].dropna().unique())
        selected_sdr = st.selectbox("Select SDR", options=["All"] + sdrs)

        statuses = sorted(df['Status'].dropna().unique())
        selected_status = st.selectbox("Select Status", options=["All"] + statuses)

        # Month filter dropdown - exclude None values
        months = [m for m in df['Month'].dropna().unique()]
        months_sorted = sorted(months, key=lambda m: list(calendar.month_name).index(m))
        selected_month = st.selectbox("Select Month", options=["All"] + months_sorted)

        # Week filter dropdown
        weeks = sorted(df['Week'].dropna().unique())
        selected_week = st.selectbox("Select Week Number", options=["All"] + weeks)

        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        from_date = st.date_input("From Date", min_value=min_date, max_value=max_date, value=min_date)
        to_date = st.date_input("To Date", min_value=min_date, max_value=max_date, value=max_date)

        # Apply filters
        filtered_df = df[
            (df['Date'].dt.date >= from_date) &
            (df['Date'].dt.date <= to_date)
        ]

        if selected_sdr != "All":
            filtered_df = filtered_df[filtered_df['SDR'] == selected_sdr]

        if selected_status != "All":
            filtered_df = filtered_df[filtered_df['Status'] == selected_status]

        if selected_month != "All":
            filtered_df = filtered_df[filtered_df['Month'] == selected_month]

        if selected_week != "All":
            filtered_df = filtered_df[filtered_df['Week'] == selected_week]

    else:
        filtered_df = None

# Main page content
st.title("📊 Interactive Dashboard")

# Add data source indicator in main area
if df is not None:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if data_source == "Google Sheets (Auto-Update)":
            st.success("📡 Live data from Google Sheets")
        else:
            st.info("📁 Data from uploaded file")
    with col2:
        st.metric("Total Records", len(df))
    with col3:
        st.metric("Filtered Records", len(filtered_df) if filtered_df is not None else 0)

if df is not None and filtered_df is not None:
    st.subheader("Filtered Data Table")
    if 'SDR' in filtered_df.columns:
        # Drop columns carefully (only if exist)
        cols_to_drop = ['SDR','Contact Name','Title','Sales Accepted?','Remarks','Meeting Transcript','Formatted Date',"Month","Week"]
        cols_to_drop = [col for col in cols_to_drop if col in filtered_df.columns]
        st.dataframe(filtered_df.drop(columns=cols_to_drop), height=300)
    else:
        st.dataframe(filtered_df, height=300)

    if not filtered_df.empty:
        # === KPI Section ===
        col1, col2 = st.columns(2)

        with col1:
            completed_count = filtered_df[filtered_df['Status'].str.lower() == 'done'].shape[0]
            st.metric(label="✅ Demo Done Status Count", value=completed_count)

        with col2:
            scheduled_statuses = ['done', 'scheduled', 'rescheduled']
            scheduled_count = filtered_df[filtered_df['Status'].str.lower().isin(scheduled_statuses)].shape[0]
            st.metric(label="📅 Demo Scheduled Count", value=scheduled_count)

        # === Status Distribution Bar Chart ===
        st.subheader("Status Distribution")
        status_count = filtered_df['Status'].value_counts().reset_index()
        status_count.columns = ['Status', 'Count']
        bar_fig = px.bar(status_count, x='Status', y='Count', title="Status Count")
        st.plotly_chart(bar_fig, use_container_width=True)

        # === Industry Pie Chart ===
        st.subheader("Industry Distribution")
        if 'Industry' in filtered_df.columns:
            pie_data = filtered_df['Industry'].value_counts().reset_index()
            pie_data.columns = ['Industry', 'Count']
            pie_fig = px.pie(pie_data, names='Industry', values='Count', title="Industry Share")
            st.plotly_chart(pie_fig, use_container_width=True)
        else:
            st.info("No 'Industry' data available for pie chart.")

        # === Grouped Bar Chart: Sales Team vs Status ===
        if 'Sales Team' in filtered_df.columns:
            st.subheader("Sales Team vs Status")
            sales_status_counts = filtered_df.groupby(['Sales Team', 'Status']).size().reset_index(name='Count')
            fig_sales = px.bar(sales_status_counts, x='Sales Team', y='Count', color='Status',
                               barmode='group', title="Sales Team-wise Status Distribution")
            st.plotly_chart(fig_sales, use_container_width=True)

        # === Grouped Bar Chart: AE vs Status ===
        if 'AE' in filtered_df.columns:
            st.subheader("AE vs Status")
            ae_status_counts = filtered_df.groupby(['AE', 'Status']).size().reset_index(name='Count')
            fig_ae = px.bar(ae_status_counts, x='AE', y='Count', color='Status',
                            barmode='group', title="AE-wise Status Distribution")
            st.plotly_chart(fig_ae, use_container_width=True)

    else:
        st.warning("No data available for selected filters.")
        
elif data_source == "Upload Excel File":
    st.info("Please upload an Excel file to begin.")
else:
    st.info("Loading data from Google Sheets...")

# Footer with update information
if data_source == "Google Sheets (Auto-Update)":
    st.markdown("---")
    st.caption("🔄 Dashboard automatically updates every 5 minutes | 📊 Data synced with Google Sheets")
