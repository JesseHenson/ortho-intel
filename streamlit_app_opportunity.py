# streamlit_app_opportunity.py
"""
Opportunity-First Competitive Intelligence Frontend
Executive-ready interface prioritizing actionable opportunities
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import json
from typing import Dict, List, Any

# Import the enhanced opportunity pipeline
from main_langgraph_opportunity import opportunity_graph
from opportunity_data_models import (
    StrategicOpportunity, 
    CategoryOpportunity, 
    ExecutiveSummary,
    OpportunityAnalysisResponse
)

# Page configuration
st.set_page_config(
    page_title="Orthopedic Intelligence - Opportunity Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
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
    
    # Header with opportunity focus
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #667eea; font-size: 3rem; margin-bottom: 0.5rem;">🎯 Orthopedic Intelligence</h1>
        <h2 style="color: #666; font-size: 1.5rem; font-weight: 300;">Opportunity-First Competitive Intelligence</h2>
        <p style="color: #888; font-size: 1.1rem;">Immediate insights for strategic advantage</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for analysis configuration
    with st.sidebar:
        st.markdown("### 🔍 Analysis Configuration")
        
        # Client name input (NEW - added above existing controls)
        client_name = st.text_input(
            "Client Name (Optional)",
            placeholder="Enter client name for personalized analysis",
            help="Personalize the analysis report with your client's name"
        )
        
        # Competitor selection (ENHANCED - kept original structure)
        predefined_competitors = [
            "Stryker Spine", "Zimmer Biomet", "Orthofix", "NuVasive", 
            "Globus Medical", "K2M", "Alphatec", "SeaSpine", "Xtant Medical"
        ]
        
        competitors = st.multiselect(
            "Select Competitors",
            options=predefined_competitors,
            default=["Stryker Spine", "Zimmer Biomet", "Orthofix"],
            help="Choose 2-4 competitors for comprehensive analysis"
        )
        
        # Custom competitor input (NEW - added below existing)
        custom_competitor = st.text_input(
            "Add Custom Competitor",
            placeholder="Enter competitor name",
            help="Add a competitor not in the predefined list"
        )
        
        # Add custom competitor to list if provided
        if custom_competitor and custom_competitor not in competitors:
            competitors.append(custom_competitor)
        
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
        
        # Run analysis button
        run_analysis = st.button(
            "🚀 Run Opportunity Analysis",
            type="primary",
            use_container_width=True
        )
    
    # Main content area
    if run_analysis and competitors:
        run_opportunity_analysis(competitors, focus_area, analysis_type, client_name)
    else:
        show_demo_dashboard()

def run_opportunity_analysis(competitors: List[str], focus_area: str, analysis_type: str, client_name: str = ""):
    """Run the opportunity-first analysis"""
    
    # Progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🔍 Initializing opportunity analysis...")
        progress_bar.progress(10)
        
        # Run the enhanced pipeline
        status_text.text("📊 Researching competitors and market opportunities...")
        progress_bar.progress(30)
        
        # Use enhanced backend (now the main backend has all enhancements)
        result = opportunity_graph.run_analysis(competitors, focus_area)
        
        progress_bar.progress(70)
        status_text.text("💡 Generating strategic opportunities...")
        
        if "error" in result:
            st.error(f"Analysis failed: {result['error']}")
            return
        
        progress_bar.progress(90)
        status_text.text("📋 Finalizing opportunity dashboard...")
        
        # Display results
        display_opportunity_results(result, competitors, focus_area)
        
        progress_bar.progress(100)
        status_text.text("✅ Opportunity analysis complete!")
        
        # Clear progress after 2 seconds
        import time
        time.sleep(2)
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        progress_bar.empty()
        status_text.empty()

def display_opportunity_results(result: Dict[str, Any], competitors: List[str], focus_area: str):
    """Display the opportunity-first analysis results"""
    
    # Extract key data
    final_report = result.get("final_report", {})
    top_opportunities = result.get("top_opportunities", [])
    executive_summary = result.get("executive_summary", {})
    
    # Hero Section - Top 3 Opportunities
    st.markdown("## 🎯 **TOP STRATEGIC OPPORTUNITIES**")
    st.markdown("*Immediate insights for competitive advantage*")
    
    if top_opportunities:
        # Display top 3 opportunities prominently
        for i, opp in enumerate(top_opportunities[:3]):
            opportunity_score = opp.get("opportunity_score", 8.0)
            impact = opp.get("potential_impact", "High impact opportunity")
            
            st.markdown(f"""
            <div class="opportunity-card">
                <div class="opportunity-title">#{i+1} {opp.get('title', 'Strategic Opportunity')}</div>
                <div class="opportunity-impact">💰 {impact}</div>
                <p style="margin: 1rem 0; font-size: 1.1rem;">{opp.get('description', '')[:200]}...</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span><strong>Score:</strong> {opportunity_score}/10</span>
                    <span><strong>Timeline:</strong> {opp.get('time_to_market', '6-12 months')}</span>
                    <span><strong>Investment:</strong> {opp.get('investment_level', 'Medium')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Executive Summary
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
    
    # Opportunity Categories
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
    
    # Competitive Landscape
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
    
    # Opportunity Matrix Visualization
    if result.get("opportunity_matrix"):
        st.markdown("## 📈 **OPPORTUNITY MATRIX**")
        create_opportunity_matrix_chart(result["opportunity_matrix"])
    
    # Implementation Roadmap
    if executive_summary.get("immediate_actions"):
        st.markdown("## 🚀 **IMMEDIATE ACTIONS**")
        
        actions = executive_summary.get("immediate_actions", [])
        for i, action in enumerate(actions):
            st.markdown(f"""
            <div class="quick-win">
                <strong>Action {i+1}:</strong> {action}
            </div>
            """, unsafe_allow_html=True)

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
    """Show demo dashboard with sample data"""
    
    st.markdown("## 🎯 **DEMO: TOP STRATEGIC OPPORTUNITIES**")
    st.markdown("*Sample analysis showing opportunity-first intelligence*")
    
    # Demo opportunities
    demo_opportunities = [
        {
            "title": "Digital Integration Platform",
            "description": "Develop IoT-enabled spine fusion devices with real-time monitoring and data analytics capabilities",
            "opportunity_score": 9.2,
            "potential_impact": "$25M-40M revenue potential",
            "time_to_market": "12-18 months",
            "investment_level": "High"
        },
        {
            "title": "Value-Based Pricing Model",
            "description": "Implement outcome-based pricing with risk-sharing agreements for improved market penetration",
            "opportunity_score": 8.7,
            "potential_impact": "$15M-25M revenue potential",
            "time_to_market": "6-9 months",
            "investment_level": "Medium"
        },
        {
            "title": "ASC Market Expansion",
            "description": "Target ambulatory surgery centers with specialized products and support programs",
            "opportunity_score": 8.1,
            "potential_impact": "$10M-20M revenue potential",
            "time_to_market": "6-12 months",
            "investment_level": "Medium"
        }
    ]
    
    # Display demo opportunities
    for i, opp in enumerate(demo_opportunities):
        st.markdown(f"""
        <div class="opportunity-card">
            <div class="opportunity-title">#{i+1} {opp['title']}</div>
            <div class="opportunity-impact">💰 {opp['potential_impact']}</div>
            <p style="margin: 1rem 0; font-size: 1.1rem;">{opp['description']}</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span><strong>Score:</strong> {opp['opportunity_score']}/10</span>
                <span><strong>Timeline:</strong> {opp['time_to_market']}</span>
                <span><strong>Investment:</strong> {opp['investment_level']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Demo metrics
    st.markdown("## 📊 **MARKET INTELLIGENCE METRICS**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">3</div>
            <div class="metric-label">High-Impact Opportunities</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">$50M+</div>
            <div class="metric-label">Revenue Potential</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">6-18</div>
            <div class="metric-label">Months to Market</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">8.7</div>
            <div class="metric-label">Avg Opportunity Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div class="executive-summary">
        <h3 style="margin-bottom: 1rem;">🚀 Ready to Discover Your Opportunities?</h3>
        <p style="font-size: 1.2rem; line-height: 1.6;">
            Configure your analysis in the sidebar to uncover strategic opportunities 
            specific to your competitive landscape and market focus.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 