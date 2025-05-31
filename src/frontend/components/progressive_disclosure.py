"""
Progressive Disclosure Components for Opportunity Analysis

Reusable accordion components that implement three-tier information architecture:
- Summary cards for quick scanning
- Detailed views with implementation information  
- Full analysis with sources and methodology

Follows existing design system colors and styling patterns.
Enhanced with real source data and methodology transparency.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, List, Any, Optional
import json
import requests
from datetime import datetime

# Enhanced API Integration Functions

class APIIntegration:
    """
    Integration layer for consuming enhanced analysis API endpoints.
    Provides real source data, methodology transparency, and traceability.
    """
    
    @staticmethod
    def get_base_url() -> str:
        """Get the API base URL from environment or default."""
        import os
        return os.getenv("API_BASE_URL", "http://localhost:8000")
    
    @staticmethod
    def get_methodology(analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive analysis methodology including LangGraph execution details.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Dict containing methodology data or None if error
        """
        try:
            base_url = APIIntegration.get_base_url()
            response = requests.get(f"{base_url}/api/opportunities/{analysis_id}/methodology")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.warning(f"Could not fetch methodology data: {e}")
        return None
    
    @staticmethod
    def get_sources_analysis(analysis_id: str, include_enhanced: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive source credibility analysis.
        
        Args:
            analysis_id: Analysis ID
            include_enhanced: Whether to include enhanced metadata
            
        Returns:
            Dict containing source analysis or None if error
        """
        try:
            base_url = APIIntegration.get_base_url()
            params = {"include_enhanced_metadata": include_enhanced}
            response = requests.get(f"{base_url}/api/opportunities/{analysis_id}/sources/analysis", params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.warning(f"Could not fetch source analysis: {e}")
        return None
    
    @staticmethod
    def get_traceability(analysis_id: str, opportunity_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get complete data flow traceability.
        
        Args:
            analysis_id: Analysis ID
            opportunity_id: Optional specific opportunity ID
            
        Returns:
            Dict containing traceability data or None if error
        """
        try:
            base_url = APIIntegration.get_base_url()
            params = {"opportunity_id": opportunity_id} if opportunity_id else {}
            response = requests.get(f"{base_url}/api/opportunities/{analysis_id}/traceability", params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.warning(f"Could not fetch traceability data: {e}")
        return None
    
    @staticmethod
    def get_quality_report(analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive quality assurance report.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Dict containing quality report or None if error
        """
        try:
            base_url = APIIntegration.get_base_url()
            response = requests.get(f"{base_url}/api/opportunities/{analysis_id}/quality-report")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.warning(f"Could not fetch quality report: {e}")
        return None

class OpportunityCard:
    """
    Summary-level opportunity card for quick scanning.
    Shows essential information without overwhelming detail.
    Enhanced with real source quality indicators.
    """
    
    @staticmethod
    def render(opportunity: Dict[str, Any], index: int = 0, show_expand_button: bool = True, 
               analysis_id: Optional[str] = None) -> bool:
        """
        Render a summary opportunity card with real source quality indicators.
        
        Args:
            opportunity: Opportunity data dictionary
            index: Card index for unique keys
            show_expand_button: Whether to show expand button
            analysis_id: Analysis ID for fetching enhanced data
            
        Returns:
            bool: True if user clicked expand, False otherwise
        """
        # Extract key information
        title = opportunity.get("title", f"Strategic Opportunity {index + 1}")
        opportunity_score = opportunity.get("opportunity_score", 8.0)
        category = opportunity.get("category", "Strategic")
        time_to_market = opportunity.get("time_to_market", "6-12 months")
        investment_level = opportunity.get("investment_level", "Medium")
        
        # Enhanced source quality indicators from progressive disclosure models
        source_quality_indicator = opportunity.get("source_quality_indicator", "🟡")
        methodology_confidence = opportunity.get("methodology_confidence", 7.0)
        evidence_strength = opportunity.get("evidence_strength", "Moderate")
        source_diversity_score = opportunity.get("source_diversity_score", 7.0)
        
        # Real source count from actual data
        source_urls = opportunity.get("source_urls", [])
        source_count_display = f"{len(source_urls)} sources" if source_urls else "Multiple sources"
        
        # Enhanced confidence display based on multiple factors
        overall_confidence = (opportunity_score + methodology_confidence + source_diversity_score) / 3
        confidence_color = "#11998e" if overall_confidence >= 8.0 else "#ffa726" if overall_confidence >= 6.0 else "#ff6b6b"
        
        # Create expandable container with enhanced styling
        with st.container():
            html_content = f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; 
                        padding: 1.5rem; 
                        border-radius: 12px; 
                        margin: 1rem 0; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div style="font-size: 1.3rem; font-weight: 700;">#{index + 1} {title}</div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;" title="Source Quality Indicator">{source_quality_indicator}</span>
                        <span style="font-size: 0.9rem; opacity: 0.8;">{source_count_display}</span>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span style="background: rgba(255,255,255,0.2); 
                                 padding: 0.3rem 0.8rem; 
                                 border-radius: 15px; 
                                 font-size: 0.9rem;">
                        {category}
                    </span>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem; font-weight: 700;">
                            Score: {opportunity_score}/10
                        </span>
                        <div style="width: 8px; height: 8px; border-radius: 50%; background: {confidence_color};" 
                             title="Overall Confidence: {overall_confidence:.1f}/10"></div>
                    </div>
                </div>
                
                <div style="display: grid; 
                           grid-template-columns: 1fr 1fr; 
                           gap: 1rem; 
                           margin-top: 1rem;">
                    <div>
                        <strong>⏱️ Timeline:</strong><br>
                        <span style="font-size: 0.95rem;">{time_to_market}</span>
                    </div>
                    <div>
                        <strong>💰 Investment:</strong><br>
                        <span style="font-size: 0.95rem;">{investment_level}</span>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; 
                           margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
                    <span style="font-size: 0.8rem; opacity: 0.8;">Evidence: {evidence_strength}</span>
                    <span style="font-size: 0.8rem; opacity: 0.8;">Confidence: {methodology_confidence:.1f}/10</span>
                </div>
            </div>
            """
            
            # Use st.components.v1.html() for reliable HTML rendering
            components.html(html_content, height=220)
            
            # Expand button if requested
            if show_expand_button:
                expand_key = f"expand_opp_{index}_{hash(title)}"
                if st.button("📋 View Details", key=expand_key, help="Click to see implementation details and sources"):
                    return True
                    
        return False

class OpportunityDetails:
    """
    Detailed view with implementation information and business impact.
    Second tier of progressive disclosure.
    Enhanced with real source insights and methodology summary.
    """
    
    @staticmethod
    def render(opportunity: Dict[str, Any], index: int = 0, show_full_analysis_button: bool = True,
               analysis_id: Optional[str] = None) -> bool:
        """
        Render detailed opportunity information with enhanced source insights.
        
        Args:
            opportunity: Opportunity data dictionary
            index: Card index for unique keys
            show_full_analysis_button: Whether to show full analysis button
            analysis_id: Analysis ID for fetching enhanced data
            
        Returns:
            bool: True if user clicked full analysis, False otherwise
        """
        # Extract detailed information
        title = opportunity.get("title", f"Strategic Opportunity {index + 1}")
        description = opportunity.get("description", "Strategic opportunity for competitive advantage")
        potential_impact = opportunity.get("potential_impact", "Significant business impact expected")
        implementation_difficulty = opportunity.get("implementation_difficulty", "Medium")
        competitive_risk = opportunity.get("competitive_risk", "Medium")
        next_steps = opportunity.get("next_steps", [])
        
        # Enhanced progressive disclosure fields
        evidence_summary = opportunity.get("evidence_summary", "Analysis based on competitive research")
        source_highlights = opportunity.get("source_highlights", [])
        credibility_breakdown = opportunity.get("credibility_breakdown", {})
        geographic_coverage = opportunity.get("geographic_coverage", [])
        methodology_summary = opportunity.get("methodology_summary", "AI-powered competitive analysis")
        
        # Risk and difficulty indicators
        risk_color = {"Low": "#11998e", "Medium": "#ffa726", "High": "#ff6b6b"}.get(
            str(implementation_difficulty).title(), "#ffa726")
        difficulty_color = {"Low": "#11998e", "Medium": "#ffa726", "High": "#ff6b6b"}.get(
            str(competitive_risk).title(), "#ffa726")
        
        with st.container():
            html_content = f"""
            <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 1rem 0;">
                <h3 style="color: #667eea; margin-bottom: 1rem;">{title}</h3>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">📝 Description</h4>
                    <p style="line-height: 1.6; color: #555;">{description}</p>
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">💰 Business Impact</h4>
                    <p style="line-height: 1.6; color: #555;">{potential_impact}</p>
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">🔍 Evidence Summary</h4>
                    <p style="line-height: 1.6; color: #555; background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                        {evidence_summary}
                    </p>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid {difficulty_color};">
                        <h5 style="margin-bottom: 0.5rem; color: #2c3e50;">🔧 Implementation Difficulty</h5>
                        <span style="color: {difficulty_color}; font-weight: 600;">{implementation_difficulty}</span>
                    </div>
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid {risk_color};">
                        <h5 style="margin-bottom: 0.5rem; color: #2c3e50;">⚠️ Competitive Risk</h5>
                        <span style="color: {risk_color}; font-weight: 600;">{competitive_risk}</span>
                    </div>
                </div>
            </div>
            """
            
            # Use st.components.v1.html() for reliable HTML rendering
            components.html(html_content, height=450)
            
            # Enhanced source highlights if available
            if source_highlights:
                st.markdown("#### 💡 Key Source Insights")
                for i, highlight in enumerate(source_highlights[:3]):  # Show top 3
                    st.markdown(f"**{i+1}.** {highlight}")
            
            # Credibility breakdown if available
            if credibility_breakdown:
                st.markdown("#### 📊 Source Credibility Breakdown")
                col1, col2, col3 = st.columns(3)
                
                high_cred = credibility_breakdown.get("high_credibility_sources", 0)
                medium_cred = credibility_breakdown.get("medium_credibility_sources", 0)
                low_cred = credibility_breakdown.get("low_credibility_sources", 0)
                
                with col1:
                    st.metric("🟢 High Credibility", high_cred)
                with col2:
                    st.metric("🟡 Medium Credibility", medium_cred)
                with col3:
                    st.metric("🔴 Low Credibility", low_cred)
            
            # Geographic coverage if available
            if geographic_coverage:
                st.markdown("#### 🌍 Geographic Coverage")
                st.markdown(", ".join(geographic_coverage[:5]))  # Show top 5 regions
            
            # Methodology summary
            if methodology_summary:
                st.markdown("#### 🔬 Analysis Methodology")
                st.info(f"**Method:** {methodology_summary}")
            
            # Next steps if available
            if next_steps:
                st.markdown("#### 🎯 Recommended Next Steps")
                for i, step in enumerate(next_steps[:5]):  # Limit to 5 steps
                    st.markdown(f"**{i+1}.** {step}")
            
            # Full analysis button if requested
            if show_full_analysis_button:
                full_analysis_key = f"full_analysis_opp_{index}_{hash(title)}"
                if st.button("🔍 View Full Analysis & Methodology", key=full_analysis_key, 
                           help="See complete analysis with sources, methodology transparency, and traceability"):
                    return True
                    
        return False

class AnalysisBreakdown:
    """
    Complete analysis view with sources, methodology, and detailed planning.
    Third tier of progressive disclosure - most comprehensive view.
    Enhanced with methodology transparency and traceability.
    """
    
    @staticmethod
    def render(opportunity: Dict[str, Any], index: int = 0, analysis_id: Optional[str] = None):
        """
        Render complete opportunity analysis breakdown with methodology transparency.
        
        Args:
            opportunity: Opportunity data dictionary
            index: Card index for unique keys
            analysis_id: Analysis ID for fetching enhanced methodology data
        """
        # Extract comprehensive information
        title = opportunity.get("title", f"Strategic Opportunity {index + 1}")
        supporting_evidence = opportunity.get("supporting_evidence", "Analysis based on competitive research")
        source_urls = opportunity.get("source_urls", [])
        confidence_level = opportunity.get("confidence_level", 7.5)
        detailed_analysis = opportunity.get("detailed_analysis", "")
        
        # Enhanced progressive disclosure fields from OpportunityFull model
        market_context = opportunity.get("market_context", {})
        competitive_intelligence = opportunity.get("competitive_intelligence", {})
        reasoning_chains = opportunity.get("reasoning_chains", [])
        decision_audit_trail = opportunity.get("decision_audit_trail", [])
        langgraph_execution_trace = opportunity.get("langgraph_execution_trace", [])
        quality_assurance_report = opportunity.get("quality_assurance_report", {})
        
        # Get enhanced methodology data if analysis_id is provided
        methodology_data = None
        sources_analysis = None
        traceability_data = None
        quality_report = None
        
        if analysis_id:
            methodology_data = APIIntegration.get_methodology(analysis_id)
            sources_analysis = APIIntegration.get_sources_analysis(analysis_id, include_enhanced=True)
            traceability_data = APIIntegration.get_traceability(analysis_id, opportunity.get("id"))
            quality_report = APIIntegration.get_quality_report(analysis_id)
        
        with st.container():
            # Main analysis header with enhanced confidence visualization
            overall_confidence = confidence_level
            if quality_report:
                overall_confidence = quality_report.get("overall_quality_score", confidence_level)
            
            html_content = f"""
            <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 2rem; border-radius: 15px; margin: 1rem 0;">
                <h3 style="margin-bottom: 1.5rem; color: white;">🔍 Complete Analysis: {title}</h3>
                
                <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;">
                    <h4 style="color: #ffd700; margin-bottom: 1rem;">📊 Analysis Confidence & Quality</h4>
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                        <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                            <strong>{overall_confidence:.1f}/10</strong>
                        </div>
                        <div style="flex: 1; background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px;">
                            <div style="background: #ffd700; height: 100%; width: {overall_confidence * 10}%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    {f'<div style="font-size: 0.9rem; opacity: 0.9;">Quality Grade: {quality_report.get("quality_grade", "B")}</div>' if quality_report else ''}
                </div>
            </div>
            """
            
            # Use st.components.v1.html() for reliable HTML rendering
            components.html(html_content, height=280)
            
            # Create tabs for different analysis aspects
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Analysis", "🔬 Methodology", "📚 Sources", "🔍 Traceability", "📊 Quality"])
            
            with tab1:
                # Core analysis content
                if detailed_analysis:
                    st.markdown("#### 📖 Detailed Analysis")
                    if detailed_analysis.strip().startswith('<') and detailed_analysis.strip().endswith('>'):
                        st.markdown(detailed_analysis, unsafe_allow_html=True)
                    else:
                        st.markdown(detailed_analysis.strip())
                
                # Supporting evidence
                if supporting_evidence:
                    st.markdown("#### 📋 Supporting Evidence")
                    st.markdown(f"> {supporting_evidence}")
                
                # Market context if available
                if market_context:
                    st.markdown("#### 🌍 Market Context")
                    market_size = market_context.get("market_size_analysis", "")
                    growth_trends = market_context.get("growth_trends", [])
                    regulatory_landscape = market_context.get("regulatory_landscape", "")
                    
                    if market_size:
                        st.markdown(f"**Market Size:** {market_size}")
                    
                    if growth_trends:
                        st.markdown("**Growth Trends:**")
                        for trend in growth_trends[:3]:
                            st.markdown(f"- {trend}")
                    
                    if regulatory_landscape:
                        st.markdown(f"**Regulatory Environment:** {regulatory_landscape}")
                
                # Competitive intelligence
                if competitive_intelligence:
                    st.markdown("#### 🎯 Competitive Intelligence")
                    competitor_positioning = competitive_intelligence.get("competitor_positioning", {})
                    market_gaps = competitive_intelligence.get("identified_gaps", [])
                    
                    if competitor_positioning:
                        for competitor, position in competitor_positioning.items():
                            st.markdown(f"**{competitor}:** {position}")
                    
                    if market_gaps:
                        st.markdown("**Identified Market Gaps:**")
                        for gap in market_gaps[:3]:
                            st.markdown(f"- {gap}")
            
            with tab2:
                # Methodology transparency
                st.markdown("#### 🔬 Analysis Methodology")
                
                if methodology_data and methodology_data.get("has_complete_trace"):
                    # Show comprehensive methodology from API
                    methodology = methodology_data.get("methodology", {})
                    execution_summary = methodology_data.get("execution_summary", {})
                    
                    st.markdown("**🎯 Methodology Overview:**")
                    st.info(f"""
                    **Analysis Type:** {methodology.get('analysis_type', 'Competitive Intelligence')}
                    **Search Strategy:** {methodology.get('search_strategy', 'Multi-source research')}
                    **Processing Method:** {methodology.get('processing_method', 'LangGraph pipeline')}
                    """)
                    
                    # Execution summary
                    st.markdown("**⚙️ Processing Summary:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Nodes Executed", execution_summary.get("total_nodes_executed", 0))
                    with col2:
                        st.metric("Processing Time", f"{execution_summary.get('total_processing_time', 0):.1f}s")
                    with col3:
                        st.metric("AI Interactions", execution_summary.get("ai_model_interactions", 0))
                    
                    # LangGraph execution trace
                    node_executions = methodology_data.get("node_executions", [])
                    if node_executions:
                        st.markdown("**📊 Processing Pipeline:**")
                        for node in node_executions[:5]:  # Show first 5 nodes
                            with st.expander(f"🔧 {node.get('node_name', 'Unknown Node')}"):
                                st.markdown(f"**Execution Order:** {node.get('execution_order', 0)}")
                                st.markdown(f"**Duration:** {node.get('processing_duration', 0):.2f}s")
                                st.markdown(f"**Input:** {node.get('input_data_summary', 'N/A')}")
                                st.markdown(f"**Output:** {node.get('output_data_summary', 'N/A')}")
                    
                    # Reasoning chains
                    reasoning_chains_data = methodology_data.get("reasoning_chains", [])
                    if reasoning_chains_data:
                        st.markdown("**🧠 Reasoning Chains:**")
                        for i, chain in enumerate(reasoning_chains_data[:3]):  # Show first 3
                            with st.expander(f"🔗 Reasoning Chain {i+1}"):
                                st.markdown(f"**Premise:** {chain.get('premise', 'N/A')}")
                                st.markdown(f"**Steps:** {' → '.join(chain.get('reasoning_steps', []))}")
                                st.markdown(f"**Conclusion:** {chain.get('conclusion', 'N/A')}")
                
                elif reasoning_chains:
                    # Fallback to opportunity data
                    st.markdown("**🧠 Reasoning Chains:**")
                    for i, chain in enumerate(reasoning_chains[:3]):
                        with st.expander(f"🔗 Reasoning Chain {i+1}"):
                            premise = chain.get("premise", "")
                            steps = chain.get("reasoning_steps", [])
                            conclusion = chain.get("conclusion", "")
                            
                            if premise:
                                st.markdown(f"**Premise:** {premise}")
                            if steps:
                                st.markdown(f"**Steps:** {' → '.join(steps)}")
                            if conclusion:
                                st.markdown(f"**Conclusion:** {conclusion}")
                
                # Decision audit trail
                if decision_audit_trail:
                    st.markdown("**📋 Decision Audit Trail:**")
                    for i, decision in enumerate(decision_audit_trail[:3]):
                        with st.expander(f"⚖️ Decision Point {i+1}"):
                            st.markdown(f"**Decision:** {decision.get('decision', 'N/A')}")
                            st.markdown(f"**Rationale:** {decision.get('rationale', 'N/A')}")
                            alternatives = decision.get("alternatives_considered", [])
                            if alternatives:
                                st.markdown(f"**Alternatives:** {', '.join(alternatives)}")
            
            with tab3:
                # Enhanced source analysis
                if sources_analysis and sources_analysis.get("includes_enhanced_analysis"):
                    st.markdown("#### 📚 Source Analysis Dashboard")
                    
                    # Quality overview
                    quality_indicators = sources_analysis.get("quality_indicators", {})
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_credibility = quality_indicators.get("average_credibility", 7.0)
                        st.metric("Average Credibility", f"{avg_credibility:.1f}/10")
                    
                    with col2:
                        avg_relevance = quality_indicators.get("average_relevance", 7.0)
                        st.metric("Average Relevance", f"{avg_relevance:.1f}/10")
                    
                    with col3:
                        total_sources = sources_analysis.get("enhanced_metadata_count", 0)
                        st.metric("Total Sources", total_sources)
                    
                    # Credibility breakdown
                    credibility_breakdown = sources_analysis.get("credibility_breakdown", {})
                    if credibility_breakdown:
                        st.markdown("**📊 Credibility Distribution:**")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("🟢 High Credibility", credibility_breakdown.get("high_credibility", 0))
                        with col2:
                            st.metric("🟡 Medium Credibility", credibility_breakdown.get("medium_credibility", 0))
                        with col3:
                            st.metric("🔴 Low Credibility", credibility_breakdown.get("low_credibility", 0))
                    
                    # Source diversity
                    source_diversity = sources_analysis.get("source_diversity", {})
                    if source_diversity:
                        st.markdown("**🌐 Source Diversity:**")
                        st.markdown(f"- **Unique Domains:** {source_diversity.get('unique_domains', 0)}")
                        st.markdown(f"- **Source Types:** {', '.join(source_diversity.get('source_types', []))}")
                        st.markdown(f"- **Search Queries:** {len(source_diversity.get('search_queries', []))} unique queries")
                    
                    # Quality summary
                    quality_summary = quality_indicators.get("quality_summary", "")
                    if quality_summary:
                        st.success(f"**Quality Assessment:** {quality_summary}")
                
                # Traditional source citations
                if source_urls:
                    st.markdown("#### 📎 Source Citations")
                    EnhancedSourceCitationSystem.render_source_list(
                        source_urls, 
                        f"sources_{index}",
                        sources_analysis
                    )
            
            with tab4:
                # Data flow traceability
                if traceability_data:
                    st.markdown("#### 🔍 Data Flow Traceability")
                    
                    # Traceability summary
                    summary = traceability_data.get("traceability_summary", {})
                    if summary:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Processing Stages", summary.get("total_stages", 0))
                        with col2:
                            st.metric("Source Coverage", summary.get("source_coverage", 0))
                        with col3:
                            st.metric("Traceability Score", f"{summary.get('traceability_score', 0):.1f}/10")
                    
                    # Data flow stages
                    data_flow_stages = traceability_data.get("data_flow_stages", [])
                    if data_flow_stages:
                        st.markdown("**📊 Processing Pipeline:**")
                        for stage in data_flow_stages:
                            with st.expander(f"🔧 {stage.get('stage', '').replace('_', ' ').title()}"):
                                st.markdown(f"**Description:** {stage.get('description', 'N/A')}")
                                st.markdown(f"**Data Count:** {stage.get('data_count', 0)}")
                                st.markdown(f"**Method:** {stage.get('processing_method', 'N/A')}")
                                
                                sample_data = stage.get("sample_data", [])
                                if sample_data:
                                    st.markdown("**Sample Data:**")
                                    for i, sample in enumerate(sample_data[:3]):
                                        if isinstance(sample, dict):
                                            st.json(sample)
                                        else:
                                            st.markdown(f"- {sample}")
                    
                    # Specific opportunity trace
                    specific_trace = traceability_data.get("specific_opportunity_trace")
                    if specific_trace:
                        st.markdown("**🎯 Opportunity-Specific Traceability:**")
                        st.markdown(f"**Opportunity:** {specific_trace.get('opportunity_title', '')}")
                        st.markdown(f"**Source Count:** {len(specific_trace.get('source_urls', []))}")
                        st.markdown(f"**Confidence:** {specific_trace.get('confidence_level', 0):.1f}/10")
                        
                        data_lineage = specific_trace.get("data_lineage", [])
                        if data_lineage:
                            st.markdown("**📈 Data Lineage:**")
                            for lineage in data_lineage[:3]:
                                with st.expander(f"🔗 {lineage.get('source_title', 'Source')[:50]}..."):
                                    st.markdown(f"**Query:** {lineage.get('search_query', 'N/A')}")
                                    st.markdown(f"**URL:** {lineage.get('source_url', 'N/A')}")
                                    st.markdown(f"**Content:** {lineage.get('content_snippet', 'N/A')}")
            
            with tab5:
                # Quality assurance report
                if quality_report:
                    st.markdown("#### 📊 Quality Assurance Report")
                    
                    # Overall quality
                    overall_score = quality_report.get("overall_quality_score", 7.0)
                    quality_grade = quality_report.get("quality_grade", "B")
                    
                    st.markdown(f"### Overall Quality: **{quality_grade}** ({overall_score:.1f}/10)")
                    
                    # Quality dimensions
                    quality_dimensions = quality_report.get("quality_dimensions", {})
                    if quality_dimensions:
                        st.markdown("**📊 Quality Dimensions:**")
                        
                        for dimension, details in quality_dimensions.items():
                            score = details.get("score", 5.0)
                            assessment = details.get("assessment", "Unknown")
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{dimension.replace('_', ' ').title()}:** {assessment}")
                            with col2:
                                st.metric("Score", f"{score:.1f}/10")
                    
                    # Confidence assessment
                    confidence_assessment = quality_report.get("confidence_assessment", {})
                    if confidence_assessment:
                        st.markdown("**🎯 Confidence Assessment:**")
                        avg_confidence = confidence_assessment.get("average_confidence", 7.0)
                        high_conf_count = confidence_assessment.get("high_confidence_opportunities", 0)
                        total_opps = confidence_assessment.get("total_opportunities", 1)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Average Confidence", f"{avg_confidence:.1f}/10")
                        with col2:
                            st.metric("High Confidence", high_conf_count)
                        with col3:
                            st.metric("Success Rate", f"{(high_conf_count/total_opps)*100:.0f}%")
                    
                    # Recommendations
                    recommendations = quality_report.get("recommendations", [])
                    if recommendations:
                        st.markdown("**💡 Quality Recommendations:**")
                        for rec in recommendations:
                            st.markdown(f"- {rec}")
                
                elif quality_assurance_report:
                    # Fallback to opportunity data
                    st.markdown("#### 📊 Quality Assurance Report")
                    validation_results = quality_assurance_report.get("validation_results", [])
                    confidence_assessment = quality_assurance_report.get("confidence_assessment", {})
                    
                    if validation_results:
                        st.markdown("**✅ Validation Results:**")
                        for result in validation_results:
                            status = "✅" if result.get("passed", True) else "❌"
                            st.markdown(f"{status} {result.get('check', 'Quality Check')}")
                    
                    if confidence_assessment:
                        st.markdown("**🎯 Confidence Metrics:**")
                        for metric, value in confidence_assessment.items():
                            st.markdown(f"- **{metric.replace('_', ' ').title()}:** {value}")

class EnhancedSourceCitationSystem:
    """
    Enhanced system for displaying source citations with real credibility data.
    Integrates with comprehensive source analysis from API endpoints.
    """
    
    @staticmethod
    def render_source_list(source_urls: List[str], unique_key: str = "sources", 
                          sources_analysis: Optional[Dict[str, Any]] = None):
        """
        Render enhanced source citations with real credibility data.
        
        Args:
            source_urls: List of source URLs
            unique_key: Unique key for Streamlit components
            sources_analysis: Enhanced source analysis data from API
        """
        if not source_urls:
            st.info("No sources available for this analysis.")
            return
        
        # Get enhanced metadata if available
        enhanced_metadata = []
        if sources_analysis and sources_analysis.get("includes_enhanced_analysis"):
            source_analysis = sources_analysis.get("source_analysis", {})
            enhanced_metadata = source_analysis.get("sources", [])
        
        for i, url in enumerate(source_urls):
            # Find matching enhanced metadata
            enhanced_source = None
            for metadata in enhanced_metadata:
                if metadata.get("url") == url:
                    enhanced_source = metadata
                    break
            
            EnhancedSourceCitationSystem.render_enhanced_source_citation(
                url, enhanced_source, f"{unique_key}_{i}"
            )
    
    @staticmethod
    def render_enhanced_source_citation(url: str, enhanced_data: Optional[Dict[str, Any]], unique_key: str):
        """
        Render individual source citation with enhanced credibility data.
        
        Args:
            url: Source URL
            enhanced_data: Enhanced source metadata from API
            unique_key: Unique key for Streamlit components
        """
        if enhanced_data:
            # Use real credibility data
            credibility_score = enhanced_data.get("credibility_score", 7.0)
            relevance_score = enhanced_data.get("relevance_score", 7.0)
            source_type = enhanced_data.get("source_type", "Unknown")
            domain = enhanced_data.get("domain", SourceCitationSystem.extract_domain(url))
            
            # Real credibility assessment
            if credibility_score >= 8.0:
                credibility = "high"
                credibility_icon = "🟢"
            elif credibility_score >= 6.0:
                credibility = "medium"
                credibility_icon = "🟡"
            else:
                credibility = "low"
                credibility_icon = "🔴"
            
            credibility_text = f"Credibility: {credibility_score:.1f}/10 ({credibility.title()})"
            relevance_text = f"Relevance: {relevance_score:.1f}/10"
            
        else:
            # Fallback to basic assessment
            domain = SourceCitationSystem.extract_domain(url)
            credibility = SourceCitationSystem.assess_credibility(domain)
            source_type = "Unknown"
            
            credibility_icon = {
                "high": "🟢",
                "medium": "🟡", 
                "low": "🔴",
                "unknown": "⚪"
            }.get(credibility, "⚪")
            
            credibility_text = f"Credibility: {credibility.title()}"
            relevance_text = "Relevance: Not assessed"
        
        # Render enhanced citation
        col1, col2 = st.columns([0.1, 0.9])
        
        with col1:
            st.markdown(f"<div style='font-size: 1.5rem; text-align: center;'>{credibility_icon}</div>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong>{domain}</strong>
                    <span style="font-size: 0.8rem; color: #666;">{source_type}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.8rem; color: #666;">{credibility_text}</span>
                    <span style="font-size: 0.8rem; color: #666;">{relevance_text}</span>
                </div>
                <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none;">
                    📎 View Source
                </a>
            </div>
            """, unsafe_allow_html=True)

class ProgressiveDisclosureManager:
    """
    Manager class for coordinating progressive disclosure state across components.
    Handles expand/collapse state management and smooth transitions.
    Enhanced with analysis_id integration.
    """
    
    def __init__(self, analysis_id: Optional[str] = None):
        """
        Initialize the progressive disclosure manager.
        
        Args:
            analysis_id: Optional analysis ID for enhanced data integration
        """
        self.analysis_id = analysis_id
        if 'disclosure_state' not in st.session_state:
            st.session_state.disclosure_state = {}
    
    def get_state(self, opportunity_id: str) -> str:
        """
        Get current disclosure state for an opportunity.
        
        Args:
            opportunity_id: Unique identifier for the opportunity
            
        Returns:
            str: Current state ('summary', 'details', 'analysis')
        """
        return st.session_state.disclosure_state.get(opportunity_id, 'summary')
    
    def set_state(self, opportunity_id: str, state: str):
        """
        Set disclosure state for an opportunity.
        
        Args:
            opportunity_id: Unique identifier for the opportunity
            state: New state ('summary', 'details', 'analysis')
        """
        st.session_state.disclosure_state[opportunity_id] = state
    
    def render_opportunity_with_disclosure(self, opportunity: Dict[str, Any], index: int = 0):
        """
        Render opportunity with progressive disclosure functionality and enhanced data integration.
        
        Args:
            opportunity: Opportunity data dictionary
            index: Opportunity index for unique identification
        """
        opportunity_id = f"opp_{index}_{hash(opportunity.get('title', ''))}"
        current_state = self.get_state(opportunity_id)
        
        # Always show summary card
        if current_state == 'summary':
            if OpportunityCard.render(opportunity, index, show_expand_button=True, analysis_id=self.analysis_id):
                self.set_state(opportunity_id, 'details')
                st.rerun()
        
        # Show details if expanded
        elif current_state == 'details':
            # Show summary (collapsed state)
            OpportunityCard.render(opportunity, index, show_expand_button=False, analysis_id=self.analysis_id)
            
            # Show details
            if OpportunityDetails.render(opportunity, index, show_full_analysis_button=True, analysis_id=self.analysis_id):
                self.set_state(opportunity_id, 'analysis')
                st.rerun()
            
            # Collapse button
            if st.button("🔼 Collapse", key=f"collapse_details_{opportunity_id}"):
                self.set_state(opportunity_id, 'summary')
                st.rerun()
        
        # Show full analysis
        elif current_state == 'analysis':
            # Show summary (collapsed state)
            OpportunityCard.render(opportunity, index, show_expand_button=False, analysis_id=self.analysis_id)
            
            # Show details (collapsed state)
            st.markdown("*📋 Details available - click to expand*")
            
            # Show full analysis
            AnalysisBreakdown.render(opportunity, index, analysis_id=self.analysis_id)
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔼 Back to Details", key=f"back_to_details_{opportunity_id}"):
                    self.set_state(opportunity_id, 'details')
                    st.rerun()
            with col2:
                if st.button("🔼 Collapse All", key=f"collapse_all_{opportunity_id}"):
                    self.set_state(opportunity_id, 'summary')
                    st.rerun()

# Utility functions for integration with existing codebase

def render_opportunities_simple(opportunities: List[Dict[str, Any]], title: str = "Strategic Opportunities"):
    """
    Render a list of opportunities with simple card display (no state management).
    Use this for debugging HTML rendering issues.
    
    Args:
        opportunities: List of opportunity dictionaries
        title: Section title
    """
    if not opportunities:
        st.info("No opportunities available.")
        return
    
    st.markdown(f"## {title}")
    
    # Render each opportunity as a simple card
    for i, opportunity in enumerate(opportunities):
        st.markdown(f"### Opportunity {i+1}")
        
        # Try direct HTML rendering first
        title_text = opportunity.get("title", f"Strategic Opportunity {i + 1}")
        score = opportunity.get("opportunity_score", 8.0)
        category = opportunity.get("category", "Strategic")
        
        # Simple HTML test
        simple_card_html = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    margin: 1rem 0;">
            <h3 style="margin: 0 0 1rem 0;">#{i + 1} {title_text}</h3>
            <p style="margin: 0.5rem 0;"><strong>Category:</strong> {category}</p>
            <p style="margin: 0.5rem 0;"><strong>Score:</strong> {score}/10</p>
        </div>
        """
        
        st.markdown("**Direct HTML rendering:**")
        st.markdown(simple_card_html, unsafe_allow_html=True)
        
        st.markdown("**Component rendering:**")
        # Try component rendering
        try:
            OpportunityCard.render(opportunity, i, show_expand_button=False)
        except Exception as e:
            st.error(f"Component rendering error: {e}")
        
        # Add separator
        if i < len(opportunities) - 1:
            st.markdown("---")

def render_opportunities_with_progressive_disclosure(
    opportunities: List[Dict[str, Any]], 
    title: str = "Strategic Opportunities",
    analysis_id: Optional[str] = None
):
    """
    Render a list of opportunities with enhanced progressive disclosure functionality.
    
    Args:
        opportunities: List of opportunity dictionaries
        title: Section title
        analysis_id: Optional analysis ID for enhanced data integration (None = demo mode)
    """
    if not opportunities:
        st.info("No opportunities available.")
        return
    
    st.markdown(f"## {title}")
    
    # Show mode-specific status
    if analysis_id:
        st.info(f"🔍 **Live Analysis Mode**: Real-time data from analysis `{analysis_id}`")
        
        # Quick quality overview if API is available
        quality_report = APIIntegration.get_quality_report(analysis_id)
        if quality_report:
            col1, col2, col3 = st.columns(3)
            with col1:
                overall_score = quality_report.get("overall_quality_score", 7.0)
                st.metric("Overall Quality", f"{overall_score:.1f}/10")
            with col2:
                quality_grade = quality_report.get("quality_grade", "B")
                st.metric("Quality Grade", quality_grade)
            with col3:
                recommendations = quality_report.get("recommendations", [])
                st.metric("Recommendations", len(recommendations))
    else:
        st.info("🎮 **Demo Mode**: Showcasing progressive disclosure with sample data")
    
    # Initialize enhanced disclosure manager
    manager = ProgressiveDisclosureManager(analysis_id=analysis_id)
    
    # Render each opportunity
    for i, opportunity in enumerate(opportunities):
        manager.render_opportunity_with_disclosure(opportunity, i)
        
        # Add separator between opportunities
        if i < len(opportunities) - 1:
            st.markdown("---")

def create_opportunity_summary_grid(opportunities: List[Dict[str, Any]], columns: int = 2, analysis_id: Optional[str] = None):
    """
    Create a grid layout of opportunity summary cards with enhanced data integration.
    
    Args:
        opportunities: List of opportunity dictionaries
        columns: Number of columns in the grid
        analysis_id: Optional analysis ID for enhanced data integration
    """
    if not opportunities:
        st.info("No opportunities available.")
        return
    
    # Create columns
    cols = st.columns(columns)
    
    for i, opportunity in enumerate(opportunities):
        with cols[i % columns]:
            OpportunityCard.render(opportunity, i, show_expand_button=True, analysis_id=analysis_id)

def create_methodology_transparency_dashboard(analysis_id: str):
    """
    Create a dedicated dashboard for methodology transparency and data flow visualization.
    
    Args:
        analysis_id: Analysis ID for fetching transparency data
    """
    st.markdown("## 🔬 Methodology Transparency Dashboard")
    
    # Get comprehensive data
    methodology_data = APIIntegration.get_methodology(analysis_id)
    traceability_data = APIIntegration.get_traceability(analysis_id)
    quality_report = APIIntegration.get_quality_report(analysis_id)
    sources_analysis = APIIntegration.get_sources_analysis(analysis_id, include_enhanced=True)
    
    if not any([methodology_data, traceability_data, quality_report, sources_analysis]):
        st.error("Unable to fetch methodology data. Please check API connection.")
        return
    
    # Create tabs for different transparency aspects
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Overview", "🔍 Data Flow", "📊 Quality", "📚 Sources"])
    
    with tab1:
        if methodology_data and methodology_data.get("has_complete_trace"):
            execution_summary = methodology_data.get("execution_summary", {})
            
            st.markdown("### 📊 Processing Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Nodes Executed", execution_summary.get("total_nodes_executed", 0))
            with col2:
                st.metric("Processing Time", f"{execution_summary.get('total_processing_time', 0):.1f}s")
            with col3:
                st.metric("AI Interactions", execution_summary.get("ai_model_interactions", 0))
            with col4:
                st.metric("Overall Confidence", f"{execution_summary.get('overall_confidence', 7.0):.1f}/10")
            
            # Methodology overview
            methodology = methodology_data.get("methodology", {})
            if methodology:
                st.markdown("### 🎯 Methodology Summary")
                st.info(f"""
                **Analysis Type:** {methodology.get('analysis_type', 'Competitive Intelligence')}
                **Search Strategy:** {methodology.get('search_strategy', 'Multi-source research')}
                **Processing Method:** {methodology.get('processing_method', 'LangGraph pipeline')}
                """)
    
    with tab2:
        if traceability_data:
            st.markdown("### 🔍 Complete Data Flow")
            
            # Traceability summary
            summary = traceability_data.get("traceability_summary", {})
            if summary:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Processing Stages", summary.get("total_stages", 0))
                with col2:
                    st.metric("Source Coverage", summary.get("source_coverage", 0))
                with col3:
                    st.metric("Traceability Score", f"{summary.get('traceability_score', 0):.1f}/10")
            
            # Data flow visualization
            data_flow_stages = traceability_data.get("data_flow_stages", [])
            if data_flow_stages:
                st.markdown("### 📊 Processing Pipeline")
                for stage in data_flow_stages:
                    with st.expander(f"🔧 {stage.get('stage', '').replace('_', ' ').title()}"):
                        st.markdown(f"**Description:** {stage.get('description', 'N/A')}")
                        st.markdown(f"**Data Count:** {stage.get('data_count', 0)}")
                        st.markdown(f"**Method:** {stage.get('processing_method', 'N/A')}")
    
    with tab3:
        if quality_report:
            st.markdown("### 📊 Quality Assessment")
            
            overall_score = quality_report.get("overall_quality_score", 7.0)
            quality_grade = quality_report.get("quality_grade", "B")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Overall Quality Score", f"{overall_score:.1f}/10")
            with col2:
                st.metric("Quality Grade", quality_grade)
            
            # Quality dimensions
            quality_dimensions = quality_report.get("quality_dimensions", {})
            if quality_dimensions:
                st.markdown("### 📊 Quality Dimensions")
                for dimension, details in quality_dimensions.items():
                    score = details.get("score", 5.0)
                    assessment = details.get("assessment", "Unknown")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{dimension.replace('_', ' ').title()}:** {assessment}")
                    with col2:
                        st.metric("Score", f"{score:.1f}/10")
    
    with tab4:
        if sources_analysis and sources_analysis.get("includes_enhanced_analysis"):
            st.markdown("### 📚 Source Analysis")
            
            # Quality overview
            quality_indicators = sources_analysis.get("quality_indicators", {})
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_credibility = quality_indicators.get("average_credibility", 7.0)
                st.metric("Average Credibility", f"{avg_credibility:.1f}/10")
            
            with col2:
                avg_relevance = quality_indicators.get("average_relevance", 7.0)
                st.metric("Average Relevance", f"{avg_relevance:.1f}/10")
            
            with col3:
                total_sources = sources_analysis.get("enhanced_metadata_count", 0)
                st.metric("Total Sources", total_sources)
            
            # Credibility breakdown
            credibility_breakdown = sources_analysis.get("credibility_breakdown", {})
            if credibility_breakdown:
                st.markdown("### 📊 Credibility Distribution")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🟢 High Credibility", credibility_breakdown.get("high_credibility", 0))
                with col2:
                    st.metric("🟡 Medium Credibility", credibility_breakdown.get("medium_credibility", 0))
                with col3:
                    st.metric("🔴 Low Credibility", credibility_breakdown.get("low_credibility", 0))

# Legacy Source Citation System Utilities (for backward compatibility)
class SourceCitationSystem:
    """
    Legacy source citation utilities for backward compatibility.
    These methods are used by EnhancedSourceCitationSystem as fallbacks.
    """
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract clean domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain if domain else url
        except:
            return url
    
    @staticmethod
    def assess_credibility(domain: str) -> str:
        """Assess basic credibility level based on domain."""
        domain_lower = domain.lower()
        
        # High credibility domains
        high_credibility = {
            'pubmed.ncbi.nlm.nih.gov', 'ncbi.nlm.nih.gov', 'fda.gov', 'who.int',
            'reuters.com', 'bloomberg.com', 'wsj.com', 'ft.com',
            'nature.com', 'science.org', 'nejm.org', 'thelancet.com'
        }
        
        # Medium credibility domains
        medium_credibility = {
            'forbes.com', 'cnn.com', 'bbc.com', 'medscape.com',
            'massdevice.com', 'medtechdive.com', 'devicetalks.com'
        }
        
        # Low credibility indicators
        low_credibility_indicators = ['blog', 'wordpress', 'medium.com', 'linkedin.com']
        
        if domain_lower in high_credibility or any(indicator in domain_lower for indicator in ['.gov', '.edu']):
            return "high"
        elif domain_lower in medium_credibility:
            return "medium"
        elif any(indicator in domain_lower for indicator in low_credibility_indicators):
            return "low"
        else:
            return "unknown"
    
    @staticmethod
    def render_source_citation(url: str, unique_key: str):
        """Render basic source citation (legacy method)."""
        domain = SourceCitationSystem.extract_domain(url)
        credibility = SourceCitationSystem.assess_credibility(domain)
        
        credibility_icon = {
            "high": "🟢",
            "medium": "🟡", 
            "low": "🔴",
            "unknown": "⚪"
        }.get(credibility, "⚪")
        
        col1, col2 = st.columns([0.1, 0.9])
        
        with col1:
            st.markdown(f"<div style='font-size: 1.5rem; text-align: center;'>{credibility_icon}</div>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong>{domain}</strong>
                    <span style="font-size: 0.8rem; color: #666;">Credibility: {credibility.title()}</span>
                </div>
                <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none;">
                    📎 View Source
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def render_source_list(source_urls: List[str], unique_key: str = "sources"):
        """Render list of sources using basic citations."""
        if not source_urls:
            st.info("No sources available for this analysis.")
            return
        
        for i, url in enumerate(source_urls):
            SourceCitationSystem.render_source_citation(url, f"{unique_key}_{i}") 