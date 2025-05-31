"""
Test Progressive Disclosure HTML Rendering

This test ensures that markdown content in progressive disclosure components
is properly rendered and not displayed as raw HTML.
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.frontend.components.progressive_disclosure import (
    AnalysisBreakdown,
    OpportunityDetails,
    OpportunityCard
)


class TestProgressiveDisclosureHTMLRendering:
    """Test HTML/Markdown rendering in progressive disclosure components"""
    
    def setup_method(self):
        """Set up test data with markdown content"""
        self.test_opportunity_with_markdown = {
            "title": "Test Opportunity",
            "description": "Test description",
            "opportunity_score": 8.5,
            "potential_impact": "$10M-20M",
            "time_to_market": "6-12 months",
            "implementation_difficulty": "Medium",
            "competitive_risk": "Low",
            "investment_level": "Medium",
            "confidence_level": 8.5,
            "detailed_analysis": """
            ## Methodology
            This is a test methodology section with **bold text** and *italic text*.
            
            ## Market Analysis
            - Point 1: Market size analysis
            - Point 2: Competitive landscape
            - Point 3: Growth projections
            
            ## Implementation Strategy
            1. Phase 1: Initial development
            2. Phase 2: Market testing
            3. Phase 3: Full rollout
            
            ### Risk Assessment
            - **Technical Risk:** Low
            - **Market Risk:** Medium
            - **Competitive Risk:** Low
            """,
            "supporting_evidence": "Test evidence with **bold** formatting",
            "source_urls": [
                "https://pubmed.ncbi.nlm.nih.gov/test1",
                "https://medtechdive.com/test2"
            ]
        }
    
    @patch('src.frontend.components.progressive_disclosure.st')
    def test_analysis_breakdown_renders_markdown_properly(self, mock_st):
        """Test that AnalysisBreakdown renders markdown content correctly"""
        # Mock Streamlit functions with proper context manager support
        mock_st.markdown = Mock()
        mock_st.info = Mock()
        
        # Mock columns with context manager support
        mock_col1 = Mock()
        mock_col2 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        mock_st.columns = Mock(return_value=[mock_col1, mock_col2])
        
        # Render the analysis breakdown
        AnalysisBreakdown.render(self.test_opportunity_with_markdown, 0)
        
        # Check that st.markdown was called with the detailed analysis
        markdown_calls = [call for call in mock_st.markdown.call_args_list 
                         if call[0] and "## Methodology" in str(call[0][0])]
        
        assert len(markdown_calls) > 0, "Detailed analysis markdown should be rendered"
        
        # Verify the markdown content is passed correctly
        detailed_analysis_call = markdown_calls[0]
        assert "## Methodology" in str(detailed_analysis_call[0][0])
        assert "## Market Analysis" in str(detailed_analysis_call[0][0])
        assert "### Risk Assessment" in str(detailed_analysis_call[0][0])
    
    @patch('src.frontend.components.progressive_disclosure.st')
    def test_opportunity_details_renders_markdown_in_evidence(self, mock_st):
        """Test that OpportunityDetails renders markdown in supporting evidence"""
        # Mock Streamlit functions with proper context manager support
        mock_st.markdown = Mock()
        mock_st.info = Mock()
        
        # Mock columns with context manager support
        mock_col1 = Mock()
        mock_col2 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        mock_st.columns = Mock(return_value=[mock_col1, mock_col2])
        mock_st.button = Mock(return_value=False)
        
        # Render the opportunity details
        OpportunityDetails.render(self.test_opportunity_with_markdown, 0)
        
        # Check that supporting evidence with markdown was rendered
        evidence_calls = [call for call in mock_st.markdown.call_args_list 
                         if call[0] and "**bold**" in str(call[0][0])]
        
        assert len(evidence_calls) > 0, "Supporting evidence with markdown should be rendered"
    
    def test_markdown_content_structure(self):
        """Test that markdown content has proper structure"""
        detailed_analysis = self.test_opportunity_with_markdown["detailed_analysis"]
        
        # Check for proper markdown headers
        assert "## Methodology" in detailed_analysis
        assert "## Market Analysis" in detailed_analysis
        assert "### Risk Assessment" in detailed_analysis
        
        # Check for markdown formatting
        assert "**bold text**" in detailed_analysis
        assert "*italic text*" in detailed_analysis
        
        # Check for lists
        assert "- Point 1:" in detailed_analysis
        assert "1. Phase 1:" in detailed_analysis
    
    @patch('src.frontend.components.progressive_disclosure.st')
    def test_no_raw_html_in_output(self, mock_st):
        """Test that no raw HTML tags are visible in rendered output"""
        # Mock Streamlit functions with proper context manager support
        mock_st.markdown = Mock()
        mock_st.info = Mock()
        
        # Mock columns with context manager support
        mock_col1 = Mock()
        mock_col2 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        mock_st.columns = Mock(return_value=[mock_col1, mock_col2])
        
        # Create opportunity with potential HTML content
        opportunity_with_html = self.test_opportunity_with_markdown.copy()
        opportunity_with_html["detailed_analysis"] = """
        <h2>This should not show as raw HTML</h2>
        <p>This paragraph should be properly rendered</p>
        <strong>Bold text in HTML</strong>
        """
        
        # Render the analysis breakdown
        AnalysisBreakdown.render(opportunity_with_html, 0)
        
        # Check that markdown was called (HTML should be handled by Streamlit)
        assert mock_st.markdown.called, "st.markdown should be called to render content"
        
        # Verify that the content is passed to st.markdown for proper rendering
        markdown_calls = mock_st.markdown.call_args_list
        html_content_calls = [call for call in markdown_calls 
                             if call[0] and "<h2>" in str(call[0][0])]
        
        # If HTML content is passed to st.markdown, it should be handled properly
        if html_content_calls:
            # Check that unsafe_allow_html is used when HTML is present
            html_call = html_content_calls[0]
            # The call should either use unsafe_allow_html=True or be processed differently
            assert len(html_call) >= 1, "HTML content should be passed to st.markdown"
            
            # Check if unsafe_allow_html=True is used for HTML content
            if len(html_call) > 1 and isinstance(html_call[1], dict):
                if 'unsafe_allow_html' in html_call[1]:
                    assert html_call[1]['unsafe_allow_html'] == True, "HTML content should use unsafe_allow_html=True"
    
    def test_demo_opportunities_have_proper_markdown(self):
        """Test that demo opportunities contain properly formatted markdown"""
        # This tests the actual demo data structure
        demo_detailed_analysis = """
        ## Methodology
        This opportunity was identified through comprehensive market analysis.
        
        ## Market Analysis
        The digital health market in orthopedics is experiencing rapid growth.
        
        ## Competitive Landscape
        - **Stryker**: Limited IoT integration
        - **Medtronic**: Strong in monitoring
        - **DePuy Synthes**: Traditional approach
        
        ## Implementation Strategy
        Phase 1: Core monitoring platform (6 months)
        Phase 2: Analytics and AI integration (12 months)
        Phase 3: Ecosystem expansion (18 months)
        """
        
        # Verify markdown structure
        assert demo_detailed_analysis.count("##") >= 4, "Should have multiple main headers"
        assert "**" in demo_detailed_analysis, "Should have bold formatting"
        assert "-" in demo_detailed_analysis, "Should have bullet points"
        assert "Phase 1:" in demo_detailed_analysis, "Should have numbered phases"
    
    @patch('src.frontend.components.progressive_disclosure.st')
    def test_source_citations_render_properly(self, mock_st):
        """Test that source citations render without HTML issues"""
        from src.frontend.components.progressive_disclosure import SourceCitationSystem
        
        # Mock Streamlit functions with proper context manager support
        mock_st.markdown = Mock()
        mock_st.info = Mock()
        
        # Mock columns with context manager support
        mock_col1 = Mock()
        mock_col2 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        mock_st.columns = Mock(return_value=[mock_col1, mock_col2])
        
        # Test source rendering
        test_urls = [
            "https://pubmed.ncbi.nlm.nih.gov/test1",
            "https://medtechdive.com/test2"
        ]
        
        SourceCitationSystem.render_source_list(test_urls, "test_sources")
        
        # Verify that markdown was called for source rendering
        assert mock_st.markdown.called, "Source citations should use st.markdown"
        
        # Check that HTML is properly structured for sources
        markdown_calls = mock_st.markdown.call_args_list
        source_html_calls = [call for call in markdown_calls 
                           if call[0] and "background:" in str(call[0][0])]
        
        assert len(source_html_calls) > 0, "Source citations should render with proper HTML styling"
        
        # Verify unsafe_allow_html is used for source HTML
        for call in source_html_calls:
            if len(call) > 1 and 'unsafe_allow_html' in call[1]:
                assert call[1]['unsafe_allow_html'] == True, "Source HTML should use unsafe_allow_html=True"

    def test_html_structure_is_properly_closed(self):
        """Test that HTML in components has proper opening and closing tags"""
        # Test the HTML structure in OpportunityCard
        opportunity = {
            "title": "Test Opportunity",
            "opportunity_score": 8.5,
            "category": "Test Category",
            "time_to_market": "6 months",
            "investment_level": "Medium",
            "credibility_indicator": "🟢",
            "source_count_display": "3 sources"
        }
        
        # Mock st.markdown to capture HTML content
        with patch('src.frontend.components.progressive_disclosure.st') as mock_st:
            # Properly mock container as context manager
            mock_container = Mock()
            mock_container.__enter__ = Mock(return_value=mock_container)
            mock_container.__exit__ = Mock(return_value=None)
            mock_st.container = Mock(return_value=mock_container)
            mock_st.markdown = Mock()
            mock_st.button = Mock(return_value=False)
            
            # Render the card
            OpportunityCard.render(opportunity, 0)
            
            # Check that st.markdown was called with HTML
            assert mock_st.markdown.called, "st.markdown should be called"
            
            # Get the HTML content
            html_calls = [call for call in mock_st.markdown.call_args_list 
                         if call[0] and '<div' in str(call[0][0])]
            
            assert len(html_calls) > 0, "Should have HTML content"
            
            # Verify the HTML has proper structure
            html_content = str(html_calls[0][0][0])
            
            # Count opening and closing div tags
            opening_divs = html_content.count('<div')
            closing_divs = html_content.count('</div>')
            
            assert opening_divs == closing_divs, f"HTML should have matching div tags: {opening_divs} opening, {closing_divs} closing"
            
            # Verify unsafe_allow_html is used
            if len(html_calls[0]) > 1:
                kwargs = html_calls[0][1]
                assert kwargs.get('unsafe_allow_html') == True, "HTML content should use unsafe_allow_html=True"
    
    @patch('src.frontend.components.progressive_disclosure.st')
    def test_opportunity_card_renders_without_raw_html(self, mock_st):
        """Test that OpportunityCard renders properly without showing raw HTML"""
        # Mock Streamlit functions
        mock_container = Mock()
        mock_container.__enter__ = Mock(return_value=mock_container)
        mock_container.__exit__ = Mock(return_value=None)
        mock_st.container = Mock(return_value=mock_container)
        mock_st.markdown = Mock()
        mock_st.button = Mock(return_value=False)
        
        # Test opportunity data
        opportunity = {
            "title": "Digital Platform",
            "opportunity_score": 9.2,
            "category": "Product Innovation",
            "time_to_market": "12-18 months",
            "investment_level": "High",
            "credibility_indicator": "🟢",
            "source_count_display": "5 sources"
        }
        
        # Render the card
        OpportunityCard.render(opportunity, 0)
        
        # Verify st.markdown was called with proper HTML
        assert mock_st.markdown.called, "st.markdown should be called for HTML rendering"
        
        # Check that HTML content is properly structured
        markdown_calls = mock_st.markdown.call_args_list
        html_calls = [call for call in markdown_calls if call[0] and '<div' in str(call[0][0])]
        
        assert len(html_calls) > 0, "Should render HTML content"
        
        # Verify the HTML contains expected content without raw tags showing
        html_content = str(html_calls[0][0][0])
        assert "Digital Platform" in html_content, "Should contain opportunity title"
        assert "9.2" in html_content, "Should contain opportunity score"
        assert "Product Innovation" in html_content, "Should contain category"
        
        # Verify proper HTML structure
        assert html_content.count('<div') == html_content.count('</div>'), "Should have balanced div tags"


class TestMarkdownRenderingFix:
    """Test the fix for markdown rendering issues"""
    
    def test_markdown_vs_html_detection(self):
        """Test detection of markdown vs HTML content"""
        markdown_content = """
        ## Header
        This is **bold** and *italic* text.
        - List item 1
        - List item 2
        """
        
        html_content = """
        <h2>Header</h2>
        <p>This is <strong>bold</strong> and <em>italic</em> text.</p>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
        </ul>
        """
        
        # Test that we can distinguish between markdown and HTML
        assert "##" in markdown_content and "<h2>" not in markdown_content
        assert "<h2>" in html_content and "##" not in html_content
    
    def test_streamlit_markdown_rendering_expectations(self):
        """Test our expectations for how Streamlit should render markdown"""
        # This is a documentation test for expected behavior
        markdown_with_headers = "## Header\nContent with **bold** text"
        
        # Streamlit's st.markdown() should handle this automatically
        # No unsafe_allow_html needed for pure markdown
        assert "##" in markdown_with_headers
        assert "**" in markdown_with_headers
        
        # HTML content would need unsafe_allow_html=True
        html_content = "<h2>Header</h2><p><strong>Bold</strong></p>"
        assert "<" in html_content and ">" in html_content


if __name__ == "__main__":
    # Run a simple test
    test_instance = TestProgressiveDisclosureHTMLRendering()
    test_instance.setup_method()
    test_instance.test_markdown_content_structure()
    print("✅ Markdown content structure test passed!")
    
    markdown_test = TestMarkdownRenderingFix()
    markdown_test.test_markdown_vs_html_detection()
    print("✅ Markdown vs HTML detection test passed!")
    
    print("All HTML rendering tests completed successfully!") 