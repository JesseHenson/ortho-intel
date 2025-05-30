"""
Enhanced Demo Frontend for Orthopedic Competitive Intelligence
Works with both demo data and live pipeline data
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from demo_frontend_adapter import get_demo_or_live_data

# Page configuration
st.set_page_config(
    page_title="Orthopedic Intelligence Platform",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .opportunity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .insight-box {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🦴 Orthopedic Competitive Intelligence Platform</h1>', unsafe_allow_html=True)
    
    # Sidebar for data source selection
    st.sidebar.title("Analysis Configuration")
    
    # Data source selection
    data_source = st.sidebar.radio(
        "Data Source",
        ["Demo Data (Recommended)", "Live Analysis (Experimental)"],
        help="Demo data is stable and showcases all features. Live analysis uses your current pipeline."
    )
    
    use_demo = data_source == "Demo Data (Recommended)"
    
    # Configuration for live analysis
    competitors = None
    focus_area = "spine_fusion"
    
    if not use_demo:
        st.sidebar.subheader("Live Analysis Settings")
        
        # Competitor selection
        competitor_options = ["Stryker Spine", "Zimmer Biomet", "Orthofix", "Medtronic Spine", "NuVasive"]
        competitors = st.sidebar.multiselect(
            "Select Competitors",
            competitor_options,
            default=["Stryker Spine", "Zimmer Biomet"],
            help="Choose competitors for live analysis"
        )
        
        # Focus area selection
        focus_area = st.sidebar.selectbox(
            "Focus Area",
            ["spine_fusion", "joint_replacement", "trauma_fixation"],
            help="Select the medical device category to analyze"
        )
        
        if not competitors:
            st.sidebar.warning("Please select at least one competitor for live analysis.")
            return
    
    # Load data
    with st.spinner("Loading analysis data..." if not use_demo else "Loading demo data..."):
        try:
            analysis_data = get_demo_or_live_data(
                use_demo=use_demo,
                competitors=competitors,
                focus_area=focus_area
            )
        except Exception as e:
            st.error(f"Failed to load data: {str(e)}")
            st.info("Falling back to demo data...")
            analysis_data = get_demo_or_live_data(use_demo=True)
    
    # Display data source info
    metadata = analysis_data.get("analysis_metadata", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Analysis Type", metadata.get("analysis_type", "Demo Analysis"))
    with col2:
        st.metric("Device Category", metadata.get("device_category", "Spine Fusion"))
    with col3:
        st.metric("Competitors", len(metadata.get("competitors_analyzed", [])))
    with col4:
        st.metric("Analysis Date", metadata.get("analysis_date", "2024-01-15"))
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Top Opportunities", 
        "📊 Opportunity Matrix", 
        "🏢 Category Analysis", 
        "🏆 Competitive Landscape", 
        "📋 Executive Summary"
    ])
    
    with tab1:
        display_top_opportunities(analysis_data)
    
    with tab2:
        display_opportunity_matrix(analysis_data)
    
    with tab3:
        display_category_analysis(analysis_data)
    
    with tab4:
        display_competitive_landscape(analysis_data)
    
    with tab5:
        display_executive_summary(analysis_data)

def display_top_opportunities(data):
    """Display top strategic opportunities"""
    st.header("🎯 Top Strategic Opportunities")
    
    opportunities = data.get("top_opportunities", [])
    
    if not opportunities:
        st.warning("No opportunities found in the analysis data.")
        return
    
    for i, opp in enumerate(opportunities[:3]):  # Top 3
        with st.container():
            st.markdown(f"""
            <div class="opportunity-card">
                <h3>#{i+1}: {opp.get('title', 'Opportunity')}</h3>
                <p><strong>Category:</strong> {opp.get('category', 'N/A')}</p>
                <p>{opp.get('description', 'No description available')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                score = opp.get('opportunity_score', 0)
                st.metric("Opportunity Score", f"{score}/10")
            with col2:
                difficulty = opp.get('implementation_difficulty', 'Unknown')
                st.metric("Difficulty", difficulty)
            with col3:
                timeline = opp.get('time_to_market', 'Unknown')
                st.metric("Timeline", timeline)
            with col4:
                investment = opp.get('investment_level', 'Unknown')
                st.metric("Investment", investment)
            
            # Next steps
            next_steps = opp.get('next_steps', [])
            if next_steps:
                st.subheader("Next Steps")
                for step in next_steps:
                    st.write(f"• {step}")
            
            # Supporting evidence
            evidence = opp.get('supporting_evidence', '')
            if evidence:
                st.markdown(f"""
                <div class="insight-box">
                    <strong>Supporting Evidence:</strong><br>
                    {evidence}
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()

def display_opportunity_matrix(data):
    """Display opportunity matrix visualization"""
    st.header("📊 Opportunity Impact vs. Implementation Matrix")
    
    matrix_data = data.get("opportunity_matrix", {})
    
    if not matrix_data:
        st.warning("No opportunity matrix data available.")
        return
    
    # Prepare data for plotting
    plot_data = []
    colors = []
    
    for category, opportunities in matrix_data.items():
        for opp in opportunities:
            plot_data.append({
                'name': opp.get('name', 'Unknown'),
                'impact': opp.get('impact', 5),
                'difficulty': opp.get('difficulty', 5),
                'category': category.replace('_', ' ').title()
            })
            
            # Color coding based on category
            if 'high_impact' in category:
                colors.append('#2E8B57' if 'easy' in category else '#FF6347')
            else:
                colors.append('#87CEEB' if 'easy' in category else '#DDA0DD')
    
    if plot_data:
        df = pd.DataFrame(plot_data)
        
        # Create scatter plot
        fig = px.scatter(
            df, 
            x='difficulty', 
            y='impact',
            text='name',
            color='category',
            title="Opportunity Matrix: Impact vs Implementation Difficulty",
            labels={
                'difficulty': 'Implementation Difficulty (1-10)',
                'impact': 'Business Impact (1-10)'
            },
            size_max=20
        )
        
        # Add quadrant lines
        fig.add_hline(y=5, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=5, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig.add_annotation(x=2.5, y=8.5, text="Quick Wins", showarrow=False, font=dict(size=14, color="green"))
        fig.add_annotation(x=7.5, y=8.5, text="Major Projects", showarrow=False, font=dict(size=14, color="orange"))
        fig.add_annotation(x=2.5, y=2.5, text="Fill-ins", showarrow=False, font=dict(size=14, color="blue"))
        fig.add_annotation(x=7.5, y=2.5, text="Questionable", showarrow=False, font=dict(size=14, color="red"))
        
        fig.update_traces(textposition="top center")
        fig.update_layout(height=600)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No opportunity matrix data to display.")

def display_category_analysis(data):
    """Display category-specific opportunities"""
    st.header("🏢 Category-Specific Opportunities")
    
    categories = {
        "Brand Strategy": data.get("brand_opportunities", []),
        "Product Innovation": data.get("product_opportunities", []),
        "Pricing Strategy": data.get("pricing_opportunities", []),
        "Market Expansion": data.get("market_opportunities", [])
    }
    
    for category_name, opportunities in categories.items():
        if opportunities:
            st.subheader(f"📈 {category_name}")
            
            for opp in opportunities:
                with st.expander(f"💡 {opp.get('opportunity', 'Opportunity')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Current Gap:**")
                        st.write(opp.get('current_gap', 'No gap information'))
                        
                        st.write("**Recommendation:**")
                        st.write(opp.get('recommendation', 'No recommendation'))
                    
                    with col2:
                        st.write("**Implementation:**")
                        st.write(opp.get('implementation', 'No implementation details'))
                        
                        col2a, col2b = st.columns(2)
                        with col2a:
                            st.metric("Timeline", opp.get('timeline', 'Unknown'))
                        with col2b:
                            st.metric("Investment", opp.get('investment', 'Unknown'))
        else:
            st.subheader(f"📈 {category_name}")
            st.info(f"No {category_name.lower()} opportunities identified in this analysis.")

def display_competitive_landscape(data):
    """Display competitive landscape analysis"""
    st.header("🏆 Competitive Landscape")
    
    landscape = data.get("competitive_landscape", {})
    market_leaders = landscape.get("market_leaders", {})
    
    if not market_leaders:
        st.warning("No competitive landscape data available.")
        return
    
    for competitor, profile in market_leaders.items():
        with st.expander(f"🏢 {competitor}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Strengths")
                strengths = profile.get('strengths', [])
                for strength in strengths:
                    st.write(f"✅ {strength}")
                
                st.subheader("Market Share")
                st.write(profile.get('market_share', 'Unknown'))
            
            with col2:
                st.subheader("Weaknesses")
                weaknesses = profile.get('weaknesses', [])
                for weakness in weaknesses:
                    st.write(f"❌ {weakness}")
                
                st.subheader("Opportunities Against")
                opportunities = profile.get('opportunities_against', [])
                for opp in opportunities:
                    st.write(f"🎯 {opp}")

def display_executive_summary(data):
    """Display executive summary"""
    st.header("📋 Executive Summary")
    
    summary = data.get("executive_summary", {})
    
    if not summary:
        st.warning("No executive summary available.")
        return
    
    # Key insight
    key_insight = summary.get("key_insight", "No key insight available")
    st.markdown(f"""
    <div class="insight-box">
        <h3>🔍 Key Insight</h3>
        <p>{key_insight}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Two columns for actions and recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚡ Immediate Actions")
        actions = summary.get("immediate_actions", [])
        for action in actions:
            st.write(f"• {action}")
    
    with col2:
        st.subheader("🎯 Strategic Recommendations")
        recommendations = summary.get("strategic_recommendations", [])
        for rec in recommendations:
            st.write(f"• {rec}")
    
    # Additional summary metrics if available
    if any(key in summary for key in ["revenue_potential", "market_share_opportunity", "investment_required"]):
        st.subheader("📊 Business Impact Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            revenue = summary.get("revenue_potential", "Not specified")
            st.metric("Revenue Potential", revenue)
        
        with col2:
            market_share = summary.get("market_share_opportunity", "Not specified")
            st.metric("Market Share Opportunity", market_share)
        
        with col3:
            investment = summary.get("investment_required", "Not specified")
            st.metric("Investment Required", investment)

if __name__ == "__main__":
    main() 