"""
Opportunity-First Competitive Intelligence Demo Frontend
Designed for medical device manufacturing companies
Focus: Immediate visibility of actionable opportunities
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from demo_data import get_demo_data, DEMO_SCENARIOS

# Configure page for executive presentation
st.set_page_config(
    page_title="Competitive Opportunity Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .opportunity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
    .quick-win {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
    }
    .high-impact {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
    }
    .action-item {
        background: #eff6ff;
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

def create_opportunity_matrix(matrix_data):
    """Create interactive opportunity matrix visualization"""
    
    # Prepare data for plotting
    all_opportunities = []
    colors = []
    sizes = []
    
    for category, opportunities in matrix_data.items():
        for opp in opportunities:
            all_opportunities.append({
                'name': opp['name'],
                'impact': opp['impact'],
                'difficulty': opp['difficulty'],
                'category': category.replace('_', ' ').title()
            })
            
            # Color coding based on category
            if category == 'high_impact_easy':
                colors.append('#10b981')  # Green - Quick wins
                sizes.append(20)
            elif category == 'high_impact_hard':
                colors.append('#f59e0b')  # Orange - Strategic investments
                sizes.append(25)
            elif category == 'low_impact_easy':
                colors.append('#6b7280')  # Gray - Low priority
                sizes.append(15)
            else:
                colors.append('#ef4444')  # Red - Avoid
                sizes.append(15)
    
    df = pd.DataFrame(all_opportunities)
    
    fig = go.Figure()
    
    for i, category in enumerate(['high_impact_easy', 'high_impact_hard', 'low_impact_easy', 'low_impact_hard']):
        category_data = df[df['category'] == category.replace('_', ' ').title()]
        if not category_data.empty:
            fig.add_trace(go.Scatter(
                x=category_data['difficulty'],
                y=category_data['impact'],
                mode='markers+text',
                name=category.replace('_', ' ').title(),
                text=category_data['name'],
                textposition="top center",
                marker=dict(
                    size=[20 if cat == 'High Impact Easy' else 25 if cat == 'High Impact Hard' else 15 
                          for cat in category_data['category']],
                    color=colors[i] if i < len(colors) else '#6b7280',
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>%{text}</b><br>Impact: %{y}<br>Difficulty: %{x}<extra></extra>'
            ))
    
    fig.update_layout(
        title="Opportunity Impact vs Implementation Difficulty",
        xaxis_title="Implementation Difficulty (1-10)",
        yaxis_title="Business Impact (1-10)",
        height=500,
        showlegend=True,
        plot_bgcolor='white',
        xaxis=dict(range=[0, 10], gridcolor='#f1f5f9'),
        yaxis=dict(range=[0, 10], gridcolor='#f1f5f9')
    )
    
    # Add quadrant labels
    fig.add_annotation(x=2.5, y=8.5, text="🎯 Quick Wins", showarrow=False, 
                      font=dict(size=14, color='#10b981'))
    fig.add_annotation(x=7.5, y=8.5, text="🚀 Strategic Investments", showarrow=False,
                      font=dict(size=14, color='#f59e0b'))
    fig.add_annotation(x=2.5, y=2.5, text="📝 Fill-ins", showarrow=False,
                      font=dict(size=14, color='#6b7280'))
    fig.add_annotation(x=7.5, y=2.5, text="❌ Avoid", showarrow=False,
                      font=dict(size=14, color='#ef4444'))
    
    return fig

def display_top_opportunity_card(opportunity, rank):
    """Display a top opportunity as an attractive card"""
    
    # Determine card styling based on rank
    if rank == 1:
        gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        emoji = "🥇"
    elif rank == 2:
        gradient = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
        emoji = "🥈"
    else:
        gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        emoji = "🥉"
    
    # Score color
    score = opportunity['opportunity_score']
    if score >= 9:
        score_color = "#10b981"
    elif score >= 7:
        score_color = "#f59e0b"
    else:
        score_color = "#6b7280"
    
    st.markdown(f"""
    <div style="background: {gradient}; padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: white;">{emoji} {opportunity['title']}</h3>
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                <strong style="font-size: 1.2rem;">{score}/10</strong>
            </div>
        </div>
        <p style="margin: 0.5rem 0; opacity: 0.9;">{opportunity['description']}</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.9rem;">
                💰 {opportunity['potential_impact']}
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.9rem;">
                ⏱️ {opportunity['time_to_market']}
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.9rem;">
                📊 {opportunity['implementation_difficulty']} Difficulty
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_category_opportunities(opportunities, category_name, icon):
    """Display opportunities for a specific category"""
    
    st.subheader(f"{icon} {category_name} Opportunities")
    
    for i, opp in enumerate(opportunities):
        with st.expander(f"💡 {opp['opportunity']}", expanded=i==0):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Current Gap:** {opp['current_gap']}")
                st.markdown(f"**Recommendation:** {opp['recommendation']}")
                st.markdown(f"**Implementation:** {opp['implementation']}")
            
            with col2:
                st.markdown(f"**Timeline:** {opp['timeline']}")
                st.markdown(f"**Investment:** {opp['investment']}")
                
                # Add action button
                if st.button(f"📋 Create Action Plan", key=f"action_{category_name}_{i}"):
                    st.success("Action plan template created! Check your downloads.")

