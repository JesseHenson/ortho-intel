"""
Test suite for Progressive Disclosure Components

Tests the accordion UI components for opportunity analysis,
ensuring proper rendering, state management, and accessibility.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import patch, MagicMock
import streamlit as st

# Import components to test
from src.frontend.components.progressive_disclosure import (
    OpportunityCard, OpportunityDetails, AnalysisBreakdown,
    SourceCitationSystem, ProgressiveDisclosureManager,
    render_opportunities_with_progressive_disclosure,
    create_opportunity_summary_grid
)

class TestOpportunityCard:
    """Test suite for OpportunityCard component"""
    
    def setup_method(self):
        """Set up test data"""
        self.mock_opportunity = {
            "id": 1,
            "title": "AI-Powered Surgical Planning",
            "category": "Product Innovation",
            "opportunity_score": 8.5,
            "time_to_market": "12-18 months",
            "investment_level": "High",
            "credibility_indicator": "🟢",
            "source_count_display": "3 sources"
        }
    
    @patch('streamlit.markdown')
    @patch('streamlit.button')
    @patch('streamlit.container')
    def test_render_with_expand_button(self, mock_container, mock_button, mock_markdown):
        """Test OpportunityCard rendering with expand button"""
        mock_button.return_value = False
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        result = OpportunityCard.render(self.mock_opportunity, index=0, show_expand_button=True)
        
        # Verify markdown was called for card rendering
        assert mock_markdown.called
        # Verify button was created
        assert mock_button.called
        # Verify return value
        assert result == False
    
    @patch('streamlit.markdown')
    @patch('streamlit.button')
    @patch('streamlit.container')
    def test_render_without_expand_button(self, mock_container, mock_button, mock_markdown):
        """Test OpportunityCard rendering without expand button"""
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        result = OpportunityCard.render(self.mock_opportunity, index=0, show_expand_button=False)
        
        # Verify markdown was called for card rendering
        assert mock_markdown.called
        # Verify button was NOT created
        assert not mock_button.called
        # Verify return value
        assert result == False
    
    @patch('streamlit.markdown')
    @patch('streamlit.button')
    @patch('streamlit.container')
    def test_render_with_button_click(self, mock_container, mock_button, mock_markdown):
        """Test OpportunityCard when expand button is clicked"""
        mock_button.return_value = True  # Simulate button click
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        result = OpportunityCard.render(self.mock_opportunity, index=0, show_expand_button=True)
        
        # Verify return value indicates expansion
        assert result == True
    
    def test_render_with_missing_fields(self):
        """Test OpportunityCard with missing optional fields"""
        minimal_opportunity = {"title": "Test Opportunity"}
        
        # Should not raise exception and use defaults
        with patch('streamlit.markdown'), patch('streamlit.container') as mock_container:
            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock()
            
            result = OpportunityCard.render(minimal_opportunity, index=0, show_expand_button=False)
            assert result == False

class TestOpportunityDetails:
    """Test suite for OpportunityDetails component"""
    
    def setup_method(self):
        """Set up test data"""
        self.mock_opportunity = {
            "id": 1,
            "title": "AI-Powered Surgical Planning",
            "description": "Develop AI-enabled surgical planning platform",
            "potential_impact": "Significant competitive advantage",
            "implementation_difficulty": "Medium",
            "competitive_risk": "Low",
            "next_steps": [
                "Conduct market research",
                "Develop prototype",
                "Validate with surgeons"
            ]
        }
    
    @patch('streamlit.markdown')
    @patch('streamlit.button')
    @patch('streamlit.container')
    def test_render_with_full_analysis_button(self, mock_container, mock_button, mock_markdown):
        """Test OpportunityDetails rendering with full analysis button"""
        mock_button.return_value = False
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        result = OpportunityDetails.render(self.mock_opportunity, index=0, show_full_analysis_button=True)
        
        # Verify markdown was called for details rendering
        assert mock_markdown.called
        # Verify button was created
        assert mock_button.called
        # Verify return value
        assert result == False
    
    @patch('streamlit.markdown')
    @patch('streamlit.button')
    @patch('streamlit.container')
    def test_render_with_button_click(self, mock_container, mock_button, mock_markdown):
        """Test OpportunityDetails when full analysis button is clicked"""
        mock_button.return_value = True  # Simulate button click
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        result = OpportunityDetails.render(self.mock_opportunity, index=0, show_full_analysis_button=True)
        
        # Verify return value indicates full analysis request
        assert result == True
    
    def test_risk_color_mapping(self):
        """Test that risk and difficulty colors are mapped correctly"""
        # Test different risk levels
        test_cases = [
            ("Low", "#11998e"),
            ("Medium", "#ffa726"),
            ("High", "#ff6b6b"),
            ("Unknown", "#ffa726")  # Default
        ]
        
        for risk_level, expected_color in test_cases:
            opportunity = self.mock_opportunity.copy()
            opportunity["competitive_risk"] = risk_level
            opportunity["implementation_difficulty"] = risk_level
            
            with patch('streamlit.markdown') as mock_markdown, \
                 patch('streamlit.container') as mock_container:
                mock_container.return_value.__enter__ = MagicMock()
                mock_container.return_value.__exit__ = MagicMock()
                
                OpportunityDetails.render(opportunity, index=0, show_full_analysis_button=False)
                
                # Check that the expected color appears in the markdown calls
                markdown_calls = [call[0][0] for call in mock_markdown.call_args_list]
                color_found = any(expected_color in call for call in markdown_calls)
                assert color_found, f"Expected color {expected_color} not found for risk level {risk_level}"

class TestAnalysisBreakdown:
    """Test suite for AnalysisBreakdown component"""
    
    def setup_method(self):
        """Set up test data"""
        self.mock_opportunity = {
            "id": 1,
            "title": "AI-Powered Surgical Planning",
            "supporting_evidence": "Market research shows 70% of surgeons want AI integration",
            "source_urls": [
                "https://pubmed.ncbi.nlm.nih.gov/example1",
                "https://example.com/source2"
            ],
            "confidence_level": 8.5,
            "detailed_analysis": "Comprehensive analysis of market opportunity",
            "analysis_methodology": "AI-powered competitive gap analysis"
        }
    
    @patch('streamlit.markdown')
    @patch('streamlit.info')
    @patch('streamlit.container')
    @patch('src.frontend.components.progressive_disclosure.SourceCitationSystem.render_source_list')
    def test_render_complete_analysis(self, mock_render_sources, mock_container, mock_info, mock_markdown):
        """Test AnalysisBreakdown rendering with complete data"""
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        AnalysisBreakdown.render(self.mock_opportunity, index=0)
        
        # Verify markdown was called for analysis rendering
        assert mock_markdown.called
        # Verify info was called for methodology
        assert mock_info.called
        # Verify source rendering was called
        assert mock_render_sources.called
    
    @patch('streamlit.markdown')
    @patch('streamlit.container')
    def test_render_minimal_analysis(self, mock_container, mock_markdown):
        """Test AnalysisBreakdown with minimal data"""
        minimal_opportunity = {"title": "Test Opportunity"}
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        # Should not raise exception
        AnalysisBreakdown.render(minimal_opportunity, index=0)
        
        # Verify markdown was called
        assert mock_markdown.called

class TestSourceCitationSystem:
    """Test suite for SourceCitationSystem component"""
    
    def test_extract_domain(self):
        """Test domain extraction from URLs"""
        test_cases = [
            ("https://www.example.com/path", "example.com"),
            ("http://pubmed.ncbi.nlm.nih.gov/12345", "pubmed.ncbi.nlm.nih.gov"),
            ("https://forbes.com/article", "forbes.com"),
            ("invalid-url", "invalid-url")  # Fallback case
        ]
        
        for url, expected_domain in test_cases:
            result = SourceCitationSystem.extract_domain(url)
            assert result == expected_domain
    
    def test_assess_credibility(self):
        """Test credibility assessment for different domains"""
        test_cases = [
            ("pubmed.ncbi.nlm.nih.gov", "high"),
            ("fda.gov", "high"),
            ("reuters.com", "high"),
            ("forbes.com", "medium"),
            ("cnn.com", "medium"),
            ("medscape.com", "medium"),
            ("blog.example.com", "low"),
            ("medium.com", "low"),
            ("unknown-domain.com", "unknown")
        ]
        
        for domain, expected_credibility in test_cases:
            result = SourceCitationSystem.assess_credibility(domain)
            assert result == expected_credibility
    
    @patch('streamlit.markdown')
    @patch('streamlit.columns')
    def test_render_source_citation(self, mock_columns, mock_markdown):
        """Test individual source citation rendering"""
        mock_columns.return_value = [MagicMock(), MagicMock()]
        
        url = "https://pubmed.ncbi.nlm.nih.gov/example"
        SourceCitationSystem.render_source_citation(url, "test_key")
        
        # Verify columns were created
        assert mock_columns.called
        # Verify markdown was called for rendering
        assert mock_markdown.called
    
    @patch('streamlit.info')
    @patch('src.frontend.components.progressive_disclosure.SourceCitationSystem.render_source_citation')
    def test_render_source_list_empty(self, mock_render_citation, mock_info):
        """Test source list rendering with empty list"""
        SourceCitationSystem.render_source_list([], "test_key")
        
        # Verify info message was shown
        assert mock_info.called
        # Verify no citations were rendered
        assert not mock_render_citation.called
    
    @patch('src.frontend.components.progressive_disclosure.SourceCitationSystem.render_source_citation')
    def test_render_source_list_with_sources(self, mock_render_citation):
        """Test source list rendering with sources"""
        sources = [
            "https://pubmed.ncbi.nlm.nih.gov/example1",
            "https://example.com/source2"
        ]
        
        SourceCitationSystem.render_source_list(sources, "test_key")
        
        # Verify citations were rendered for each source
        assert mock_render_citation.call_count == len(sources)

class TestProgressiveDisclosureManager:
    """Test suite for ProgressiveDisclosureManager"""
    
    def setup_method(self):
        """Set up test data"""
        self.manager = ProgressiveDisclosureManager()
        self.mock_opportunity = {
            "title": "Test Opportunity",
            "description": "Test description"
        }
    
    @patch('streamlit.session_state', {})
    def test_initialization(self):
        """Test manager initialization"""
        manager = ProgressiveDisclosureManager()
        
        # Verify session state was initialized
        assert 'disclosure_state' in st.session_state
        assert isinstance(st.session_state.disclosure_state, dict)
    
    def test_get_set_state(self):
        """Test state getting and setting"""
        opportunity_id = "test_opp_1"
        
        # Test default state
        state = self.manager.get_state(opportunity_id)
        assert state == 'summary'
        
        # Test setting state
        self.manager.set_state(opportunity_id, 'details')
        state = self.manager.get_state(opportunity_id)
        assert state == 'details'
        
        # Test setting another state
        self.manager.set_state(opportunity_id, 'analysis')
        state = self.manager.get_state(opportunity_id)
        assert state == 'analysis'

class TestUtilityFunctions:
    """Test suite for utility functions"""
    
    def setup_method(self):
        """Set up test data"""
        self.mock_opportunities = [
            {
                "title": "Opportunity 1",
                "description": "First opportunity"
            },
            {
                "title": "Opportunity 2", 
                "description": "Second opportunity"
            }
        ]
    
    @patch('streamlit.markdown')
    @patch('streamlit.info')
    @patch('src.frontend.components.progressive_disclosure.ProgressiveDisclosureManager')
    def test_render_opportunities_empty_list(self, mock_manager, mock_info, mock_markdown):
        """Test rendering with empty opportunities list"""
        render_opportunities_with_progressive_disclosure([], "Test Title")
        
        # Verify info message was shown
        assert mock_info.called
        # Verify manager was not initialized
        assert not mock_manager.called
    
    @patch('streamlit.markdown')
    @patch('src.frontend.components.progressive_disclosure.ProgressiveDisclosureManager')
    def test_render_opportunities_with_data(self, mock_manager_class, mock_markdown):
        """Test rendering with opportunities data"""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        render_opportunities_with_progressive_disclosure(self.mock_opportunities, "Test Title")
        
        # Verify manager was initialized
        assert mock_manager_class.called
        # Verify opportunities were rendered
        assert mock_manager.render_opportunity_with_disclosure.call_count == len(self.mock_opportunities)
    
    @patch('streamlit.columns')
    @patch('streamlit.info')
    @patch('src.frontend.components.progressive_disclosure.OpportunityCard.render')
    def test_create_summary_grid_empty(self, mock_render, mock_info, mock_columns):
        """Test summary grid with empty opportunities"""
        create_opportunity_summary_grid([], columns=2)
        
        # Verify info message was shown
        assert mock_info.called
        # Verify no cards were rendered
        assert not mock_render.called
    
    @patch('streamlit.columns')
    @patch('src.frontend.components.progressive_disclosure.OpportunityCard.render')
    def test_create_summary_grid_with_data(self, mock_render, mock_columns):
        """Test summary grid with opportunities data"""
        mock_columns.return_value = [MagicMock(), MagicMock()]
        
        create_opportunity_summary_grid(self.mock_opportunities, columns=2)
        
        # Verify columns were created
        assert mock_columns.called
        # Verify cards were rendered
        assert mock_render.call_count == len(self.mock_opportunities)

class TestAccessibilityAndResponsiveness:
    """Test suite for accessibility and responsive design features"""
    
    def test_button_help_text(self):
        """Test that buttons include helpful tooltips"""
        opportunity = {"title": "Test Opportunity"}
        
        with patch('streamlit.button') as mock_button, \
             patch('streamlit.container') as mock_container:
            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock()
            
            OpportunityCard.render(opportunity, index=0, show_expand_button=True)
            
            # Verify button was called with help text
            assert mock_button.called
            call_args = mock_button.call_args
            assert 'help' in call_args[1]
    
    def test_semantic_html_structure(self):
        """Test that components use semantic HTML structure"""
        opportunity = {
            "title": "Test Opportunity",
            "description": "Test description"
        }
        
        with patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.container') as mock_container:
            mock_container.return_value.__enter__ = MagicMock()
            mock_container.return_value.__exit__ = MagicMock()
            
            OpportunityDetails.render(opportunity, index=0, show_full_analysis_button=False)
            
            # Verify semantic HTML elements are used
            markdown_calls = [call[0][0] for call in mock_markdown.call_args_list]
            html_content = ' '.join(markdown_calls)
            
            # Check for semantic elements
            assert '<h3' in html_content or '<h4' in html_content
            assert 'style=' in html_content  # CSS styling present

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 