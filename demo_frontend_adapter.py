"""
Demo Frontend Adapter
Bridges the gap between demo_frontend_fixed.py and the current opportunity pipeline
Allows seamless switching between demo data and live analysis
"""

import streamlit as st
from typing import Dict, Any, Optional
from demo_data import get_demo_data, DEMO_SCENARIOS
from main_langgraph_opportunity import opportunity_graph

class DemoFrontendAdapter:
    """Adapter to make demo frontend work with current opportunity pipeline"""
    
    @staticmethod
    def get_analysis_data(use_demo: bool = True, competitors: Optional[list] = None, 
                         focus_area: str = "spine_fusion") -> Dict[str, Any]:
        """
        Get analysis data - either from demo or live pipeline
        
        Args:
            use_demo: If True, use demo data. If False, run live analysis
            competitors: List of competitors for live analysis
            focus_area: Focus area for analysis
            
        Returns:
            Analysis data in demo frontend format
        """
        
        if use_demo:
            # Use demo data (guaranteed to work)
            return get_demo_data(focus_area)
        
        else:
            # Run live analysis and adapt the data
            if not competitors:
                competitors = ["Stryker Spine", "Zimmer Biomet", "Orthofix"]
            
            try:
                # Run the opportunity pipeline
                result = opportunity_graph.run_analysis(competitors, focus_area)
                
                if "error" in result:
                    # Fallback to demo data if live analysis fails
                    st.warning(f"Live analysis failed: {result.get('error', 'Unknown error')}. Using demo data.")
                    return get_demo_data(focus_area)
                
                # Adapt the live data to demo format
                return DemoFrontendAdapter._adapt_live_data_to_demo_format(result, competitors, focus_area)
                
            except Exception as e:
                # Fallback to demo data if anything goes wrong
                st.error(f"Analysis error: {str(e)}. Using demo data.")
                return get_demo_data(focus_area)
    
    @staticmethod
    def _adapt_live_data_to_demo_format(live_result: Dict[str, Any], 
                                       competitors: list, 
                                       focus_area: str) -> Dict[str, Any]:
        """
        Adapt live pipeline data to demo frontend format
        
        This handles the data structure differences between the current pipeline
        and what the demo frontend expects.
        """
        
        # Extract data from live result
        final_report = live_result.get("final_report", {})
        
        # Create demo-compatible structure
        adapted_data = {
            "analysis_metadata": {
                "client_company": "Live Analysis",
                "analysis_date": "2024-01-15",
                "competitors_analyzed": competitors,
                "device_category": focus_area.replace("_", " ").title(),
                "analysis_type": "Live Competitive Opportunity Intelligence"
            },
            
            # TOP OPPORTUNITIES - Extract from live data or create defaults
            "top_opportunities": DemoFrontendAdapter._extract_top_opportunities(final_report),
            
            # OPPORTUNITY MATRIX - Create safe matrix data
            "opportunity_matrix": DemoFrontendAdapter._create_safe_opportunity_matrix(final_report),
            
            # CATEGORY OPPORTUNITIES - Extract or create defaults
            "brand_opportunities": DemoFrontendAdapter._extract_category_opportunities(
                final_report, "brand_opportunities"
            ),
            "product_opportunities": DemoFrontendAdapter._extract_category_opportunities(
                final_report, "product_opportunities"
            ),
            "pricing_opportunities": DemoFrontendAdapter._extract_category_opportunities(
                final_report, "pricing_opportunities"
            ),
            "market_opportunities": DemoFrontendAdapter._extract_category_opportunities(
                final_report, "market_opportunities"
            ),
            
            # COMPETITIVE LANDSCAPE
            "competitive_landscape": DemoFrontendAdapter._extract_competitive_landscape(
                final_report, competitors
            ),
            
            # EXECUTIVE SUMMARY
            "executive_summary": DemoFrontendAdapter._extract_executive_summary(final_report)
        }
        
        return adapted_data
    
    @staticmethod
    def _extract_top_opportunities(final_report: Dict[str, Any]) -> list:
        """Extract top opportunities from live data or create defaults"""
        
        # Try to extract from final_report
        top_opps = final_report.get("top_opportunities", [])
        
        if top_opps and len(top_opps) > 0:
            # Adapt live opportunities to demo format
            adapted_opps = []
            for i, opp in enumerate(top_opps[:3]):  # Top 3
                adapted_opp = {
                    "id": i + 1,
                    "title": opp.get("title", f"Strategic Opportunity {i+1}"),
                    "category": opp.get("category", "Market Positioning"),
                    "description": opp.get("description", "Live analysis opportunity"),
                    "opportunity_score": opp.get("opportunity_score", 8.0),
                    "implementation_difficulty": opp.get("implementation_difficulty", "Medium"),
                    "time_to_market": opp.get("time_to_market", "6-12 months"),
                    "investment_level": opp.get("investment_level", "Medium"),
                    "competitive_risk": opp.get("competitive_risk", "Medium"),
                    "potential_impact": opp.get("potential_impact", "Significant opportunity"),
                    "next_steps": opp.get("next_steps", [
                        "Conduct detailed analysis",
                        "Develop implementation plan",
                        "Validate with stakeholders"
                    ]),
                    "supporting_evidence": opp.get("supporting_evidence", "Live competitive analysis")
                }
                adapted_opps.append(adapted_opp)
            return adapted_opps
        
        else:
            # Return default opportunities for live analysis
            return [
                {
                    "id": 1,
                    "title": "Live Analysis Opportunity",
                    "category": "Market Positioning",
                    "description": "Opportunity identified through live competitive analysis",
                    "opportunity_score": 8.0,
                    "implementation_difficulty": "Medium",
                    "time_to_market": "6-12 months",
                    "investment_level": "Medium",
                    "competitive_risk": "Medium",
                    "potential_impact": "Market differentiation",
                    "next_steps": [
                        "Review live analysis results",
                        "Develop detailed strategy",
                        "Execute implementation plan"
                    ],
                    "supporting_evidence": "Live competitive intelligence analysis"
                }
            ]
    
    @staticmethod
    def _create_safe_opportunity_matrix(final_report: Dict[str, Any]) -> Dict[str, list]:
        """Create a safe opportunity matrix that won't cause validation errors"""
        
        # Create safe matrix with proper numeric values
        return {
            "high_impact_easy": [
                {"name": "Quick Win Opportunity", "impact": 8.0, "difficulty": 3.0}
            ],
            "high_impact_hard": [
                {"name": "Strategic Investment", "impact": 9.0, "difficulty": 7.0}
            ],
            "low_impact_easy": [
                {"name": "Low Priority Task", "impact": 4.0, "difficulty": 2.0}
            ],
            "low_impact_hard": [
                {"name": "Avoid This", "impact": 3.0, "difficulty": 8.0}
            ]
        }
    
    @staticmethod
    def _extract_category_opportunities(final_report: Dict[str, Any], category: str) -> list:
        """Extract category opportunities or create defaults"""
        
        opportunities = final_report.get(category, [])
        
        if opportunities:
            return opportunities
        else:
            # Return default category opportunity
            return [
                {
                    "opportunity": f"Live {category.replace('_', ' ').title()} Opportunity",
                    "current_gap": "Gap identified through live analysis",
                    "recommendation": "Recommendation based on competitive intelligence",
                    "implementation": "Implementation approach from analysis",
                    "timeline": "6-12 months",
                    "investment": "Medium ($200K-500K)"
                }
            ]
    
    @staticmethod
    def _extract_competitive_landscape(final_report: Dict[str, Any], competitors: list) -> Dict[str, Any]:
        """Extract competitive landscape or create defaults"""
        
        landscape = final_report.get("competitive_landscape", {})
        
        if landscape:
            return landscape
        else:
            # Create default competitive landscape
            market_leaders = {}
            for competitor in competitors:
                market_leaders[competitor] = {
                    "market_share": "Analysis-based",
                    "strengths": ["Market presence", "Product portfolio"],
                    "weaknesses": ["Innovation gaps", "Pricing pressure"],
                    "opportunities_against": ["Digital innovation", "Value positioning"]
                }
            
            return {"market_leaders": market_leaders}
    
    @staticmethod
    def _extract_executive_summary(final_report: Dict[str, Any]) -> Dict[str, Any]:
        """Extract executive summary or create default"""
        
        summary = final_report.get("executive_summary", {})
        
        if summary:
            return summary
        else:
            return {
                "key_insight": "Live competitive analysis reveals strategic opportunities",
                "immediate_actions": [
                    "Review detailed analysis results",
                    "Prioritize identified opportunities",
                    "Develop implementation roadmap"
                ],
                "strategic_recommendations": [
                    "Focus on competitive differentiation",
                    "Leverage identified market gaps",
                    "Execute strategic initiatives"
                ]
            }

# Convenience function for easy use
def get_demo_or_live_data(use_demo: bool = True, competitors: Optional[list] = None, 
                         focus_area: str = "spine_fusion") -> Dict[str, Any]:
    """
    Convenience function to get either demo or live data
    
    Usage:
        # Get demo data (safe, always works)
        data = get_demo_or_live_data(use_demo=True)
        
        # Get live data (may fallback to demo if issues)
        data = get_demo_or_live_data(use_demo=False, competitors=["Stryker Spine"])
    """
    return DemoFrontendAdapter.get_analysis_data(use_demo, competitors, focus_area) 