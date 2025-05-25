# streamlit_frontend.py
"""
Streamlit frontend for orthopedic competitive intelligence
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, Any
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="Orthopedic Competitive Intelligence",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException:
        return False, None

def start_analysis(competitors: list, focus_area: str) -> Dict[str, Any]:
    """Start competitive analysis via API"""
    try:
        payload = {
            "competitors": competitors,
            "focus_area": focus_area
        }
        response = requests.post(
            f"{API_BASE_URL}/analyze-gaps",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return {"error": str(e)}

def get_analysis_status(analysis_id: str) -> Dict[str, Any]:
    """Get analysis status"""
    try:
        response = requests.get(f"{API_BASE_URL}/status/{analysis_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def run_sync_analysis(competitors: list, focus_area: str) -> Dict[str, Any]:
    """Run synchronous analysis (for testing)"""
    try:
        payload = {
            "competitors": competitors,
            "focus_area": focus_area
        }
        response = requests.post(
            f"{API_BASE_URL}/analyze-gaps-sync",
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Analysis failed: {str(e)}")
        return {"error": str(e)}

def display_clinical_gaps(gaps: list):
    """Display clinical gaps in a formatted way"""
    if not gaps:
        st.info("No clinical gaps identified in the analysis.")
        return
    
    st.subheader(f"🔬 Clinical Gaps Identified ({len(gaps)})")
    
    for i, gap in enumerate(gaps, 1):
        with st.expander(f"Gap {i}: {gap.get('competitor', 'Unknown')} - {gap.get('gap_type', 'General')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Description:**")
                st.write(gap.get('description', 'No description available'))
                
                if gap.get('evidence'):
                    st.write("**Supporting Evidence:**")
                    st.write(gap.get('evidence', ''))
            
            with col2:
                st.metric("Severity", gap.get('severity', 'Unknown').title())
                
                if gap.get('source_url'):
                    st.write("**Source:**")
                    st.markdown(f"[View Source]({gap.get('source_url')})")

def display_market_opportunities(opportunities: list):
    """Display market opportunities in a formatted way"""
    if not opportunities:
        st.info("No market opportunities identified in the analysis.")
        return
    
    st.subheader(f"💡 Market Opportunities ({len(opportunities)})")
    
    for i, opp in enumerate(opportunities, 1):
        with st.expander(f"Opportunity {i}: {opp.get('opportunity_type', 'Market').replace('_', ' ').title()}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Description:**")
                st.write(opp.get('description', 'No description available'))
                
                if opp.get('evidence'):
                    st.write("**Supporting Evidence:**")
                    st.write(opp.get('evidence', ''))
            
            with col2:
                st.write("**Market Landscape:**")
                st.write(opp.get('competitive_landscape', 'Unknown'))
                
                if opp.get('source_url') and opp.get('source_url') != "Multiple sources":
                    st.write("**Source:**")
                    st.markdown(f"[View Source]({opp.get('source_url')})")

def display_analysis_summary(result: Dict[str, Any]):
    """Display executive summary and metadata"""
    st.subheader("📊 Executive Summary")
    
    summary = result.get('summary', 'No summary available')
    st.write(summary)
    
    # Display metadata in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Competitors Analyzed", 
            len(result.get('competitors_analyzed', []))
        )
    
    with col2:
        st.metric(
            "Clinical Gaps", 
            len(result.get('clinical_gaps', []))
        )
    
    with col3:
        st.metric(
            "Market Opportunities", 
            len(result.get('market_opportunities', []))
        )
    
    with col4:
        st.metric(
            "Sources Analyzed", 
            result.get('total_sources_analyzed', 0)
        )
    
    # Show analysis metadata
    if result.get('analysis_metadata'):
        with st.expander("📈 Analysis Details"):
            metadata = result['analysis_metadata']
            st.json(metadata)

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🦴 Orthopedic Competitive Intelligence")
    st.markdown("*AI-powered competitive analysis for orthopedic device manufacturers*")
    
    # Check API health
    api_healthy, health_info = check_api_health()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Status
        if api_healthy:
            st.success("✅ API Connected")
            if health_info:
                st.write("**Service Status:**")
                services = health_info.get('services', {})
                for service, status in services.items():
                    icon = "✅" if status else "❌"
                    st.write(f"{icon} {service.replace('_', ' ').title()}")
        else:
            st.error("❌ API Disconnected")
            st.write("Make sure FastAPI server is running on localhost:8000")
        
        st.divider()
        
        # Competitor Selection
        st.subheader("🏢 Select Competitors")
        
        # Predefined competitor options
        competitor_options = [
            "Stryker Spine",
            "Zimmer Biomet", 
            "Orthofix",
            "NuVasive",
            "Medtronic Spine",
            "DePuy Synthes",
            "Globus Medical"
        ]
        
        selected_competitors = st.multiselect(
            "Choose competitors to analyze:",
            options=competitor_options,
            default=["Stryker Spine", "Zimmer Biomet"],
            max_selections=5,
            help="Select 1-5 competitors for analysis"
        )
        
        # Custom competitor input
        custom_competitor = st.text_input(
            "Add custom competitor:",
            placeholder="Enter competitor name"
        )
        
        if custom_competitor and st.button("Add Custom"):
            if custom_competitor not in selected_competitors:
                selected_competitors.append(custom_competitor)
                st.success(f"Added {custom_competitor}")
            else:
                st.warning("Competitor already selected")
        
        st.divider()
        
        # Focus Area Selection
        st.subheader("🎯 Focus Area")
        focus_area = st.selectbox(
            "Select focus area:",
            options=["spine_fusion", "joint_replacement", "trauma", "sports_medicine"],
            index=0,
            help="Medical device category to focus analysis on"
        )
        
        st.divider()
        
        # Analysis Mode
        st.subheader("⚡ Analysis Mode")
        sync_mode = st.checkbox(
            "Synchronous Analysis",
            value=True,
            help="Run analysis immediately (may take 2-5 minutes)"
        )
    
    # Main content area
    if not selected_competitors:
        st.warning("Please select at least one competitor to analyze.")
        st.stop()
    
    if not api_healthy:
        st.error("Cannot run analysis - API is not available. Please start the FastAPI server.")
        st.code("python fastapi_server.py")
        st.stop()
    
    # Display selected configuration
    st.subheader("📋 Analysis Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Selected Competitors:**")
        for comp in selected_competitors:
            st.write(f"• {comp}")
    
    with col2:
        st.write(f"**Focus Area:** {focus_area.replace('_', ' ').title()}")
        st.write(f"**Analysis Mode:** {'Synchronous' if sync_mode else 'Asynchronous'}")
    
    # Run Analysis Button
    if st.button("🚀 Start Competitive Analysis", type="primary", use_container_width=True):
        
        if sync_mode:
            # Synchronous analysis
            with st.spinner("Running competitive analysis... This may take 2-5 minutes."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress updates
                for i in range(1, 6):
                    progress_bar.progress(i * 20)
                    status_text.text(f"Step {i}/5: {'Initializing' if i==1 else 'Researching competitors' if i<=3 else 'Analyzing results' if i==4 else 'Generating report'}...")
                    time.sleep(0.5)
                
                # Run actual analysis
                result = run_sync_analysis(selected_competitors, focus_area)
                
                progress_bar.progress(100)
                status_text.text("Analysis complete!")
                
                if "error" not in result:
                    st.success("✅ Analysis completed successfully!")
                    
                    # Store result in session state
                    st.session_state['analysis_result'] = result
                    st.session_state['analysis_timestamp'] = time.time()
                    
                else:
                    st.error(f"Analysis failed: {result['error']}")
        
        else:
            # Asynchronous analysis (placeholder for future implementation)
            st.info("Asynchronous analysis will be implemented in a future version.")
            st.write("For now, please use synchronous mode.")
    
    # Display Results
    if 'analysis_result' in st.session_state:
        st.divider()
        st.header("📊 Analysis Results")
        
        result = st.session_state['analysis_result']
        
        # Display executive summary
        display_analysis_summary(result)
        
        st.divider()
        
        # Display detailed results in tabs
        tab1, tab2, tab3 = st.tabs(["🔬 Clinical Gaps", "💡 Market Opportunities", "📄 Raw Data"])
        
        with tab1:
            display_clinical_gaps(result.get('clinical_gaps', []))
        
        with tab2:
            display_market_opportunities(result.get('market_opportunities', []))
        
        with tab3:
            st.subheader("Raw Analysis Data")
            st.json(result)
        
        # Download results
        st.divider()
        st.subheader("💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON download
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📄 Download JSON",
                data=json_str,
                file_name=f"competitive_analysis_{int(time.time())}.json",
                mime="application/json"
            )
        
        with col2:
            # Summary report download
            summary_report = f"""
            COMPETITIVE INTELLIGENCE REPORT
            Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
            
            COMPETITORS ANALYZED:
            {chr(10).join(['• ' + comp for comp in result.get('competitors_analyzed', [])])}
            
            EXECUTIVE SUMMARY:
            {result.get('summary', 'No summary available')}
            
            CLINICAL GAPS ({len(result.get('clinical_gaps', []))}):
            {chr(10).join([f"• {gap.get('competitor', 'Unknown')}: {gap.get('description', 'No description')}" for gap in result.get('clinical_gaps', [])])}
            
            MARKET OPPORTUNITIES ({len(result.get('market_opportunities', []))}):
            {chr(10).join([f"• {opp.get('opportunity_type', 'Unknown')}: {opp.get('description', 'No description')}" for opp in result.get('market_opportunities', [])])}
            """
            
            st.download_button(
                label="📊 Download Report",
                data=summary_report,
                file_name=f"competitive_report_{int(time.time())}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()