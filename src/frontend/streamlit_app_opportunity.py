# streamlit_app_opportunity.py
"""
Opportunity-First Competitive Intelligence Frontend
Executive-ready interface prioritizing actionable opportunities
Enhanced with Progressive Disclosure UI Components
"""

import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Orthopedic Intelligence - Opportunity Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import json
from typing import Dict, List, Any
import sys
import os
import hashlib

# Add project root to path for absolute imports when run directly
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Try relative imports first (when run through launcher)
    from ..backend.pipelines.main_langgraph_opportunity import opportunity_graph
    from ..backend.core.opportunity_data_models import (
        StrategicOpportunity, 
        CategoryOpportunity, 
        ExecutiveSummary,
        OpportunityAnalysisResponse
    )
    from .components.progressive_disclosure import (
        render_opportunities_with_progressive_disclosure,
        render_opportunities_simple,
        create_opportunity_summary_grid,
        ProgressiveDisclosureManager
    )
except ImportError:
    # Fall back to absolute imports (when run directly)
    from src.backend.pipelines.main_langgraph_opportunity import opportunity_graph
    from src.backend.core.opportunity_data_models import (
        StrategicOpportunity, 
        CategoryOpportunity, 
        ExecutiveSummary,
        OpportunityAnalysisResponse
    )
    from src.frontend.components.progressive_disclosure import (
        render_opportunities_with_progressive_disclosure,
        render_opportunities_simple,
        create_opportunity_summary_grid,
        ProgressiveDisclosureManager
    )

