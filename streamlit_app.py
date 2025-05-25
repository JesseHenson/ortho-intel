"""
Modified frontend for Streamlit Cloud deployment with authentication
"""

import streamlit as st
import requests
import json
import time
from streamlit_auth import StreamlitAuth

# Configure page
st.set_page_config(
    page_title="Orthopedic Competitive Intelligence",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication
auth = StreamlitAuth(password="ortho2025")

def run_local_analysis(competitors, focus_area):
    """
    STREAMLIT CLOUD LIMITATION: Can't run FastAPI server
    So we'll run the LangGraph analysis directly in Streamlit
    """
    try:
        # Import our LangGraph directly
        from main_langgraph import intelligence_graph
        
        with st.spinner("Running competitive analysis... This may take 2-5 minutes."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Progress simulation
            progress_bar.progress(20)
            status_text.text("🔍 Initializing research...")
            
            # Run analysis
            result = intelligence_graph.run_analysis(competitors, focus_area)
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            
            return result
            
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return {"error": str(e)}

def display_clinical_gaps(gaps):
    """Display clinical gaps"""
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
                severity = gap.get('severity', 'Unknown').title()
                if severity == 'High':
                    st.error(f"🔴 Severity: {severity}")
                elif severity == 'Medium':
                    st.warning(f"🟡 Severity: {severity}")
                else:
                    st.success(f"🟢 Severity: {severity}")
                
                if gap.get('source_url'):
                    st.markdown(f"[📎 View Source]({gap.get('source_url')})")

def display_market_opportunities(opportunities):
    """Display market opportunities"""
    if not opportunities:
        st.info("No market opportunities identified in the analysis.")
        return
    
    st.subheader(f"💡 Market Opportunities ({len(opportunities)})")
    
    for i, opp in enumerate(opportunities, 1):
        with st.expander(f"Opportunity {i}: {opp.get('opportunity_type', 'Market').replace('_', ' ').title()}"):
            st.write("**Description:**")
            st.write(opp.get('description', 'No description available'))
            
            if opp.get('evidence'):
                st.write("**Supporting Evidence:**")
                st.write(opp.get('evidence', ''))
            
            st.write(f"**Market Landscape:** {opp.get('competitive_landscape', 'Unknown')}")

def main():
    """Main Streamlit application with authentication"""
    
    # Check authentication first
    if not auth.check_password():
        st.stop()
    
    # Show authenticated content
    st.title("🦴 Orthopedic Competitive Intelligence")
    st.markdown("*AI-powered competitive analysis for orthopedic device manufacturers*")
    
    # Demo info banner
    st.info("🚀 **Demo Version** - This analysis runs entirely in your browser using AI. Results generated in 2-5 minutes.")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Environment check
        import os
        tavily_key = os.getenv("TAVILY_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY") 
        
        if tavily_key and openai_key:
            st.success("✅ API Keys Configured")
        else:
            st.error("❌ API Keys Missing")
            st.caption("Set in Streamlit Cloud secrets")
        
        st.divider()
        
        # Demo scenarios
        st.subheader("🎯 Quick Demo Scenarios")
        
        demo_scenarios = {
            "Spine Leaders": ["Stryker Spine", "Zimmer Biomet"],
            "Emerging Players": ["Orthofix", "NuVasive"], 
            "Full Landscape": ["Stryker Spine", "Zimmer Biomet", "Orthofix"]
        }
        
        selected_demo = st.selectbox("Choose demo scenario:", ["Custom"] + list(demo_scenarios.keys()))
        
        if selected_demo != "Custom":
            selected_competitors = demo_scenarios[selected_demo]
            st.success(f"Loaded: {selected_demo}")
        else:
            # Manual selection
            competitor_options = [
                "Stryker Spine", "Zimmer Biomet", "Orthofix",
                "NuVasive", "Medtronic Spine", "DePuy Synthes", "Globus Medical"
            ]
            
            selected_competitors = st.multiselect(
                "Select competitors to analyze:",
                options=competitor_options,
                default=["Stryker Spine", "Zimmer Biomet"],
                max_selections=3,  # Limit for demo
                help="Select up to 3 competitors for analysis"
            )
        
        focus_area = st.selectbox(
            "Focus area:",
            options=["spine_fusion", "joint_replacement", "trauma"],
            index=0
        )
    
    # Main content
    if not selected_competitors:
        st.warning("Please select at least one competitor to analyze.")
        st.stop()
    
    # Show configuration
    st.subheader("📋 Analysis Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Selected Competitors:**")
        for comp in selected_competitors:
            st.write(f"• {comp}")
    
    with col2:
        st.write(f"**Focus Area:** {focus_area.replace('_', ' ').title()}")
        st.write(f"**Analysis Type:** Direct AI Analysis")
    
    # Value proposition
    with st.expander("💡 What This Analysis Provides"):
        st.write("• **Clinical Gaps**: Regulatory issues, device limitations, surgeon feedback")
        st.write("• **Market Opportunities**: Unmet needs, technology gaps, positioning opportunities")
        st.write("• **Evidence-Based**: All insights backed by web research and citations")
        st.write("• **Actionable**: Ready for product strategy and competitive positioning")
    
    # Run analysis
    if st.button("🚀 Start Competitive Analysis", type="primary", use_container_width=True):
        
        # Environment check
        if not (os.getenv("TAVILY_API_KEY") and os.getenv("OPENAI_API_KEY")):
            st.error("❌ API keys not configured. Please set TAVILY_API_KEY and OPENAI_API_KEY in Streamlit Cloud secrets.")
            st.stop()
        
        # Run analysis
        result = run_local_analysis(selected_competitors, focus_area)
        
        if "error" not in result:
            st.success("✅ Analysis completed successfully!")
            
            # Store in session state
            st.session_state['analysis_result'] = result
            st.session_state['analysis_timestamp'] = time.time()
        else:
            st.error(f"Analysis failed: {result['error']}")
    
    # Display results
    if 'analysis_result' in st.session_state:
        st.divider()
        st.header("📊 Analysis Results")
        
        result = st.session_state['analysis_result']
        
        # Executive summary
        st.subheader("📋 Executive Summary")
        summary = result.get('summary', 'Analysis completed with findings below.')
        st.write(summary)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Competitors Analyzed", len(result.get('competitors_analyzed', [])))
        with col2:
            st.metric("Clinical Gaps", len(result.get('clinical_gaps', [])))
        with col3:
            st.metric("Market Opportunities", len(result.get('market_opportunities', [])))
        
        # Detailed results
        tab1, tab2, tab3 = st.tabs(["🔬 Clinical Gaps", "💡 Opportunities", "📄 Raw Data"])
        
        with tab1:
            display_clinical_gaps(result.get('clinical_gaps', []))
        
        with tab2:
            display_market_opportunities(result.get('market_opportunities', []))
        
        with tab3:
            st.subheader("Raw Analysis Data")
            st.json(result)
        
        # Export options
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            json_str = json.dumps(result, indent=2)
            st.download_button(
                "📄 Download JSON",
                data=json_str,
                file_name=f"competitive_analysis_{int(time.time())}.json",
                mime="application/json"
            )
        
        with col2:
            # Summary report
            summary_report = f"""
COMPETITIVE INTELLIGENCE REPORT
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

COMPETITORS: {', '.join(result.get('competitors_analyzed', []))}
FOCUS AREA: {focus_area.replace('_', ' ').title()}

EXECUTIVE SUMMARY:
{result.get('summary', 'No summary available')}

CLINICAL GAPS ({len(result.get('clinical_gaps', []))}):
{chr(10).join([f"• {gap.get('competitor', 'Unknown')}: {gap.get('description', 'No description')[:100]}..." for gap in result.get('clinical_gaps', [])])}

OPPORTUNITIES ({len(result.get('market_opportunities', []))}):
{chr(10).join([f"• {opp.get('opportunity_type', 'Unknown')}: {opp.get('description', 'No description')[:100]}..." for opp in result.get('market_opportunities', [])])}
            """
            
            st.download_button(
                "📊 Download Report",
                data=summary_report,
                file_name=f"competitive_report_{int(time.time())}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()