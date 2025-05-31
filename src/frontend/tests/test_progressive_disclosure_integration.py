"""
Integration Tests for Progressive Disclosure Components
Tests the integration of progressive disclosure components with the main Streamlit application
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.frontend.streamlit_app_opportunity import (
    enhance_opportunities_with_credibility,
    display_opportunity_results_with_progressive_disclosure
)
from src.frontend.components.progressive_disclosure import (
    render_opportunities_with_progressive_disclosure,
    OpportunityCard,
    ProgressiveDisclosureManager
)

class TestProgressiveDisclosureIntegration:
    """Test the integration of progressive disclosure components with the main app"""
    
    def setup_method(self):
        """Set up test data for each test"""
        self.sample_opportunities = [
            {
                "title": "Digital Integration Platform",
                "description": "Develop IoT-enabled spine fusion devices",
                "opportunity_score": 9.2,
                "potential_impact": "$25M-40M revenue potential",
                "time_to_market": "12-18 months",
                "investment_level": "High",
                "source_urls": [
                    "https://pubmed.ncbi.nlm.nih.gov/example1",
                    "https://medtechdive.com/example2",
                    "https://massdevice.com/example3"
                ],
                "supporting_evidence": "Market research shows strong demand",
                "next_steps": ["Conduct interviews", "Develop MVP"]
            },
            {
                "title": "Value-Based Pricing Model",
                "description": "Implement outcome-based pricing",
                "opportunity_score": 8.7,
                "potential_impact": "$15M-25M revenue potential",
                "time_to_market": "6-9 months",
                "investment_level": "Medium",
                "source_urls": ["https://healthcaredive.com/example1"],
                "supporting_evidence": "Healthcare systems demand value-based contracts"
            },
            {
                "title": "ASC Market Expansion",
                "description": "Target ambulatory surgery centers",
                "opportunity_score": 8.1,
                "potential_impact": "$10M-20M revenue potential",
                "time_to_market": "6-12 months",
                "investment_level": "Medium",
                "source_urls": []  # No sources to test low credibility
            }
        ]
        
        self.sample_result = {
            "top_opportunities": self.sample_opportunities,
            "executive_summary": {
                "revenue_potential": "$50M-85M",
                "market_share_opportunity": "10-15%",
                "key_insight": "Digital transformation presents the largest opportunity"
            },
            "final_report": {
                "brand_opportunities": [],
                "product_opportunities": [],
                "pricing_opportunities": [],
                "market_opportunities": []
            },
            "competitive_profiles": {
                "Stryker Spine": {
                    "market_share": "25%",
                    "strengths": ["Strong R&D", "Market leader"],
                    "opportunities_against": ["Digital integration gap"]
                }
            },
            "confidence_score": 8.5
        }

    def test_enhance_opportunities_with_credibility(self):
        """Test that opportunities are properly enhanced with credibility indicators"""
        enhanced = enhance_opportunities_with_credibility(self.sample_opportunities)
        
        # Should have same number of opportunities
        assert len(enhanced) == len(self.sample_opportunities)
        
        # First opportunity should have high credibility (3+ sources)
        assert enhanced[0]["credibility_indicator"] == "🟢"
        assert enhanced[0]["source_count_display"] == "3 sources"
        assert enhanced[0]["has_detailed_analysis"] == True
        assert enhanced[0]["has_source_analysis"] == True
        
        # Second opportunity should have medium credibility (1 source)
        assert enhanced[1]["credibility_indicator"] == "🟡"
        assert enhanced[1]["source_count_display"] == "1 source"
        
        # Third opportunity should have low credibility (no sources)
        assert enhanced[2]["credibility_indicator"] == "🔴"
        assert enhanced[2]["source_count_display"] == "Limited sources"
        assert enhanced[2]["has_source_analysis"] == False
        
        # All should have confidence levels
        for opp in enhanced:
            assert "confidence_level" in opp
            assert "detailed_analysis" in opp

    def test_enhance_opportunities_handles_missing_fields(self):
        """Test that enhancement works with opportunities missing optional fields"""
        minimal_opportunity = {
            "title": "Minimal Opportunity",
            "description": "Basic description"
        }
        
        enhanced = enhance_opportunities_with_credibility([minimal_opportunity])
        
        assert len(enhanced) == 1
        assert enhanced[0]["credibility_indicator"] == "🔴"
        assert enhanced[0]["source_count_display"] == "Limited sources"
        assert enhanced[0]["confidence_level"] == 8.0  # Default value
        assert "detailed_analysis" in enhanced[0]

    @patch('streamlit.markdown')
    @patch('streamlit.warning')
    def test_display_opportunity_results_with_progressive_disclosure(self, mock_warning, mock_markdown):
        """Test the main display function with progressive disclosure"""
        competitors = ["Stryker Spine", "Medtronic Spine"]
        focus_area = "spine_fusion"
        client_name = "Test Client"
        
        # Mock the render function to avoid Streamlit context issues
        with patch('src.frontend.streamlit_app_opportunity.render_opportunities_with_progressive_disclosure') as mock_render:
            display_opportunity_results_with_progressive_disclosure(
                self.sample_result, competitors, focus_area, client_name
            )
            
            # Should call the progressive disclosure render function
            mock_render.assert_called_once()
            
            # Should not show warning for empty opportunities
            mock_warning.assert_not_called()

    @patch('streamlit.markdown')
    @patch('streamlit.warning')
    def test_display_with_empty_opportunities(self, mock_warning, mock_markdown):
        """Test display function handles empty opportunities gracefully"""
        empty_result = {
            "top_opportunities": [],
            "executive_summary": {},
            "final_report": {},
            "competitive_profiles": {},
            "confidence_score": 0
        }
        
        display_opportunity_results_with_progressive_disclosure(
            empty_result, ["Competitor"], "spine_fusion", "Test Client"
        )
        
        # Should show warning for no opportunities
        mock_warning.assert_called_once_with("No strategic opportunities were identified in this analysis.")

    def test_credibility_scoring_logic(self):
        """Test the credibility scoring logic in detail"""
        test_cases = [
            # (source_count, expected_indicator, expected_display)
            (0, "🔴", "Limited sources"),
            (1, "🟡", "1 source"),
            (2, "🟡", "2 sources"),
            (3, "🟢", "3 sources"),
            (5, "🟢", "5 sources")
        ]
        
        for source_count, expected_indicator, expected_display in test_cases:
            opportunity = {
                "title": f"Test Opportunity {source_count}",
                "source_urls": ["url"] * source_count
            }
            
            enhanced = enhance_opportunities_with_credibility([opportunity])
            
            assert enhanced[0]["credibility_indicator"] == expected_indicator
            assert enhanced[0]["source_count_display"] == expected_display

    def test_detailed_analysis_generation(self):
        """Test that detailed analysis is properly generated for opportunities"""
        opportunity = {
            "title": "Test Opportunity",
            "supporting_evidence": "Strong market evidence",
            "implementation_difficulty": "High",
            "competitive_risk": "Low",
            "investment_level": "Medium"
        }
        
        enhanced = enhance_opportunities_with_credibility([opportunity])
        detailed_analysis = enhanced[0]["detailed_analysis"]
        
        # Should contain key sections
        assert "## Methodology" in detailed_analysis
        assert "## Analysis Details" in detailed_analysis
        assert "## Implementation Considerations" in detailed_analysis
        assert "## Success Factors" in detailed_analysis
        
        # Should include the provided evidence
        assert "Strong market evidence" in detailed_analysis
        
        # Should include the risk and difficulty information
        assert "High" in detailed_analysis  # implementation_difficulty
        assert "Low" in detailed_analysis   # competitive_risk
        assert "Medium" in detailed_analysis  # investment_level

    @patch('src.frontend.components.progressive_disclosure.st')
    def test_progressive_disclosure_components_integration(self, mock_st):
        """Test that progressive disclosure components integrate properly"""
        # Mock Streamlit session state properly
        mock_session_state = {}
        mock_st.session_state = mock_session_state
        
        # Mock other Streamlit functions that might be called
        mock_st.markdown = Mock()
        mock_st.columns = Mock(return_value=[Mock(), Mock()])
        mock_st.button = Mock(return_value=False)
        mock_st.expander = Mock()
        
        enhanced_opportunities = enhance_opportunities_with_credibility(self.sample_opportunities)
        
        # Test that we can call the render function without errors
        try:
            render_opportunities_with_progressive_disclosure(
                enhanced_opportunities,
                title="Test Opportunities"
            )
            integration_success = True
        except Exception as e:
            integration_success = False
            print(f"Integration failed: {e}")
        
        assert integration_success, "Progressive disclosure components should integrate without errors"

    def test_opportunity_card_rendering_with_enhanced_data(self):
        """Test that OpportunityCard can render enhanced opportunity data"""
        enhanced_opportunities = enhance_opportunities_with_credibility(self.sample_opportunities)
        
        # Test with the first enhanced opportunity
        enhanced_opp = enhanced_opportunities[0]
        
        # Should have all required fields for OpportunityCard
        required_fields = [
            "title", "opportunity_score", "credibility_indicator", 
            "source_count_display", "time_to_market", "investment_level"
        ]
        
        for field in required_fields:
            assert field in enhanced_opp, f"Enhanced opportunity missing required field: {field}"

    def test_progressive_disclosure_manager_integration(self):
        """Test that ProgressiveDisclosureManager works with enhanced opportunities"""
        enhanced_opportunities = enhance_opportunities_with_credibility(self.sample_opportunities)
        
        # Test manager initialization
        manager = ProgressiveDisclosureManager()
        
        # Should be able to handle enhanced opportunities
        for i, opp in enumerate(enhanced_opportunities):
            opportunity_id = f"opp_{i}"
            
            # Should have proper disclosure flags
            assert "has_detailed_analysis" in opp
            assert "has_source_analysis" in opp
            
            # Manager should handle state for each opportunity
            # Note: ProgressiveDisclosureManager uses Streamlit session state internally
            # so we test the basic functionality without session state dependency
            assert hasattr(manager, 'set_disclosure_level')
            assert hasattr(manager, 'toggle_disclosure_level')

class TestProgressiveDisclosureValueProposition:
    """Test that the progressive disclosure implementation delivers on the value proposition"""
    
    def test_credibility_system_implementation(self):
        """Test that the credibility system is properly implemented as a selling point"""
        # High credibility sources (should get green indicator)
        high_credibility_opp = {
            "title": "High Credibility Opportunity",
            "source_urls": [
                "https://pubmed.ncbi.nlm.nih.gov/article1",
                "https://fda.gov/report2",
                "https://reuters.com/news3"
            ]
        }
        
        # Medium credibility sources (should get yellow indicator)
        medium_credibility_opp = {
            "title": "Medium Credibility Opportunity",
            "source_urls": [
                "https://forbes.com/article1",
                "https://medscape.com/report2"
            ]
        }
        
        # Low credibility sources (should get red indicator)
        low_credibility_opp = {
            "title": "Low Credibility Opportunity",
            "source_urls": []
        }
        
        opportunities = [high_credibility_opp, medium_credibility_opp, low_credibility_opp]
        enhanced = enhance_opportunities_with_credibility(opportunities)
        
        # Verify credibility indicators match expectations
        assert enhanced[0]["credibility_indicator"] == "🟢"  # High credibility
        assert enhanced[1]["credibility_indicator"] == "🟡"  # Medium credibility  
        assert enhanced[2]["credibility_indicator"] == "🔴"  # Low credibility
        
        # Verify source count displays are informative
        assert "3 sources" in enhanced[0]["source_count_display"]
        assert "2 sources" in enhanced[1]["source_count_display"]
        assert "Limited sources" in enhanced[2]["source_count_display"]

    def test_three_tier_architecture_implementation(self):
        """Test that the three-tier progressive disclosure architecture is properly implemented"""
        opportunity = {
            "title": "Test Opportunity",
            "description": "Summary level description",
            "supporting_evidence": "Detailed evidence for implementation",
            "next_steps": ["Step 1", "Step 2"],
            "source_urls": ["https://example.com/source1"]
        }
        
        enhanced = enhance_opportunities_with_credibility([opportunity])
        enhanced_opp = enhanced[0]
        
        # Tier 1: Summary level (always available)
        assert "title" in enhanced_opp
        assert "description" in enhanced_opp
        assert "opportunity_score" in enhanced_opp
        assert "credibility_indicator" in enhanced_opp
        
        # Tier 2: Details level (flagged for availability)
        assert enhanced_opp["has_detailed_analysis"] == True
        assert "supporting_evidence" in enhanced_opp
        assert "next_steps" in enhanced_opp
        
        # Tier 3: Full analysis level (flagged for availability)
        assert enhanced_opp["has_source_analysis"] == True
        assert "detailed_analysis" in enhanced_opp
        assert "source_urls" in enhanced_opp

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 