import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
import requests
from io import StringIO
from datetime import datetime
import hashlib

# Page configuration
st.set_page_config(page_title="Interactive Dashboard", layout="wide")

# Function to load data from Google Sheets with better caching and error handling
@st.cache_data(ttl=60)  # Reduced to 1 minute for more frequent updates
def load_google_sheets_data():
    """Load data from Google Sheets with better error handling and freshness check"""
    try:
        # Use the correct CSV export URL for your published sheet
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2-ynySfxqoXOra8yMSUO3x5AjlOp42soc2FhE4TySJ9to825OpNCODiIcF70pmv_jI0li4xE5qJ7r/pub?gid=0&single=true&output=csv"
        
        # Add timestamp to force fresh data
        timestamped_url = f"{csv_url}&t={int(datetime.now().timestamp())}"
        
        response = requests.get(timestamped_url, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            
            # Add data freshness check
            data_hash = hashlib.md5(response.text.encode()).hexdigest()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return df, None, data_hash, timestamp
        else:
            return None, f"Failed to fetch data. Status code: {response.status_code}", None, None
    except Exception as e:
        return None, f"Error loading data: {str(e)}", None, None

# Function to force cache clear
def clear_cache_and_reload():
    """Clear cache and reload data"""
    st.cache_data.clear()
    st.rerun()

# Initialize session state for tracking data changes
if 'last_data_hash' not in st.session_state:
    st.session_state.last_data_hash = None
if 'data_update_count' not in st.session_state:
    st.session_state.data_update_count = 0

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
        
        # Manual refresh button (more prominent)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Force Refresh", type="primary"):
                clear_cache_and_reload()
        with col2:
            if st.button("🗑️ Clear Cache"):
                st.cache_data.clear()
                st.success("Cache cleared!")
        
        # Load data from Google Sheets
        df, error, data_hash, last_update = load_google_sheets_data()
        
        # Check if data has changed
        if data_hash and st.session_state.last_data_hash != data_hash:
            st.session_state.last_data_hash = data_hash
            st.session_state.data_update_count += 1
        
        # Show data freshness info
        if last_update:
            st.info(f"🕐 Last Updated: {last_update}")
            st.info(f"🔄 Updates: {st.session_state.data_update_count}")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh every 30 seconds", value=False)
        if auto_refresh:
            st.rerun()
        
        if error:
            st.error(f"❌ {error}")
            st.error("**Troubleshooting Tips:**")
            st.error("1. Check if Google Sheet is published")
            st.error("2. Verify the sheet URL is correct")
            st.error("3. Try the Force Refresh button")
            st.stop()
        elif df is None:
            st.error("❌ No data loaded from Google Sheets")
            st.stop()
        else:
            st.success(f"✅ Loaded {len(df)} rows")
            
            # Show data preview for debugging
            with st.expander("🔍 Debug: Data Preview"):
                st.write("**Column Names:**", list(df.columns))
                st.write("**Data Types:**", df.dtypes.to_dict())
                st.write("**First 3 rows:**")
                st.dataframe(df.head(3))
    
    else:
        # Original file upload functionality
        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
        else:
            df = None

    # Proceed only if data is available
    if df is not None and not df.empty:
        # Check for required columns with better error messages
        required_columns = ['Date', 'SDR']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Missing required columns: {missing_columns}")
            st.error(f"Available columns: {list(df.columns)}")
            st.stop()

        # Data preprocessing with error handling
        try:
            # Parse dates and standardize format
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Check for invalid dates
            invalid_dates = df['Date'].isna().sum()
            if invalid_dates > 0:
                st.warning(f"⚠️ Found {invalid_dates} invalid dates")
            
            df['Formatted Date'] = df['Date'].dt.strftime('%d/%m/%Y')

            # Extract Month names safely
            df['Month'] = df['Date'].dt.month
            df['Month'] = df['Month'].apply(lambda x: calendar.month_name[int(x)] if pd.notnull(x) else None)

            # Extract Week number
            df['Week'] = df['Date'].dt.isocalendar().week

        except Exception as e:
            st.error(f"❌ Error processing data: {str(e)}")
            st.stop()

        # Filters
        st.subheader("🔍 Filters")
        
        # SDR filter with error handling
        try:
            sdrs = sorted(df['SDR'].dropna().unique())
            selected_sdr = st.selectbox("Select SDR", options=["All"] + sdrs)
        except Exception as e:
            st.error(f"Error with SDR filter: {str(e)}")
            selected_sdr = "All"

        # Status filter with error handling
        try:
            if 'Status' in df.columns:
                statuses = sorted(df['Status'].dropna().unique())
                selected_status = st.selectbox("Select Status", options=["All"] + statuses)
            else:
                selected_status = "All"
                st.warning("⚠️ No 'Status' column found")
        except Exception as e:
            st.error(f"Error with Status filter: {str(e)}")
            selected_status = "All"

        # Month filter with error handling
        try:
            months = [m for m in df['Month'].dropna().unique() if m is not None]
            months_sorted = sorted(months, key=lambda m: list(calendar.month_name).index(m))
            selected_month = st.selectbox("Select Month", options=["All"] + months_sorted)
        except Exception as e:
            st.error(f"Error with Month filter: {str(e)}")
            selected_month = "All"

        # Week filter
        try:
            weeks = sorted(df['Week'].dropna().unique())
            selected_week = st.selectbox("Select Week Number", options=["All"] + weeks)
        except Exception as e:
            st.error(f"Error with Week filter: {str(e)}")
            selected_week = "All"

        # Date range filter
        try:
            valid_dates = df['Date'].dropna()
            if len(valid_dates) > 0:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()
                from_date = st.date_input("From Date", min_value=min_date, max_value=max_date, value=min_date)
                to_date = st.date_input("To Date", min_value=min_date, max_value=max_date, value=max_date)
            else:
                st.error("No valid dates found in data")
                from_date = to_date = datetime.now().date()
        except Exception as e:
            st.error(f"Error with date filters: {str(e)}")
            from_date = to_date = datetime.now().date()

        # Apply filters with error handling
        try:
            filtered_df = df[
                (df['Date'].dt.date >= from_date) &
                (df['Date'].dt.date <= to_date)
            ]

            if selected_sdr != "All":
                filtered_df = filtered_df[filtered_df['SDR'] == selected_sdr]

            if selected_status != "All" and 'Status' in df.columns:
                filtered_df = filtered_df[filtered_df['Status'] == selected_status]

            if selected_month != "All":
                filtered_df = filtered_df[filtered_df['Month'] == selected_month]

            if selected_week != "All":
                filtered_df = filtered_df[filtered_df['Week'] == selected_week]

        except Exception as e:
            st.error(f"Error applying filters: {str(e)}")
            filtered_df = df

    else:
        filtered_df = None

# Main page content
st.title("📊 Interactive Dashboard")

# Add data source indicator in main area
if df is not None:
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        if data_source == "Google Sheets (Auto-Update)":
            st.success("📡 Live data from Google Sheets")
        else:
            st.info("📁 Data from uploaded file")
    with col2:
        st.metric("Total Records", len(df))
    with col3:
        st.metric("Filtered Records", len(filtered_df) if filtered_df is not None else 0)
    with col4:
        if data_source == "Google Sheets (Auto-Update)":
            st.metric("Data Updates", st.session_state.data_update_count)

# Rest of your visualization code remains the same...
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
            if 'Status' in filtered_df.columns:
                completed_count = filtered_df[filtered_df['Status'].str.lower() == 'done'].shape[0]
                st.metric(label="✅ Demo Done Status Count", value=completed_count)
            else:
                st.metric(label="✅ Demo Done Status Count", value="N/A")

        with col2:
            if 'Status' in filtered_df.columns:
                scheduled_statuses = ['done', 'scheduled', 'rescheduled']
                scheduled_count = filtered_df[filtered_df['Status'].str.lower().isin(scheduled_statuses)].shape[0]
                st.metric(label="📅 Demo Scheduled Count", value=scheduled_count)
            else:
                st.metric(label="📅 Demo Scheduled Count", value="N/A")

        # === Status Distribution Bar Chart ===
        if 'Status' in filtered_df.columns:
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
        if 'Sales Team' in filtered_df.columns and 'Status' in filtered_df.columns:
            st.subheader("Sales Team vs Status")
            sales_status_counts = filtered_df.groupby(['Sales Team', 'Status']).size().reset_index(name='Count')
            fig_sales = px.bar(sales_status_counts, x='Sales Team', y='Count', color='Status',
                               barmode='group', title="Sales Team-wise Status Distribution")
            st.plotly_chart(fig_sales, use_container_width=True)

        # === Grouped Bar Chart: AE vs Status ===
        if 'AE' in filtered_df.columns and 'Status' in filtered_df.columns:
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
    st.caption("🔄 Dashboard updates every minute | 📊 Data synced with Google Sheets")
    
# Debug section (remove in production)
if st.checkbox("🔧 Show Debug Info"):
    st.subheader("Debug Information")
    st.write("**Session State:**", dict(st.session_state))
    if df is not None:
        st.write("**Data Shape:**", df.shape)
        st.write("**Last Data Hash:**", st.session_state.last_data_hash)
