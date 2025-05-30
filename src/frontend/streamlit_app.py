"""
Modified frontend for Streamlit Cloud deployment with authentication
"""

import streamlit as st
import requests
import json
import time
from .auth.streamlit_auth import StreamlitAuth

# Configure page
st.set_page_config(
    page_title="Medical Device Competitive Intelligence",
    page_icon="🏥",
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
        from ..backend.pipelines.main_langgraph import intelligence_graph
        
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

def display_market_share_insights(insights):
    """Display market share insights - NEW"""
    if not insights:
        st.info("No market share insights available in this analysis.")
        return
    
    st.subheader(f"📈 Market Share Analysis ({len(insights)})")
    
    for i, insight in enumerate(insights, 1):
        competitor = insight.get('competitor', 'Unknown')
        market_position = insight.get('market_position', 'Unknown')
        
        # Color code market position
        position_color = {
            'Leader': '🟢',
            'Challenger': '🟡', 
            'Follower': '🟠',
            'Niche': '🔵'
        }.get(market_position, '⚪')
        
        with st.expander(f"{position_color} {competitor} - {market_position}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if insight.get('estimated_market_share'):
                    st.metric("Market Share", insight.get('estimated_market_share'))
                
                if insight.get('revenue_estimate'):
                    st.write(f"**Revenue Estimate:** {insight.get('revenue_estimate')}")
                
                if insight.get('growth_trend'):
                    trend_emoji = {'Increasing': '📈', 'Stable': '➡️', 'Declining': '📉'}.get(insight.get('growth_trend'), '📊')
                    st.write(f"**Growth Trend:** {trend_emoji} {insight.get('growth_trend')}")
                
                if insight.get('key_markets'):
                    st.write(f"**Key Markets:** {', '.join(insight.get('key_markets', []))}")
            
            with col2:
                st.write("**Evidence:**")
                st.write(insight.get('evidence', 'No evidence available'))
                
                if insight.get('source_url'):
                    st.markdown(f"[📎 View Source]({insight.get('source_url')})")

def display_brand_positioning(positioning):
    """Display brand positioning analysis - NEW"""
    if not positioning:
        st.info("No brand positioning analysis available.")
        return
    
    st.subheader(f"🎯 Brand Positioning Analysis ({len(positioning)})")
    
    for i, brand in enumerate(positioning, 1):
        competitor = brand.get('competitor', 'Unknown')
        
        with st.expander(f"🏷️ {competitor} Brand Analysis"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Brand Message:**")
                st.write(brand.get('brand_message', 'Not identified'))
                
                if brand.get('target_segments'):
                    st.write("**Target Segments:**")
                    for segment in brand.get('target_segments', []):
                        st.write(f"• {segment}")
                
                if brand.get('differentiation_factors'):
                    st.write("**Differentiation Factors:**")
                    for factor in brand.get('differentiation_factors', []):
                        st.write(f"• {factor}")
            
            with col2:
                if brand.get('brand_strengths'):
                    st.write("**Brand Strengths:**")
                    for strength in brand.get('brand_strengths', []):
                        st.write(f"✅ {strength}")
                
                if brand.get('brand_weaknesses'):
                    st.write("**Brand Weaknesses:**")
                    for weakness in brand.get('brand_weaknesses', []):
                        st.write(f"❌ {weakness}")
                
                if brand.get('source_url'):
                    st.markdown(f"[📎 View Source]({brand.get('source_url')})")

def display_product_feature_gaps(gaps):
    """Display product feature gap analysis - NEW"""
    if not gaps:
        st.info("No product feature gap analysis available.")
        return
    
    st.subheader(f"⚙️ Product Feature Analysis ({len(gaps)})")
    
    for i, gap in enumerate(gaps, 1):
        competitor = gap.get('competitor', 'Unknown')
        category = gap.get('product_category', 'Unknown')
        
        with st.expander(f"🔧 {competitor} - {category} Features"):
            col1, col2 = st.columns(2)
            
            with col1:
                if gap.get('competitor_advantages'):
                    st.write("**Competitive Advantages:**")
                    for advantage in gap.get('competitor_advantages', []):
                        st.write(f"🟢 {advantage}")
                
                if gap.get('feature_comparison'):
                    st.write("**Feature Comparison:**")
                    for feature, rating in gap.get('feature_comparison', {}).items():
                        st.write(f"• **{feature}:** {rating}")
            
            with col2:
                if gap.get('competitor_gaps'):
                    st.write("**Identified Gaps:**")
                    for gap_item in gap.get('competitor_gaps', []):
                        st.write(f"🔴 {gap_item}")
                
                if gap.get('innovation_areas'):
                    st.write("**Innovation Opportunities:**")
                    for area in gap.get('innovation_areas', []):
                        st.write(f"💡 {area}")
                
                if gap.get('source_url'):
                    st.markdown(f"[📎 View Source]({gap.get('source_url')})")

def main():
    """Main Streamlit application with authentication"""
    
    # Check authentication first
    if not auth.check_password():
        st.stop()
    
    # Show authenticated content
    st.title("🏥 Medical Device Competitive Intelligence")
    st.markdown("*AI-powered competitive analysis across 4 medical device categories*")
    
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
            "🫀 Cardiovascular Leaders": ["Medtronic", "Abbott", "Boston Scientific"],
            "🫀 Cardiovascular Innovation": ["Edwards Lifesciences", "Biotronik"],
            "🦴 Spine Fusion Leaders": ["Stryker Spine", "Zimmer Biomet"],
            "🦴 Spine Emerging Players": ["Orthofix", "NuVasive"],
            "🦵 Joint Replacement Giants": ["Stryker Ortho", "Smith+Nephew", "DePuy Synthes"],
            "🦵 Joint Innovation": ["Wright Medical", "Conformis"],
            "💉 Diabetes Care Leaders": ["Dexcom", "Abbott"],
            "💉 Diabetes Innovation": ["Medtronic Diabetes", "Tandem", "Insulet"]
        }
        
        selected_demo = st.selectbox("Choose demo scenario:", ["Custom"] + list(demo_scenarios.keys()))
        
        if selected_demo != "Custom":
            selected_competitors = demo_scenarios[selected_demo]
            st.success(f"Loaded: {selected_demo}")
        else:
            # Manual selection - Group competitors by category for better UX
            cardiovascular_competitors = ["Medtronic", "Abbott", "Boston Scientific", "Edwards Lifesciences", "Biotronik"]
            spine_competitors = ["Stryker Spine", "Zimmer Biomet", "Orthofix", "NuVasive", "Medtronic Spine"]
            joint_competitors = ["Stryker Ortho", "Smith+Nephew", "DePuy Synthes", "Wright Medical", "Conformis"]
            diabetes_competitors = ["Dexcom", "Abbott", "Medtronic Diabetes", "Tandem", "Insulet"]
            
            # Combine all for multiselect
            competitor_options = cardiovascular_competitors + spine_competitors + joint_competitors + diabetes_competitors
            
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
        
        # Show detected category if competitors selected
        if selected_competitors:
            from data_models import CategoryRouter
            router = CategoryRouter()
            detected_category = router.detect_category(selected_competitors, "")
            
            category_display = {
                "cardiovascular": "🫀 Cardiovascular",
                "spine_fusion": "🦴 Spine Fusion", 
                "joint_replacement": "🦵 Joint Replacement",
                "diabetes_care": "💉 Diabetes Care"
            }
            
            st.info(f"🎯 **Detected Category:** {category_display.get(detected_category, detected_category)}")
            st.session_state['detected_category'] = detected_category
    
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
        if 'detected_category' in st.session_state:
            category = st.session_state['detected_category']
            category_display = {
                "cardiovascular": "🫀 Cardiovascular",
                "spine_fusion": "🦴 Spine Fusion", 
                "joint_replacement": "🦵 Joint Replacement",
                "diabetes_care": "💉 Diabetes Care"
            }
            st.write(f"**Device Category:** {category_display.get(category, category)}")
        st.write(f"**Analysis Type:** Multi-Category AI Analysis")
    
    # Value proposition - Updated for market intelligence focus
    with st.expander("💡 What This Analysis Provides"):
        st.write("• **Market Intelligence**: Market share analysis, brand positioning, and competitive landscape insights")
        st.write("• **Multi-Category Support**: Analyze competitors across 4 medical device categories")
        st.write("• **Strategic Insights**: Market opportunities, positioning gaps, and competitive advantages")
        st.write("• **Clinical Analysis**: Regulatory issues, device limitations, and clinical gaps")
        st.write("• **Evidence-Based**: All insights backed by web research and citations")
        st.write("• **Auto-Detection**: Category automatically detected from selected competitors")
    
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
        
        # Metrics - Updated to include market intelligence
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Competitors Analyzed", len(result.get('competitors_analyzed', [])))
        with col2:
            st.metric("Clinical Gaps", len(result.get('clinical_gaps', [])))
        with col3:
            st.metric("Market Opportunities", len(result.get('market_opportunities', [])))
        with col4:
            st.metric("Market Insights", len(result.get('market_share_insights', [])))
        
        # Detailed results - Updated with market intelligence tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Market Share", 
            "🎯 Brand Positioning", 
            "💡 Market Opportunities", 
            "🔬 Clinical Gaps", 
            "📄 Raw Data"
        ])
        
        with tab1:
            display_market_share_insights(result.get('market_share_insights', []))
        
        with tab2:
            display_brand_positioning(result.get('brand_positioning', []))
        
        with tab3:
            display_market_opportunities(result.get('market_opportunities', []))
        
        with tab4:
            display_clinical_gaps(result.get('clinical_gaps', []))
        
        with tab5:
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