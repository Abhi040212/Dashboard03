import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
import requests
from io import StringIO
from datetime import datetime
import hashlib
import time
import random

# Page configuration
st.set_page_config(page_title="Interactive Dashboard", layout="wide")

# Enhanced Google Sheets data fetching with multiple strategies
@st.cache_data(ttl=10)  # Very short cache - 10 seconds
def load_google_sheets_data_enhanced():
    """Enhanced Google Sheets data loading with multiple fallback strategies"""
    
    # Your sheet ID - UPDATED with your correct sheet ID
    sheet_id = "1XtQWQXzn8OAr52yJIH39nSFbwRx74JQAifol85Var1A"
    
    # Multiple URL strategies to try
    strategies = [
        {
            "name": "Direct Export with Cache Busting",
            "url": f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0&cachebust={int(time.time())}&rand={random.randint(1000,9999)}"
        },
        {
            "name": "Published CSV with Headers",
            "url": f"https://docs.google.com/spreadsheets/d/e/2PACX-{sheet_id}/pub?gid=0&single=true&output=csv&headers=false&t={int(time.time())}"
        },
        {
            "name": "Published CSV Original",
            "url": f"https://docs.google.com/spreadsheets/d/e/2PACX-{sheet_id}/pub?gid=0&single=true&output=csv"
        },
        {
            "name": "TSV Format (Alternative)",
            "url": f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=tsv&gid=0&cachebust={int(time.time())}"
        }
    ]
    
    # Headers to simulate real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/csv,application/csv,text/plain,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for strategy in strategies:
        try:
            st.write(f"🔄 Trying: {strategy['name']}")
            
            # Make request with longer timeout
            response = requests.get(
                strategy['url'], 
                headers=headers, 
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                content = response.text.strip()
                
                # Check if we got HTML error page instead of CSV
                if content.startswith('<!DOCTYPE') or content.startswith('<html') or '<html>' in content:
                    st.warning(f"❌ {strategy['name']}: Got HTML instead of CSV")
                    continue
                
                # Check if content looks like CSV
                if len(content) < 50:  # Too short to be real data
                    st.warning(f"❌ {strategy['name']}: Content too short ({len(content)} chars)")
                    continue
                
                # Try to parse as CSV
                try:
                    if strategy['name'] == "TSV Format (Alternative)":
                        df = pd.read_csv(StringIO(content), sep='\t')
                    else:
                        df = pd.read_csv(StringIO(content))
                    
                    # Validate data structure
                    if len(df.columns) < 2:
                        st.warning(f"❌ {strategy['name']}: Too few columns ({len(df.columns)})")
                        continue
                    
                    if len(df) < 1:
                        st.warning(f"❌ {strategy['name']}: No data rows")
                        continue
                    
                    # Check for required columns (made more flexible)
                    required_cols = ['Date', 'SDR']
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    if missing_cols:
                        st.warning(f"❌ {strategy['name']}: Missing columns: {missing_cols}")
                        st.info(f"Available columns: {list(df.columns)}")
                        # Continue anyway - maybe the column names are different
                    
                    # Success!
                    data_hash = hashlib.md5(content.encode()).hexdigest()
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    st.success(f"✅ Success with: {strategy['name']}")
                    return df, None, data_hash, timestamp, strategy['name']
                    
                except Exception as parse_error:
                    st.warning(f"❌ {strategy['name']}: Parse error - {str(parse_error)}")
                    continue
            else:
                st.warning(f"❌ {strategy['name']}: HTTP {response.status_code}")
                continue
                
        except Exception as e:
            st.warning(f"❌ {strategy['name']}: {str(e)}")
            continue
    
    # If all strategies failed
    return None, "All data fetching strategies failed", None, None, None

# Alternative: Direct Google Sheets API approach (if you want to set up API)
def setup_google_sheets_api_instructions():
    """Instructions for setting up proper Google Sheets API"""
    st.info("""
    **🔧 For Most Reliable Solution - Google Sheets API:**
    
    1. **Enable Google Sheets API:**
       - Go to Google Cloud Console
       - Create/select a project
       - Enable Google Sheets API
    
    2. **Create Service Account:**
       - Create service account key (JSON)
       - Share your Google Sheet with service account email
    
    3. **Install required package:**
       ```bash
       pip install gspread google-auth
       ```
    
    4. **Replace CSV method with API method**
    """)

# Main app with enhanced Google Sheets loading
def main():
    st.title("📊 Dashboard with Enhanced Google Sheets")
    
    # Important note about sheet permissions
    st.info("""
    **📋 Important:** Make sure your Google Sheet is set to "Anyone with the link can view" 
    for the CSV export to work properly.
    """)
    
    # Sidebar for controls
    with st.sidebar:
        st.title("📊 Data Controls")
        
        # Show current sheet ID
        st.code("Sheet ID: 1XtQWQXzn8OAr52yJIH39nSFbwRx74JQAifol85Var1A")
        
        # Force refresh button
        if st.button("🔄 Force Fresh Data", type="primary"):
            # Clear cache and reload
            st.cache_data.clear()
            st.rerun()
        
        # Show API setup option
        if st.checkbox("🔧 Show Google Sheets API Setup"):
            setup_google_sheets_api_instructions()
        
        st.markdown("---")
        
        # Load data
        with st.spinner("Loading data from Google Sheets..."):
            df, error, data_hash, last_update, method_used = load_google_sheets_data_enhanced()
        
        if error:
            st.error(f"❌ Error: {error}")
            
            # Show manual alternatives
            st.markdown("**Manual Alternatives:**")
            st.markdown("1. Download CSV from Google Sheets")
            st.markdown("2. Upload using file uploader below")
            
            uploaded_file = st.file_uploader("📁 Upload CSV as backup", type=['csv'])
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(df)} rows from upload")
                method_used = "Manual Upload"
            else:
                st.stop()
        
        elif df is None:
            st.error("No data available")
            st.stop()
        else:
            # Show success info
            st.success(f"✅ Data loaded successfully!")
            st.info(f"📊 Rows: {len(df)}")
            st.info(f"📅 Updated: {last_update}")
            st.info(f"🔧 Method: {method_used}")
            
            # Data validation
            with st.expander("🔍 Data Validation"):
                st.write("**Columns:**", list(df.columns))
                if 'Status' in df.columns:
                    status_counts = df['Status'].value_counts()
                    st.write("**Status Distribution:**")
                    for status, count in status_counts.items():
                        st.write(f"  - {status}: {count}")
                
                # Show sample data
                st.write("**Sample Data:**")
                st.dataframe(df.head(3))
    
    # Main content area
    if df is not None and not df.empty:
        # Data processing (flexible column handling)
        # Parse dates - try common date column names
        date_cols = ['Date', 'date', 'DATE', 'Created', 'Timestamp']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break
        
        if date_col:
            df['Date'] = pd.to_datetime(df[date_col], errors='coerce')
            df['Month'] = df['Date'].dt.month
            df['Month'] = df['Month'].apply(lambda x: calendar.month_name[int(x)] if pd.notnull(x) else None)
            df['Week'] = df['Date'].dt.isocalendar().week
        
        # Show current status counts prominently
        status_cols = ['Status', 'status', 'STATUS', 'State']
        status_col = None
        for col in status_cols:
            if col in df.columns:
                status_col = col
                break
        
        if status_col:
            st.subheader("📊 Current Status Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_records = len(df)
                st.metric("Total Records", total_records)
            
            with col2:
                done_count = df[df[status_col].str.strip().str.lower() == 'done'].shape[0]
                st.metric("✅ Done", done_count)
            
            with col3:
                scheduled_statuses = ['done', 'scheduled', 'rescheduled']
                scheduled_count = df[df[status_col].str.strip().str.lower().isin(scheduled_statuses)].shape[0]
                st.metric("📅 Scheduled", scheduled_count)
            
            with col4:
                if method_used:
                    st.metric("🔧 Method", method_used)
            
            # Status distribution chart
            st.subheader("Status Distribution")
            status_counts = df[status_col].value_counts()
            fig = px.bar(
                x=status_counts.index, 
                y=status_counts.values,
                title=f"Current {status_col} Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Show raw data
        st.subheader("Raw Data")
        st.dataframe(df, height=400)
        
        # Add refresh reminder
        st.markdown("---")
        st.caption(f"🔄 Data last refreshed: {last_update} | 🔧 Method: {method_used}")
        st.caption("💡 Click 'Force Fresh Data' if numbers seem outdated")

if __name__ == "__main__":
    main()