# Custom CSS for opportunity-first design
st.markdown("""
<style>
    /* Main opportunity cards */
    .opportunity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .opportunity-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .opportunity-impact {
        font-size: 1.1rem;
        color: #ffd700;
        font-weight: 600;
    }
    
    /* Quick wins styling */
    .quick-win {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Strategic investments styling */
    .strategic-investment {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Executive summary styling */
    .executive-summary {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    /* Metrics styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #667eea;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Category tabs */
    .category-tab {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Competitive landscape */
    .competitor-profile {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Dark mode adaptations */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
        
        .category-tab {
            background: rgba(255, 255, 255, 0.05);
            color: white;
        }
        
        .competitor-profile {
            background: rgba(255, 255, 255, 0.05);
            color: white;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application interface"""
    
    # Initialize session state for analysis results
    if 'analysis_completed' not in st.session_state:
        st.session_state.analysis_completed = False
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'analysis_config' not in st.session_state:
        st.session_state.analysis_config = None
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #667eea; font-size: 3rem; margin-bottom: 0.5rem;">🎯 Orthopedic Intelligence</h1>
        <p style="font-size: 1.3rem; color: #666; margin-bottom: 2rem;">
            Competitive Intelligence Platform for Medical Device Manufacturing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## 🔧 **Analysis Configuration**")
        
        # Client name input
        client_name = st.text_input(
            "Client Name",
            placeholder="Enter client/company name",
            help="Personalize the analysis report with your client's name"
        )
        
        # Competitor input methods
        st.markdown("### 🏢 **Competitor Selection**")
        
        input_method = st.radio(
            "Choose input method:",
            options=["Quick Select", "Custom Input"],
            help="Quick Select for common competitors, Custom Input for specific companies"
        )
        
        competitors = []
        
        if input_method == "Quick Select":
            # Predefined competitor options
            competitor_options = [
                "Stryker Spine", "Medtronic Spine", "DePuy Synthes", 
                "Zimmer Biomet", "Globus Medical", "NuVasive",
                "Orthofix", "SeaSpine", "Alphatec Spine"
            ]
            
            selected_competitors = st.multiselect(
                "Select competitors:",
                options=competitor_options,
                default=["Stryker Spine", "Medtronic Spine", "DePuy Synthes"],
                help="Choose from common orthopedic spine competitors"
            )
            competitors = selected_competitors
            
        else:  # Custom Input
            # Manual competitor entry
            st.markdown("**Enter competitors (one per line):**")
            competitor_text = st.text_area(
                "Competitors",
                placeholder="Stryker Spine\nMedtronic Spine\nDePuy Synthes\n...",
                height=100,
                help="Enter each competitor on a new line"
            )
            
            if competitor_text.strip():
                competitors = [comp.strip() for comp in competitor_text.split('\n') if comp.strip()]
        
        # Display selected competitors
        if competitors:
            st.markdown("**Selected Competitors:**")
            for i, comp in enumerate(competitors, 1):
                st.markdown(f"{i}. {comp}")
        
        st.markdown("---")
        
        # Focus area selection
        focus_area = st.selectbox(
            "Focus Area",
            options=[
                "spine_fusion", "joint_replacement", "trauma_fixation", 
                "sports_medicine", "neurosurgery", "orthobiologics"
            ],
            index=0,
            help="Primary market segment for analysis"
        )
        
        # Analysis type
        analysis_type = st.radio(
            "Analysis Priority",
            options=["Opportunities First", "Comprehensive Analysis"],
            index=0,
            help="Choose analysis focus"
        )
        
        # Show current analysis status
        if st.session_state.analysis_completed:
            st.success("✅ Analysis completed!")
            st.markdown("**Current Analysis:**")
            if st.session_state.analysis_config:
                config = st.session_state.analysis_config
                st.markdown(f"- **Competitors:** {', '.join(config['competitors'])}")
                st.markdown(f"- **Focus Area:** {config['focus_area']}")
                st.markdown(f"- **Analysis Type:** {config['analysis_type']}")
            
            # Reset button
            if st.button("🔄 Run New Analysis", type="secondary", use_container_width=True):
                st.session_state.analysis_completed = False
                st.session_state.analysis_result = None
                st.session_state.analysis_config = None
                st.rerun()
        
        # Run analysis button (only show if no analysis completed)
        if not st.session_state.analysis_completed:
            run_analysis = st.button(
                "🚀 Run Opportunity Analysis",
                type="primary",
                use_container_width=True,
                disabled=not competitors
            )
            
            # Trigger analysis if button clicked
            if run_analysis and competitors:
                run_opportunity_analysis(competitors, focus_area, analysis_type, client_name)
    
    # Main content area - Show analysis results if available, else show demo
    if st.session_state.analysis_completed and st.session_state.analysis_result:
        # Display real analysis results
        config = st.session_state.analysis_config
        display_opportunity_results_with_progressive_disclosure(
            st.session_state.analysis_result, 
            config['competitors'], 
            config['focus_area'], 
            config['client_name']
        )
    else:
        # Show demo dashboard
        show_demo_dashboard()

def run_opportunity_analysis(competitors: List[str], focus_area: str, analysis_type: str, client_name: str = ""):
    """Run the opportunity analysis pipeline and store results in session state"""
    
    # Store analysis configuration
    st.session_state.analysis_config = {
        "competitors": competitors,
        "focus_area": focus_area,
        "analysis_type": analysis_type,
        "client_name": client_name
    }
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize the analysis
        status_text.text("🔍 Initializing competitive intelligence analysis...")
        progress_bar.progress(10)
        
        # Run the opportunity graph
        status_text.text("🔬 Analyzing competitive landscape...")
        progress_bar.progress(30)
        
        # Simulate analysis steps
        import time
        time.sleep(1)
        
        status_text.text("📊 Generating strategic opportunities...")
        progress_bar.progress(60)
        time.sleep(1)
        
        status_text.text("📋 Compiling executive summary...")
        progress_bar.progress(80)
        time.sleep(1)
        
        # Execute the graph
        result = opportunity_graph.run_analysis(
            competitors=competitors,
            focus_area=focus_area
        )
        
        status_text.text("✅ Analysis complete!")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # Store results in session state
        st.session_state.analysis_result = result
        st.session_state.analysis_completed = True
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Force page refresh to show results
        st.rerun()
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")
        
        # Reset session state on error
        st.session_state.analysis_completed = False
        st.session_state.analysis_result = None
        st.session_state.analysis_config = None
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

def display_opportunity_results_with_progressive_disclosure(result: Dict[str, Any], competitors: List[str], focus_area: str, client_name: str = ""):
    """Display the opportunity-first analysis results with progressive disclosure components"""
    
    # Generate unique analysis ID for this session
    analysis_timestamp = datetime.now().isoformat()
    analysis_data = f"{competitors}_{focus_area}_{analysis_timestamp}"
    analysis_id = hashlib.md5(analysis_data.encode()).hexdigest()[:8]
    
    # Extract key data
    final_report = result.get("final_report", {})
    top_opportunities = result.get("top_opportunities", [])
    executive_summary = result.get("executive_summary", {})
    
    # Analysis metadata
    analysis_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    
    # Client header if provided
    if client_name:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; text-align: center;">
            <h2 style="margin-bottom: 0.5rem;">📊 Competitive Intelligence Report</h2>
            <h3 style="color: #ffd700; margin-bottom: 0;">for {client_name}</h3>
            <p style="opacity: 0.8; margin-top: 0.5rem;">Generated on {analysis_date}</p>
            <p style="opacity: 0.6; font-size: 0.9rem;">Analysis ID: {analysis_id}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; text-align: center;">
            <h2 style="margin-bottom: 0.5rem;">📊 Live Competitive Intelligence Analysis</h2>
            <p style="opacity: 0.8; margin-top: 0.5rem;">Generated on {analysis_date}</p>
            <p style="opacity: 0.6; font-size: 0.9rem;">Analysis ID: {analysis_id}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced opportunities with credibility indicators
    enhanced_opportunities = enhance_opportunities_with_credibility(top_opportunities)
    
    # Hero Section - Progressive Disclosure Opportunities with analysis_id
    if enhanced_opportunities:
        render_opportunities_with_progressive_disclosure(
            enhanced_opportunities, 
            title="🎯 **TOP STRATEGIC OPPORTUNITIES**",
            analysis_id=analysis_id  # Pass analysis ID to distinguish from demo mode
        )
    else:
        st.warning("No strategic opportunities were identified in this analysis.")
    
    # Executive Summary (unchanged - still valuable as overview)
    if executive_summary:
        st.markdown("## 📊 **EXECUTIVE SUMMARY**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(top_opportunities)}</div>
                <div class="metric-label">Strategic Opportunities</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            revenue_potential = executive_summary.get("revenue_potential", "$10M-50M")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{revenue_potential.split('-')[0]}</div>
                <div class="metric-label">Revenue Potential</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            market_share = executive_summary.get("market_share_opportunity", "5-10%")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{market_share.split('-')[0]}</div>
                <div class="metric-label">Market Share Gain</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Key insight
        key_insight = executive_summary.get("key_insight", "")
        if key_insight:
            st.markdown(f"""
            <div class="executive-summary">
                <h3 style="margin-bottom: 1rem;">🔍 Key Strategic Insight</h3>
                <p style="font-size: 1.2rem; line-height: 1.6;">{key_insight}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Opportunity Categories (unchanged - still valuable for categorization)
    st.markdown("## 📋 **OPPORTUNITY CATEGORIES**")
    
    # Create tabs for different opportunity types
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Brand Strategy", "🔧 Product Innovation", "💰 Pricing Strategy", "🌍 Market Expansion"])
    
    with tab1:
        # Try both final_report and direct access
        brand_opps = final_report.get("brand_opportunities", []) if final_report else result.get("brand_opportunities", [])
        display_category_opportunities(brand_opps, "Brand Strategy")
    
    with tab2:
        product_opps = final_report.get("product_opportunities", []) if final_report else result.get("product_opportunities", [])
        display_category_opportunities(product_opps, "Product Innovation")
    
    with tab3:
        pricing_opps = final_report.get("pricing_opportunities", []) if final_report else result.get("pricing_opportunities", [])
        display_category_opportunities(pricing_opps, "Pricing Strategy")
    
    with tab4:
        market_opps = final_report.get("market_opportunities", []) if final_report else result.get("market_expansion_opportunities", [])
        display_category_opportunities(market_opps, "Market Expansion")
    
    # Competitive Landscape (unchanged)
    st.markdown("## 🏆 **COMPETITIVE LANDSCAPE**")
    
    competitive_profiles = result.get("competitive_profiles", {})
    if competitive_profiles:
        cols = st.columns(min(len(competitive_profiles), 3))
        
        for i, (competitor, profile) in enumerate(competitive_profiles.items()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="competitor-profile">
                    <h4 style="color: #667eea; margin-bottom: 1rem;">{competitor}</h4>
                    <p><strong>Market Share:</strong> {profile.get('market_share', 'Analysis-based')}</p>
                    <p><strong>Key Strengths:</strong> {', '.join(profile.get('strengths', []))}</p>
                    <p><strong>Opportunities Against:</strong> {', '.join(profile.get('opportunities_against', []))}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Opportunity Matrix Visualization (unchanged)
    if result.get("opportunity_matrix"):
        st.markdown("## 📈 **OPPORTUNITY MATRIX**")
        create_opportunity_matrix_chart(result["opportunity_matrix"])
    
    # Implementation Roadmap (unchanged)
    if executive_summary.get("immediate_actions"):
        st.markdown("## 🚀 **IMMEDIATE ACTIONS**")
        
        actions = executive_summary.get("immediate_actions", [])
        for i, action in enumerate(actions):
            st.markdown(f"""
            <div class="quick-win">
                <strong>Action {i+1}:</strong> {action}
            </div>
            """, unsafe_allow_html=True)
    
    # Analysis metadata
    st.markdown("---")
    st.markdown("### 📋 Analysis Details")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Client:** {client_name if client_name else 'Not specified'}")
        st.markdown(f"**Focus Area:** {focus_area.replace('_', ' ').title()}")
    
    with col2:
        st.markdown(f"**Competitors Analyzed:** {len(competitors)}")
        st.markdown(f"**Analysis Date:** {analysis_date}")
    
    with col3:
        st.markdown(f"**Opportunities Found:** {len(top_opportunities)}")
        confidence = result.get("confidence_score", 7.5)
        st.markdown(f"**Confidence Score:** {confidence}/10")

def enhance_opportunities_with_credibility(opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enhance opportunities with credibility indicators and source information for progressive disclosure.
    
    Args:
        opportunities: List of opportunity dictionaries
        
    Returns:
        List of enhanced opportunity dictionaries with credibility metadata
    """
    enhanced = []
    
    for opp in opportunities:
        enhanced_opp = opp.copy()
        
        # Add credibility indicator based on source quality (simulated for now)
        source_urls = opp.get("source_urls", [])
        source_count = len(source_urls)
        
        # Determine credibility based on source count and quality
        if source_count >= 3:
            enhanced_opp["credibility_indicator"] = "🟢"
            enhanced_opp["source_count_display"] = f"{source_count} sources"
        elif source_count >= 1:
            enhanced_opp["credibility_indicator"] = "🟡"
            enhanced_opp["source_count_display"] = f"{source_count} source{'s' if source_count > 1 else ''}"
        else:
            enhanced_opp["credibility_indicator"] = "🔴"
            enhanced_opp["source_count_display"] = "Limited sources"
        
        # Add progressive disclosure flags
        enhanced_opp["has_detailed_analysis"] = bool(opp.get("supporting_evidence") or opp.get("next_steps"))
        enhanced_opp["has_source_analysis"] = bool(source_urls)
        
        # Add confidence level if not present
        if "confidence_level" not in enhanced_opp:
            enhanced_opp["confidence_level"] = opp.get("opportunity_score", 8.0)
        
        # Add opportunity_score if not present (required for progressive disclosure components)
        if "opportunity_score" not in enhanced_opp:
            enhanced_opp["opportunity_score"] = enhanced_opp["confidence_level"]
        
        # Add detailed analysis if not present
        if "detailed_analysis" not in enhanced_opp:
            enhanced_opp["detailed_analysis"] = f"""
            ## Methodology
            This opportunity was identified through competitive gap analysis using AI-powered market intelligence.
            
            ## Analysis Details
            {opp.get('supporting_evidence', 'Comprehensive market research and competitive positioning analysis.')}
            
            ## Implementation Considerations
            - **Difficulty Level:** {opp.get('implementation_difficulty', 'Medium')}
            - **Competitive Risk:** {opp.get('competitive_risk', 'Medium')}
            - **Investment Required:** {opp.get('investment_level', 'Medium')}
            
            ## Success Factors
            Key factors for successful implementation include market timing, competitive response, and execution quality.
            """
        
        enhanced.append(enhanced_opp)
    
    return enhanced

# Keep existing helper functions unchanged
def display_category_opportunities(opportunities: List[Dict], category: str):
    """Display opportunities for a specific category"""
    
    if not opportunities:
        st.info(f"No specific {category.lower()} opportunities identified in this analysis.")
        return
    
    for opp in opportunities:
        st.markdown(f"""
        <div class="category-tab">
            <h4 style="color: #667eea; margin-bottom: 0.5rem;">{opp.get('opportunity', 'Opportunity')}</h4>
            <p><strong>Current Gap:</strong> {opp.get('current_gap', '')}</p>
            <p><strong>Recommendation:</strong> {opp.get('recommendation', '')}</p>
            <p><strong>Implementation:</strong> {opp.get('implementation', '')}</p>
            <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                <span><strong>Timeline:</strong> {opp.get('timeline', '')}</span>
                <span><strong>Investment:</strong> {opp.get('investment', '')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_opportunity_matrix_chart(matrix_data: Dict):
    """Create opportunity matrix visualization"""
    
    # Extract data for plotting
    opportunities = matrix_data.get("opportunities", [])
    
    if not opportunities:
        st.info("Opportunity matrix data not available.")
        return
    
    # Create scatter plot
    fig = go.Figure()
    
    # Add opportunities as scatter points
    for opp in opportunities:
        fig.add_trace(go.Scatter(
            x=[opp.get("implementation_difficulty", 5)],
            y=[opp.get("opportunity_score", 5)],
            mode='markers+text',
            text=[opp.get("title", "")[:20] + "..."],
            textposition="top center",
            marker=dict(
                size=15,
                color=opp.get("opportunity_score", 5),
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Opportunity Score")
            ),
            name=opp.get("title", "Opportunity")
        ))
    
    fig.update_layout(
        title="Opportunity Matrix: Impact vs Implementation Difficulty",
        xaxis_title="Implementation Difficulty (1=Easy, 10=Hard)",
        yaxis_title="Opportunity Score (1=Low, 10=High)",
        height=500,
        showlegend=False
    )
    
    # Add quadrant lines
    fig.add_hline(y=5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=5, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=2.5, y=7.5, text="Quick Wins", showarrow=False, font=dict(size=14, color="green"))
    fig.add_annotation(x=7.5, y=7.5, text="Strategic Investments", showarrow=False, font=dict(size=14, color="orange"))
    fig.add_annotation(x=2.5, y=2.5, text="Low Priority", showarrow=False, font=dict(size=14, color="gray"))
    fig.add_annotation(x=7.5, y=2.5, text="Consider Carefully", showarrow=False, font=dict(size=14, color="red"))
    
    st.plotly_chart(fig, use_container_width=True)

def show_demo_dashboard():
    """Show demo dashboard with progressive disclosure components"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; text-align: center;">
        <h2 style="margin-bottom: 0.5rem;">🎯 DEMO: Strategic Opportunities Dashboard</h2>
        <p style="opacity: 0.9; margin-top: 0.5rem;">Experience three-tier information architecture</p>
        <p style="opacity: 0.7; font-size: 0.9rem;">Use the sidebar to run a real analysis with live data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced demo opportunities with credibility indicators
    demo_opportunities = [
        {
            "title": "Digital Integration Platform",
            "category": "Product Innovation",
            "description": "Develop IoT-enabled spine fusion devices with real-time monitoring and data analytics capabilities",
            "opportunity_score": 9.2,
            "potential_impact": "$25M-40M revenue potential",
            "time_to_market": "12-18 months",
            "investment_level": "High",
            "implementation_difficulty": "Medium",
            "competitive_risk": "Low",
            "credibility_indicator": "🟢",
            "source_count_display": "5 sources",
            "confidence_level": 9.2,
            "supporting_evidence": "Market research shows 78% of surgeons want IoT integration. Current competitors lack comprehensive digital platforms.",
            "source_urls": [
                "https://pubmed.ncbi.nlm.nih.gov/example1",
                "https://medtechdive.com/example2",
                "https://massdevice.com/example3"
            ],
            "next_steps": [
                "Conduct surgeon interviews to validate feature requirements",
                "Develop MVP with core monitoring capabilities",
                "Partner with hospital systems for pilot programs",
                "Establish data security and compliance framework"
            ],
            "detailed_analysis": """
            ## Methodology
            This opportunity was identified through comprehensive market analysis combining surgeon surveys, competitive intelligence, and technology trend analysis.
            
            ## Market Analysis
            The digital health market in orthopedics is experiencing rapid growth, with IoT-enabled devices representing a $2.3B opportunity by 2027. Current solutions are fragmented, creating an opportunity for integrated platforms.
            
            ## Competitive Landscape
            - **Stryker**: Limited IoT integration, focused on robotics
            - **Medtronic**: Strong in monitoring but lacks comprehensive platform
            - **DePuy Synthes**: Traditional approach, minimal digital integration
            
            ## Implementation Strategy
            Phase 1: Core monitoring platform (6 months)
            Phase 2: Analytics and AI integration (12 months)
            Phase 3: Ecosystem expansion (18 months)
            
            ## Risk Assessment
            - **Technical Risk:** Medium - IoT integration complexity
            - **Market Risk:** Low - Strong surgeon demand validated
            - **Competitive Risk:** Low - First-mover advantage opportunity
            """
        },
        {
            "title": "Value-Based Pricing Model",
            "category": "Pricing Strategy",
            "description": "Implement outcome-based pricing with risk-sharing agreements for improved market penetration",
            "opportunity_score": 8.7,
            "potential_impact": "$15M-25M revenue potential",
            "time_to_market": "6-9 months",
            "investment_level": "Medium",
            "implementation_difficulty": "High",
            "competitive_risk": "Medium",
            "credibility_indicator": "🟡",
            "source_count_display": "3 sources",
            "confidence_level": 8.7,
            "supporting_evidence": "Healthcare systems increasingly demand value-based contracts. 65% of hospitals prefer outcome-based pricing models.",
            "source_urls": [
                "https://healthcaredive.com/example1",
                "https://modernhealthcare.com/example2"
            ],
            "next_steps": [
                "Develop outcome measurement framework",
                "Create risk-sharing contract templates",
                "Pilot with 3-5 health systems",
                "Establish performance tracking systems"
            ]
        },
        {
            "title": "ASC Market Expansion",
            "category": "Market Expansion",
            "description": "Target ambulatory surgery centers with specialized products and support programs",
            "opportunity_score": 8.1,
            "potential_impact": "$10M-20M revenue potential",
            "time_to_market": "6-12 months",
            "investment_level": "Medium",
            "implementation_difficulty": "Low",
            "competitive_risk": "High",
            "credibility_indicator": "🟢",
            "source_count_display": "4 sources",
            "confidence_level": 8.1,
            "supporting_evidence": "ASC market growing 15% annually. Current competitors have limited ASC-specific offerings.",
            "source_urls": [
                "https://beckersasc.com/example1",
                "https://outpatientsurgery.net/example2",
                "https://amsurg.com/example3"
            ],
            "next_steps": [
                "Develop ASC-specific product configurations",
                "Create dedicated sales channel",
                "Establish ASC partnership program",
                "Launch targeted marketing campaign"
            ]
        }
    ]
    
    # Show progressive disclosure opportunities with None analysis_id (demo mode)
    render_opportunities_with_progressive_disclosure(
        demo_opportunities, 
        title="🎯 **STRATEGIC OPPORTUNITIES**",
        analysis_id=None  # None indicates demo mode
    )

if __name__ == "__main__":
    main() 