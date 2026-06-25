import streamlit as st
import os
import pandas as pd
import json
from dotenv import load_dotenv

# Load env variables if .env exists
load_dotenv()

# Set page configuration with premium title and icon
st.set_page_config(
    page_title="AI Data Analyst Team",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium aesthetics, modern fonts, card layouts, and subtle animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }
    
    .main-title {
        font-size: 3rem;
        background: linear-gradient(135deg, #26A69A 0%, #1E88E5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #718096;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f7fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.05);
        border-color: #cbd5e0;
    }
    
    .metric-val {
        font-size: 2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-top: 0.5rem;
    }
    
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .agent-coordinator { background-color: #E0F2F1; color: #00695C; }
    .agent-cleaning { background-color: #E3F2FD; color: #1565C0; }
    .agent-insight { background-color: #EDE7F6; color: #4527A0; }
    .agent-report { background-color: #FFF3E0; color: #EF6C00; }
    
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown("<h1 class='main-title'>📊 AI Data Analyst Team</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Empowering Small Businesses with Multi-Agent Sales Analysis & Executive Reporting</p>", unsafe_allow_html=True)

# Setup Sidebar for API key input and options
st.sidebar.header("🛠️ Configuration")

# API Key Validation and input
env_api_key = os.environ.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Gemini API Key", value=env_api_key, type="password", help="Enter your Gemini API key. Alternatively, set the GEMINI_API_KEY environment variable.")

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key
    st.sidebar.success("🔑 API Key configured!")
else:
    st.sidebar.warning("⚠️ Please provide a Gemini API Key to run agent analyses.")

# Advanced model selection
model_option = st.sidebar.selectbox(
    "Select LLM Model",
    options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
    index=0
)
os.environ["GEMINI_MODEL"] = model_option

# File Uploader Section
st.header("📂 1. Upload Sales Dataset")

uploaded_file = st.file_uploader(
    "Drag and drop your sales transaction CSV file here", 
    type=["csv"],
    help="CSV file size limit is 10 MB. File must contain date, product name, quantity, price, or revenue columns."
)

if uploaded_file is not None:
    # --- SECURITY CHECK: File Size Limit ---
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > 10.0:
        st.error(f"❌ File size exceeds 10 MB limit (Current: {file_size_mb:.2f} MB). Please upload a smaller file.")
    else:
        # Load and Preview the dataset safely
        try:
            df_preview = pd.read_csv(uploaded_file)
            
            # --- SECURITY CHECK: Input Structure Validation ---
            cols = [c.lower() for c in df_preview.columns]
            has_product = any(x in cols for x in ['product', 'item', 'name'])
            has_sales = any(x in cols for x in ['revenue', 'sales', 'total', 'price', 'rate'])
            
            st.success(f"✅ Successful uploaded '{uploaded_file.name}' ({len(df_preview)} rows, {len(df_preview.columns)} columns)")
            
            st.subheader("👀 Dataset Preview")
            st.dataframe(df_preview.head(8), use_container_width=True)
            
            if not (has_product and has_sales):
                st.warning("⚠️ Warning: Your dataset columns don't seem to contain typical sales headers like 'Product' and 'Price'/'Revenue'. Calculations might fail or be incomplete.")
                
            # Create action buttons
            st.header("⚡ 2. Execute Multi-Agent Analysis")
            
            if st.button("Run Data Analyst Team", type="primary", disabled=not api_key):
                # Save uploaded file temporarily to data/ folder
                os.makedirs("data", exist_ok=True)
                import time

                temp_file_path = os.path.join(
                  "data",
                f"uploaded_dataset_{int(time.time())}.csv"
      )
                
                # Write file safely
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Import coordinator here to prevent import errors during initialization
                try:
                    from agents.coordinator_agent import run_analyst_team
                    
                    with st.spinner("🤖 Orchestrating AI Data Analyst Team (this may take a minute)..."):
                        # Phase 1: Data Cleaning
                        status_clean = st.empty()
                        status_clean.info("🧹 Data Cleaning Agent: Inspecting dataset schema & duplicates...")
                        
                        # Run the team workflow
                        pipeline_results = run_analyst_team(temp_file_path)
                        
                        if "error" in pipeline_results:
                            st.error(f"❌ Analysis failed: {pipeline_results['error']}")
                        else:
                            status_clean.success("🧹 Data Cleaning Agent: Finished profiling!")
                            
                            # Renders Results tabs
                            st.balloons()
                            st.header("📈 3. Analysis Results")
                            
                            tab1, tab2, tab3 = st.tabs(["🧹 Data Quality Summary", "📊 Metrics & Visualizations", "📄 Executive Report"])
                            
                            with tab1:
                                st.markdown("<span class='agent-badge agent-cleaning'>Data Cleaning Agent</span>", unsafe_allow_html=True)
                                st.markdown(pipeline_results["cleaning_summary_ai"])
                                
                                # Show technical metrics dictionary
                                with st.expander("Show Technical Quality Dictionary"):
                                    st.json(pipeline_results["clean_summary_dict"])
                                    
                            with tab2:
                                st.markdown("<span class='agent-badge agent-insight'>Insight Agent</span>", unsafe_allow_html=True)
                                
                                # Render Key Metrics in cards
                                metrics_dict = pipeline_results.get("insights_data_dict", {}).get("metrics", {})
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown(f"""
                                    <div class='metric-card'>
                                        <div><strong>Total Revenue</strong></div>
                                        <div class='metric-val'>${metrics_dict.get('total_revenue', 0.0):,.2f}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    st.markdown(f"""
                                    <div class='metric-card'>
                                        <div><strong>Total Orders</strong></div>
                                        <div class='metric-val'>{metrics_dict.get('total_transactions', 0):,}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col3:
                                    st.markdown(f"""
                                    <div class='metric-card'>
                                        <div><strong>Average Order Value</strong></div>
                                        <div class='metric-val'>${metrics_dict.get('average_transaction_value', 0.0):,.2f}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                st.markdown("### Visualizations")
                                charts = pipeline_results.get("insights_data_dict", {}).get("charts", {})
                                
                                # Display side-by-side charts
                                v_col1, v_col2 = st.columns(2)
                                with v_col1:
                                    if "revenue_trend" in charts and os.path.exists(charts["revenue_trend"]):
                                        st.image(charts["revenue_trend"], caption="Monthly Revenue Trend", use_container_width=True)
                                    else:
                                        st.warning("Revenue trend chart not available.")
                                with v_col2:
                                    if "top_products" in charts and os.path.exists(charts["top_products"]):
                                        st.image(charts["top_products"], caption="Top Products Performance", use_container_width=True)
                                    else:
                                        st.warning("Top products chart not available.")
                                        
                                st.markdown("### Strategic Observations")
                                st.markdown(pipeline_results["insight_summary_ai"])
                                
                            with tab3:
                                st.markdown("<span class='agent-badge agent-report'>Report Agent</span>", unsafe_allow_html=True)
                                
                                report_md = pipeline_results.get("final_report_markdown", "")
                                st.markdown(report_md)
                                
                                # Download Report Button
                                st.markdown("### 📥 Download Executive Report")
                                st.download_button(
                                    label="Download Report as Markdown",
                                    data=report_md,
                                    file_name="executive_sales_report.md",
                                    mime="text/markdown",
                                    key="download-report"
                                )
                                
                except Exception as e:
                    st.error(f"❌ Error during multi-agent orchestration: {str(e)}")
                    st.exception(e)
            elif not api_key:
                st.info("💡 Enter your Gemini API Key in the sidebar to activate the button.")
                
        except Exception as e:
            st.error(f"❌ Failed to parse uploaded CSV: {str(e)}")
            st.info("Please make sure the CSV is not malformed and uses comma delimiters.")
else:
    # Friendly empty state helper
    st.info("ℹ️ Upload a sales transaction CSV file to get started. You can use the pre-generated sample dataset in the project repository under `data/sample_sales.csv` for a demonstration!")
