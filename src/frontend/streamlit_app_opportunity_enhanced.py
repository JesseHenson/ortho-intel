# streamlit_app_opportunity_enhanced.py
"""
Enhanced Opportunity-First Competitive Intelligence Frontend
Executive-ready interface with client customization and flexible competitor input
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
from main_langgraph_opportunity_enhanced import enhanced_opportunity_graph
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
    
    /* Client branding */
    .client-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .client-name {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
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
    
    /* Input styling */
    .input-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
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
        
        .input-section {
            background: rgba(255, 255, 255, 0.05);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
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
        
        # Client Information Section
        st.markdown("#### 👤 Client Information")
        client_name = st.text_input(
            "Client Name",
            value="",
            placeholder="Enter client company name",
            help="The client company name for personalized reports"
        )
        
        if client_name:
            st.markdown(f"""
            <div class="input-section">
                <strong>📊 Analysis for:</strong> {client_name}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Competitor Selection Section
        st.markdown("#### 🏢 Competitor Selection")
        
        # Predefined competitor options
        predefined_competitors = [
            "Stryker Spine", "Zimmer Biomet", "Orthofix", "NuVasive", 
            "Globus Medical", "K2M", "Alphatec", "SeaSpine", "Xtant Medical",
            "Medtronic Spine", "DePuy Synthes", "Smith & Nephew"
        ]
        
        # Selection method
        competitor_input_method = st.radio(
            "How would you like to select competitors?",
            options=["Select from list", "Enter custom competitors", "Mixed selection"],
            index=0,
            help="Choose how to specify competitors for analysis"
        )
        
        competitors = []
        
        if competitor_input_method == "Select from list":
            competitors = st.multiselect(
                "Select Competitors",
                options=predefined_competitors,
                default=["Stryker Spine", "Zimmer Biomet", "Orthofix"],
                help="Choose 2-4 competitors for comprehensive analysis"
            )
            
        elif competitor_input_method == "Enter custom competitors":
            custom_competitors_text = st.text_area(
                "Enter Competitors (one per line)",
                value="Stryker Spine\nZimmer Biomet\nOrthofix",
                height=100,
                help="Enter competitor names, one per line"
            )
            competitors = [comp.strip() for comp in custom_competitors_text.split('\n') if comp.strip()]
            
        else:  # Mixed selection
            selected_competitors = st.multiselect(
                "Select from Predefined List",
                options=predefined_competitors,
                default=["Stryker Spine"],
                help="Select from common competitors"
            )
            
            additional_competitors_text = st.text_input(
                "Additional Competitors (comma-separated)",
                value="",
                placeholder="Enter additional competitor names",
                help="Add custom competitors separated by commas"
            )
            
            additional_competitors = []
            if additional_competitors_text:
                additional_competitors = [comp.strip() for comp in additional_competitors_text.split(',') if comp.strip()]
            
            competitors = selected_competitors + additional_competitors
        
        # Display selected competitors
        if competitors:
            st.markdown("**Selected Competitors:**")
            for i, comp in enumerate(competitors, 1):
                st.markdown(f"{i}. {comp}")
        
        # Competitor search hint (future feature)
        with st.expander("🔍 Need help finding competitors?"):
            st.markdown("""
            **Coming Soon: Intelligent Competitor Search**
            
            We're developing an AI-powered competitor discovery feature that will:
            - Suggest relevant competitors based on your market segment
            - Identify emerging competitors and new market entrants
            - Provide competitor profiles and market positioning insights
            
            For now, you can:
            - Use the predefined list of major orthopedic companies
            - Enter custom competitor names if you know specific companies
            - Contact support for competitor research assistance
            """)
        
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
        
        # Validation and run button
        can_run_analysis = bool(competitors and len(competitors) >= 1)
        
        if not can_run_analysis:
            st.warning("⚠️ Please select at least one competitor to run analysis")
        
        # Run analysis button
        run_analysis = st.button(
            "🚀 Run Opportunity Analysis",
            type="primary",
            use_container_width=True,
            disabled=not can_run_analysis
        )
    
    # Main content area
    if run_analysis and competitors:
        run_opportunity_analysis(competitors, focus_area, analysis_type, client_name)
    else:
        show_demo_dashboard(client_name)