def main():
    """Main demo application"""
    
    # Header section
    st.markdown('<h1 class="main-header">🎯 Competitive Opportunity Intelligence</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Actionable insights for medical device manufacturers • Demo Version</p>', unsafe_allow_html=True)
    
    # Demo scenario selector
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        scenario = st.selectbox(
            "Select Demo Scenario:",
            options=["spine_fusion", "cardiovascular", "joint_replacement", "diabetes_care"],
            format_func=lambda x: {
                "spine_fusion": "🦴 Spine Fusion Devices",
                "cardiovascular": "🫀 Cardiovascular Devices", 
                "joint_replacement": "🦵 Joint Replacement",
                "diabetes_care": "💉 Diabetes Care"
            }[x]
        )
    
    with col2:
        if st.button("🔄 Refresh Analysis"):
            st.rerun()
    
    with col3:
        if st.button("📊 Export Report"):
            st.success("Report exported!")
    
    # Load demo data
    data = get_demo_data(scenario)
    
    # Client info banner
    st.info(f"**Analysis for:** {data['analysis_metadata']['client_company']} | **Category:** {data['analysis_metadata']['device_category']} | **Competitors:** {', '.join(data['analysis_metadata']['competitors_analyzed'])}")
    
    # HERO SECTION - Top 3 Opportunities
    st.markdown("## 🚀 Top Strategic Opportunities")
    st.markdown("*Your biggest competitive advantages, ranked by impact and feasibility*")
    
    # Display top 3 opportunities as cards
    for i, opportunity in enumerate(data['top_opportunities'][:3], 1):
        display_top_opportunity_card(opportunity, i)
    
    # Executive summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue Impact", 
            data['executive_summary']['estimated_revenue_impact'],
            help="Estimated 3-year revenue opportunity"
        )
    
    with col2:
        st.metric(
            "High-Priority Opportunities", 
            data['executive_summary']['high_priority_opportunities'],
            help="Opportunities requiring immediate attention"
        )
    
    with col3:
        st.metric(
            "Quick Wins Available",
            len([opp for opp in data['top_opportunities'] if opp['implementation_difficulty'] == 'Easy']),
            help="Low-effort, high-impact opportunities"
        )
    
    with col4:
        st.metric(
            "Competitive Advantage",
            "Strong",
            help="Overall competitive position assessment"
        )
    
    # OPPORTUNITY MATRIX
    st.markdown("---")
    st.markdown("## 📊 Opportunity Portfolio Matrix")
    st.markdown("*Visual guide to prioritize your investments*")
    
    matrix_fig = create_opportunity_matrix(data['opportunity_matrix'])
    st.plotly_chart(matrix_fig, use_container_width=True)
    
    # Quick interpretation
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="quick-win">
            <h4>🎯 Quick Wins (Start Here)</h4>
            <p>High impact, low difficulty opportunities. Execute these first for immediate competitive advantage.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="high-impact">
            <h4>🚀 Strategic Investments</h4>
            <p>High impact but challenging. These are your long-term competitive differentiators.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # DETAILED OPPORTUNITY CATEGORIES
    st.markdown("---")
    st.markdown("## 🎯 Detailed Opportunity Analysis")
    
    # Create tabs for different opportunity categories
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Brand", "⚙️ Product", "💰 Pricing", "🌍 Market"])
    
    with tab1:
        display_category_opportunities(data['brand_opportunities'], "Brand Strategy", "🎨")
    
    with tab2:
        display_category_opportunities(data['product_opportunities'], "Product Innovation", "⚙️")
    
    with tab3:
        display_category_opportunities(data['pricing_opportunities'], "Pricing Strategy", "💰")
    
    with tab4:
        display_category_opportunities(data['market_opportunities'], "Market Expansion", "🌍")
    
    # IMMEDIATE ACTION PLAN
    st.markdown("---")
    st.markdown("## ⚡ Immediate Action Plan")
    st.markdown("*Start here - prioritized by speed to market and impact*")
    
    for i, action in enumerate(data['executive_summary']['recommended_immediate_actions'], 1):
        st.markdown(f"""
        <div class="action-item">
            <strong>Action {i}:</strong> {action}
        </div>
        """, unsafe_allow_html=True)
    
    # COMPETITIVE LANDSCAPE (Supporting Info)
    with st.expander("🔍 Competitive Landscape Details", expanded=False):
        st.markdown("### Market Leaders Analysis")
        
        for competitor, details in data['competitive_landscape']['market_leaders'].items():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**{competitor}**")
                st.markdown(f"Market Share: {details['market_share']}")
                st.markdown("**Strengths:**")
                for strength in details['strengths']:
                    st.markdown(f"• {strength}")
            
            with col2:
                st.markdown("**Weaknesses:**")
                for weakness in details['weaknesses']:
                    st.markdown(f"• {weakness}")
            
            with col3:
                st.markdown("**Opportunities Against Them:**")
                for opp in details['opportunities_against']:
                    st.markdown(f"• {opp}")
            
            st.markdown("---")
    
    # Footer with next steps
    st.markdown("---")
    st.markdown("### 🎯 Ready to Act on These Opportunities?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 Schedule Strategy Session", use_container_width=True):
            st.success("Strategy session request sent!")
    
    with col2:
        if st.button("📋 Download Action Plan", use_container_width=True):
            st.success("Detailed action plan downloaded!")
    
    with col3:
        if st.button("🔄 Run New Analysis", use_container_width=True):
            st.info("Contact us to analyze different competitors or markets!")

if __name__ == "__main__":
    main() 