def run_opportunity_analysis(competitors: List[str], focus_area: str, analysis_type: str, client_name: str = ""):
    """Run the opportunity-first analysis with client context"""
    
    # Client header if provided
    if client_name:
        st.markdown(f"""
        <div class="client-header">
            <div class="client-name">{client_name}</div>
            <div>Competitive Intelligence Report</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">{datetime.now().strftime('%B %d, %Y')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🔍 Initializing opportunity analysis...")
        progress_bar.progress(10)
        
        # Run the enhanced pipeline
        status_text.text("📊 Researching competitors and market opportunities...")
        progress_bar.progress(30)
        
        result = enhanced_opportunity_graph.run_analysis(competitors, focus_area, client_name)
        
        progress_bar.progress(70)
        status_text.text("💡 Generating strategic opportunities...")
        
        if "error" in result:
            st.error(f"Analysis failed: {result['error']}")
            return
        
        progress_bar.progress(90)
        status_text.text("📋 Finalizing opportunity dashboard...")
        
        # Display results with client context
        display_opportunity_results(result, competitors, focus_area, client_name)
        
        progress_bar.progress(100)
        status_text.text("✅ Opportunity analysis complete!")
        
        # Clear progress after 2 seconds
        import time
        time.sleep(2)
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        st.error("Please check your internet connection and try again.")
        progress_bar.empty()
        status_text.empty()

def display_opportunity_results(result: Dict[str, Any], competitors: List[str], focus_area: str, client_name: str = ""):
    """Display the opportunity-first analysis results with client context"""
    
    # Extract key data
    final_report = result.get("final_report", {})
    top_opportunities = result.get("top_opportunities", [])
    executive_summary = result.get("executive_summary", {})
    
    # Analysis metadata
    analysis_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    
    # Hero Section - Top 3 Opportunities
    st.markdown("## 🎯 **TOP STRATEGIC OPPORTUNITIES**")
    if client_name:
        st.markdown(f"*Immediate insights for {client_name}'s competitive advantage*")
    else:
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
    
    # Opportunity Matrix
    if result.get("opportunity_matrix"):
        st.markdown("## 📈 **OPPORTUNITY MATRIX**")
        st.markdown("*Impact vs Implementation Difficulty*")
        
        matrix_chart = create_opportunity_matrix_chart(result["opportunity_matrix"])
        if matrix_chart:
            st.plotly_chart(matrix_chart, use_container_width=True)
    
    # Category-specific opportunities
    st.markdown("## 🎯 **CATEGORY OPPORTUNITIES**")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏷️ Brand Strategy", "🔬 Product Innovation", "💰 Pricing Strategy", "🌍 Market Expansion"])
    
    with tab1:
        brand_opps = result.get("brand_opportunities", [])
        if brand_opps:
            display_category_opportunities(brand_opps, "Brand Strategy")
        else:
            st.info("No specific brand opportunities identified in this analysis.")
    
    with tab2:
        product_opps = result.get("product_opportunities", [])
        if product_opps:
            display_category_opportunities(product_opps, "Product Innovation")
        else:
            st.info("No specific product opportunities identified in this analysis.")
    
    with tab3:
        pricing_opps = result.get("pricing_opportunities", [])
        if pricing_opps:
            display_category_opportunities(pricing_opps, "Pricing Strategy")
        else:
            st.info("No specific pricing opportunities identified in this analysis.")
    
    with tab4:
        market_opps = result.get("market_opportunities", [])
        if market_opps:
            display_category_opportunities(market_opps, "Market Expansion")
        else:
            st.info("No specific market expansion opportunities identified in this analysis.")
    
    # Competitive Landscape
    competitive_landscape = result.get("competitive_landscape", {})
    if competitive_landscape:
        st.markdown("## 🏢 **COMPETITIVE LANDSCAPE**")
        
        for competitor, profile in competitive_landscape.items():
            with st.expander(f"📊 {competitor} Profile"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Strengths:**")
                    for strength in profile.get("strengths", []):
                        st.markdown(f"• {strength}")
                    
                    st.markdown("**Market Share:**")
                    st.markdown(f"• {profile.get('market_share', 'Analysis-based')}")
                
                with col2:
                    st.markdown("**Weaknesses:**")
                    for weakness in profile.get("weaknesses", []):
                        st.markdown(f"• {weakness}")
                    
                    st.markdown("**Opportunities Against:**")
                    for opp in profile.get("opportunities_against", []):
                        st.markdown(f"• {opp}")
    
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

def display_category_opportunities(opportunities: List[Dict], category: str):
    """Display category-specific opportunities"""
    for i, opp in enumerate(opportunities):
        with st.container():
            st.markdown(f"""
            <div class="category-tab">
                <h4>{opp.get('opportunity', f'{category} Opportunity {i+1}')}</h4>
                <p><strong>Current Gap:</strong> {opp.get('current_gap', 'Gap identified')}</p>
                <p><strong>Recommendation:</strong> {opp.get('recommendation', 'Strategic recommendation')}</p>
                <p><strong>Implementation:</strong> {opp.get('implementation', 'Implementation approach')}</p>
                <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                    <span><strong>Timeline:</strong> {opp.get('timeline', '6-12 months')}</span>
                    <span><strong>Investment:</strong> {opp.get('investment', 'Medium')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_opportunity_matrix_chart(matrix_data: Dict):
    """Create interactive opportunity matrix visualization"""
    try:
        # Prepare data for plotting
        all_opportunities = []
        colors = []
        
        # Process each quadrant
        quadrants = {
            "high_impact_easy": ("Quick Wins", "#11998e"),
            "high_impact_hard": ("Strategic Investments", "#ff6b6b"),
            "low_impact_easy": ("Fill-ins", "#ffa726"),
            "low_impact_hard": ("Avoid", "#95a5a6")
        }
        
        for quadrant, (label, color) in quadrants.items():
            opportunities = matrix_data.get(quadrant, [])
            for opp in opportunities:
                all_opportunities.append({
                    "name": opp.get("name", "Opportunity"),
                    "impact": opp.get("impact", 5),
                    "difficulty": opp.get("difficulty", 5),
                    "quadrant": label,
                    "color": color
                })
        
        if not all_opportunities:
            return None
        
        # Create DataFrame
        df = pd.DataFrame(all_opportunities)
        
        # Create scatter plot
        fig = px.scatter(
            df, 
            x="difficulty", 
            y="impact",
            color="quadrant",
            hover_name="name",
            title="Opportunity Impact vs Implementation Difficulty",
            labels={
                "difficulty": "Implementation Difficulty",
                "impact": "Business Impact"
            },
            color_discrete_map={
                "Quick Wins": "#11998e",
                "Strategic Investments": "#ff6b6b", 
                "Fill-ins": "#ffa726",
                "Avoid": "#95a5a6"
            }
        )
        
        # Add quadrant lines
        fig.add_hline(y=6.5, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=5.5, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig.add_annotation(x=2, y=9, text="Quick Wins", showarrow=False, font=dict(size=14, color="#11998e"))
        fig.add_annotation(x=8, y=9, text="Strategic Investments", showarrow=False, font=dict(size=14, color="#ff6b6b"))
        fig.add_annotation(x=2, y=2, text="Fill-ins", showarrow=False, font=dict(size=14, color="#ffa726"))
        fig.add_annotation(x=8, y=2, text="Avoid", showarrow=False, font=dict(size=14, color="#95a5a6"))
        
        # Update layout
        fig.update_layout(
            xaxis=dict(range=[0, 10]),
            yaxis=dict(range=[0, 10]),
            height=500,
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating opportunity matrix chart: {str(e)}")
        return None

def show_demo_dashboard(client_name: str = ""):
    """Show demo dashboard with sample data"""
    
    if client_name:
        st.markdown(f"""
        <div class="client-header">
            <div class="client-name">{client_name}</div>
            <div>Demo Dashboard</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">Sample Competitive Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## 🎯 **DEMO: TOP STRATEGIC OPPORTUNITIES**")
    st.markdown("*Sample analysis showing platform capabilities*")
    
    # Demo opportunities
    demo_opportunities = [
        {
            "title": "Digital Integration Platform",
            "description": "Develop IoT-enabled orthopedic devices with real-time patient monitoring and data analytics capabilities",
            "opportunity_score": 9.2,
            "potential_impact": "$25M-50M revenue opportunity",
            "time_to_market": "12-18 months",
            "investment_level": "High"
        },
        {
            "title": "Value-Based Pricing Model",
            "description": "Implement outcome-based pricing with risk-sharing agreements for improved market penetration",
            "opportunity_score": 8.7,
            "potential_impact": "15-20% margin improvement",
            "time_to_market": "6-9 months", 
            "investment_level": "Medium"
        },
        {
            "title": "ASC Market Expansion",
            "description": "Target ambulatory surgery centers with specialized product line and support programs",
            "opportunity_score": 8.1,
            "potential_impact": "10-15% market share gain",
            "time_to_market": "9-12 months",
            "investment_level": "Medium"
        }
    ]
    
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
    st.markdown("## 📊 **DEMO METRICS**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">3</div>
            <div class="metric-label">Strategic Opportunities</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">$25M+</div>
            <div class="metric-label">Revenue Potential</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">15%</div>
            <div class="metric-label">Market Share Gain</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Instructions
    st.markdown("---")
    st.info("""
    **👈 Configure your analysis in the sidebar to see live results!**
    
    1. Enter your client name for personalized reports
    2. Select competitors using the flexible input options
    3. Choose your focus area and analysis type
    4. Click 'Run Opportunity Analysis' to generate real insights
    """)

if __name__ == "__main__":
    main() 