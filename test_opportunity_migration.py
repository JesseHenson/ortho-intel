# test_opportunity_migration.py
"""
Comprehensive test suite for opportunity-first migration
Validates all components and ensures backward compatibility
"""

import pytest
import sys
import os
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import components to test
from opportunity_data_models import (
    StrategicOpportunity,
    OpportunityCategory,
    ImplementationDifficulty,
    InvestmentLevel,
    CompetitiveRisk,
    CategoryOpportunity,
    CompetitorProfile,
    ExecutiveSummary,
    OpportunityAnalysisResponse,
    OpportunityTransformer,
    OpportunityRanker,
    OpportunityMatrix,
    enhance_graph_state_with_opportunities
)

from main_langgraph_opportunity import OpportunityIntelligenceGraph

class TestOpportunityDataModels:
    """Test opportunity data models"""
    
    def test_strategic_opportunity_creation(self):
        """Test creating a strategic opportunity"""
        opportunity = StrategicOpportunity(
            id=1,
            title="Test Opportunity",
            category=OpportunityCategory.PRODUCT_INNOVATION,
            description="Test description",
            opportunity_score=8.5,
            implementation_difficulty=ImplementationDifficulty.MEDIUM,
            time_to_market="6-12 months",
            investment_level=InvestmentLevel.MEDIUM,
            competitive_risk=CompetitiveRisk.LOW,
            potential_impact="High impact",
            next_steps=["Step 1", "Step 2"],
            supporting_evidence="Test evidence",
            confidence_level=8.0
        )
        
        assert opportunity.id == 1
        assert opportunity.title == "Test Opportunity"
        assert opportunity.category == OpportunityCategory.PRODUCT_INNOVATION
        assert opportunity.opportunity_score == 8.5
        assert len(opportunity.next_steps) == 2
    
    def test_category_opportunity_creation(self):
        """Test creating a category opportunity"""
        category_opp = CategoryOpportunity(
            opportunity="Test Category Opportunity",
            current_gap="Test gap",
            recommendation="Test recommendation",
            implementation="Test implementation",
            timeline="6 months",
            investment="Medium"
        )
        
        assert category_opp.opportunity == "Test Category Opportunity"
        assert category_opp.current_gap == "Test gap"
        assert category_opp.timeline == "6 months"
    
    def test_executive_summary_creation(self):
        """Test creating an executive summary"""
        summary = ExecutiveSummary(
            key_insight="Test insight",
            top_3_opportunities=["Opp 1", "Opp 2", "Opp 3"],
            immediate_actions=["Action 1", "Action 2"],
            strategic_focus="Test focus",
            competitive_advantage="Test advantage",
            revenue_potential="$10M-20M",
            market_share_opportunity="5-10%",
            investment_required="$2M-5M"
        )
        
        assert summary.key_insight == "Test insight"
        assert len(summary.top_3_opportunities) == 3
        assert summary.revenue_potential == "$10M-20M"
    
    def test_opportunity_transformer(self):
        """Test opportunity transformation functionality"""
        # Test clinical gaps to opportunities
        clinical_gaps = [
            {
                "competitor": "Test Competitor",
                "gap_type": "clinical_limitation",
                "description": "Test clinical gap",
                "severity": "high"
            }
        ]
        
        opportunities = OpportunityTransformer.clinical_gaps_to_opportunities(clinical_gaps)
        
        assert len(opportunities) > 0
        assert isinstance(opportunities[0], StrategicOpportunity)
        assert "Test Competitor" in opportunities[0].supporting_evidence
    
    def test_opportunity_ranker(self):
        """Test opportunity ranking functionality"""
        opportunities = [
            StrategicOpportunity(
                id=1,
                title="High Score Opportunity",
                category=OpportunityCategory.PRODUCT_INNOVATION,
                description="High scoring opportunity",
                opportunity_score=9.0,
                implementation_difficulty=ImplementationDifficulty.EASY,
                time_to_market="3-6 months",
                investment_level=InvestmentLevel.LOW,
                competitive_risk=CompetitiveRisk.LOW,
                potential_impact="High impact",
                next_steps=["Step 1"],
                supporting_evidence="Evidence",
                confidence_level=9.0
            ),
            StrategicOpportunity(
                id=2,
                title="Low Score Opportunity",
                category=OpportunityCategory.BRAND_STRATEGY,
                description="Low scoring opportunity",
                opportunity_score=5.0,
                implementation_difficulty=ImplementationDifficulty.HARD,
                time_to_market="12-18 months",
                investment_level=InvestmentLevel.HIGH,
                competitive_risk=CompetitiveRisk.HIGH,
                potential_impact="Medium impact",
                next_steps=["Step 1"],
                supporting_evidence="Evidence",
                confidence_level=5.0
            )
        ]
        
        ranked = OpportunityRanker.rank_opportunities(opportunities)
        
        assert len(ranked) == 2
        assert ranked[0].opportunity_score > ranked[1].opportunity_score
        assert ranked[0].title == "High Score Opportunity"
    
    def test_opportunity_matrix_creation(self):
        """Test opportunity matrix creation"""
        opportunities = [
            StrategicOpportunity(
                id=1,
                title="Test Opportunity",
                category=OpportunityCategory.PRODUCT_INNOVATION,
                description="Test",
                opportunity_score=8.0,
                implementation_difficulty=ImplementationDifficulty.MEDIUM,
                time_to_market="6 months",
                investment_level=InvestmentLevel.MEDIUM,
                competitive_risk=CompetitiveRisk.MEDIUM,
                potential_impact="High",
                next_steps=["Step 1"],
                supporting_evidence="Evidence",
                confidence_level=8.0
            )
        ]
        
        matrix = OpportunityRanker.create_opportunity_matrix(opportunities)
        
        assert isinstance(matrix, OpportunityMatrix)
        assert len(matrix.opportunities) == 1
        assert matrix.opportunities[0]["title"] == "Test Opportunity"
    
    def test_graph_state_enhancement(self):
        """Test graph state enhancement with opportunity fields"""
        original_state = {
            "competitors": ["Competitor 1", "Competitor 2"],
            "focus_area": "spine_fusion"
        }
        
        enhanced_state = enhance_graph_state_with_opportunities(original_state)
        
        # Check that original fields are preserved
        assert enhanced_state["competitors"] == ["Competitor 1", "Competitor 2"]
        assert enhanced_state["focus_area"] == "spine_fusion"
        
        # Check that new opportunity fields are added
        assert "top_opportunities" in enhanced_state
        assert "opportunity_matrix" in enhanced_state
        assert "brand_opportunities" in enhanced_state
        assert "product_opportunities" in enhanced_state
        assert "pricing_opportunities" in enhanced_state
        assert "market_expansion_opportunities" in enhanced_state
        assert "executive_summary" in enhanced_state
        assert "competitive_profiles" in enhanced_state

class TestOpportunityPipeline:
    """Test the enhanced opportunity pipeline"""
    
    def test_pipeline_initialization(self):
        """Test that the opportunity pipeline initializes correctly"""
        graph = OpportunityIntelligenceGraph()
        
        assert graph is not None
        assert graph.graph is not None
    
    @patch('main_langgraph_opportunity.tavily_tool')
    @patch('main_langgraph_opportunity.llm')
    def test_detect_category_node(self, mock_llm, mock_tavily):
        """Test the detect_category node"""
        graph = OpportunityIntelligenceGraph()
        
        test_state = {
            "competitors": ["Stryker Spine", "Zimmer Biomet"],
            "focus_area": "spine_fusion"
        }
        
        result = graph.detect_category(test_state)
        
        assert "device_category" in result
        assert result["competitors"] == ["Stryker Spine", "Zimmer Biomet"]
        assert result["focus_area"] == "spine_fusion"
        
        # Check that opportunity fields were added
        assert "top_opportunities" in result
        assert "opportunity_matrix" in result
    
    @patch('main_langgraph_opportunity.tavily_tool')
    @patch('main_langgraph_opportunity.llm')
    def test_initialize_research_node(self, mock_llm, mock_tavily):
        """Test the initialize_research node"""
        graph = OpportunityIntelligenceGraph()
        
        test_state = {
            "competitors": ["Stryker Spine"],
            "focus_area": "spine_fusion",
            "device_category": "spine_fusion"
        }
        
        result = graph.initialize_research(test_state)
        
        assert "search_queries" in result
        assert "current_competitor" in result
        assert "research_iteration" in result
        assert len(result["search_queries"]) > 0
        assert result["current_competitor"] == "Stryker Spine"
    
    def test_opportunity_query_generation(self):
        """Test opportunity-focused query generation"""
        graph = OpportunityIntelligenceGraph()
        
        queries = graph._generate_opportunity_queries("Stryker Spine", "spine_fusion")
        
        assert len(queries) > 0
        assert any("opportunity" in query.lower() for query in queries)
        assert any("Stryker Spine" in query for query in queries)
    
    def test_strategic_query_generation(self):
        """Test strategic query generation"""
        graph = OpportunityIntelligenceGraph()
        
        queries = graph._generate_strategic_queries("spine_fusion", ["Stryker Spine", "Zimmer Biomet"])
        
        assert len(queries) > 0
        assert any("trends" in query.lower() for query in queries)
        assert any("opportunities" in query.lower() for query in queries)

class TestBackwardCompatibility:
    """Test that the new system maintains backward compatibility"""
    
    def test_original_data_models_still_work(self):
        """Test that original data models are still functional"""
        from data_models import ClinicalGap, MarketOpportunity, MarketShareInsight
        
        # Test ClinicalGap creation
        gap = ClinicalGap(
            competitor="Test Competitor",
            gap_type="clinical_limitation",
            description="Test gap",
            evidence="Test evidence",
            severity="medium",
            source_url="http://test.com"
        )
        
        assert gap.competitor == "Test Competitor"
        assert gap.gap_type == "clinical_limitation"
        
        # Test MarketOpportunity creation
        opportunity = MarketOpportunity(
            opportunity_type="market_expansion",
            description="Test opportunity",
            market_size_indicator="Large",
            competitive_landscape="Fragmented",
            evidence="Test evidence",
            source_url="http://test.com"
        )
        
        assert opportunity.opportunity_type == "market_expansion"
        assert opportunity.description == "Test opportunity"
        
        # Test MarketShareInsight creation
        insight = MarketShareInsight(
            competitor="Test Competitor",
            market_position="Leader",
            estimated_market_share="25%",
            revenue_estimate="$100M",
            growth_trend="Growing",
            key_markets=["US", "Europe"],
            evidence="Test evidence",
            source_url="http://test.com"
        )
        
        assert insight.competitor == "Test Competitor"
        assert insight.market_position == "Leader"
    
    def test_original_pipeline_components_accessible(self):
        """Test that original pipeline components are still accessible"""
        from data_models import SearchTemplates, AnalysisProcessor, CategoryRouter
        
        # Test SearchTemplates
        queries = SearchTemplates.get_competitor_queries("Stryker", "spine_fusion", "spine_fusion")
        assert len(queries) > 0
        
        # Test CategoryRouter
        category = CategoryRouter.detect_category(["Stryker Spine"], "spine_fusion")
        assert category is not None
        
        # Test AnalysisProcessor methods exist
        assert hasattr(AnalysisProcessor, 'extract_clinical_gaps')
        assert hasattr(AnalysisProcessor, 'extract_market_opportunities')

class TestIntegration:
    """Integration tests for the complete opportunity-first system"""
    
    @patch('main_langgraph_opportunity.tavily_tool')
    @patch('main_langgraph_opportunity.llm')
    def test_end_to_end_pipeline_mock(self, mock_llm, mock_tavily):
        """Test the complete pipeline with mocked external services"""
        
        # Mock Tavily responses
        mock_tavily.invoke.return_value = [
            {
                "url": "http://test.com",
                "title": "Test Article",
                "content": "Test content about spine fusion devices and market opportunities",
                "score": 0.9
            }
        ]
        
        # Mock LLM responses
        mock_response = Mock()
        mock_response.content = """
        CLINICAL: Limited minimally invasive options
        PRODUCT: Lack of digital integration features
        BRAND: Weak outcome-focused messaging
        MARKET: Limited presence in ASC segment
        """
        mock_llm.invoke.return_value = mock_response
        
        # Run the pipeline
        graph = OpportunityIntelligenceGraph()
        result = graph.run_analysis(["Stryker Spine"], "spine_fusion")
        
        # Validate results
        assert "error" not in result
        assert "final_report" in result
        assert "top_opportunities" in result
        assert "executive_summary" in result
        
        # Check that opportunities were generated
        top_opportunities = result.get("top_opportunities", [])
        assert len(top_opportunities) > 0
        
        # Check that executive summary was created
        executive_summary = result.get("executive_summary", {})
        assert "key_insight" in executive_summary
        assert "top_3_opportunities" in executive_summary
    
    def test_frontend_import_compatibility(self):
        """Test that the frontend can import all required components"""
        try:
            import streamlit_app_opportunity
            from streamlit_app_opportunity import main, show_demo_dashboard
            
            # Test that key functions exist
            assert callable(main)
            assert callable(show_demo_dashboard)
            
        except ImportError as e:
            pytest.fail(f"Frontend import failed: {e}")

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_competitors_list(self):
        """Test handling of empty competitors list"""
        graph = OpportunityIntelligenceGraph()
        
        result = graph.run_analysis([], "spine_fusion")
        
        # Should handle gracefully
        assert "error" in result or len(result.get("competitors", [])) == 0
    
    def test_invalid_focus_area(self):
        """Test handling of invalid focus area"""
        graph = OpportunityIntelligenceGraph()
        
        result = graph.run_analysis(["Stryker Spine"], "invalid_focus_area")
        
        # Should still work or handle gracefully
        assert result is not None
    
    @patch('main_langgraph_opportunity.tavily_tool')
    def test_tavily_failure_handling(self, mock_tavily):
        """Test handling of Tavily API failures"""
        
        # Mock Tavily to raise an exception
        mock_tavily.invoke.side_effect = Exception("API Error")
        
        graph = OpportunityIntelligenceGraph()
        
        # Should handle the error gracefully
        test_state = {
            "competitors": ["Stryker Spine"],
            "focus_area": "spine_fusion",
            "device_category": "spine_fusion",
            "current_competitor": "Stryker Spine",
            "research_iteration": 0,
            "raw_research_results": [],
            "error_messages": []
        }
        
        result = graph.research_competitor(test_state)
        
        # Should continue despite the error
        assert result is not None
        assert "error_messages" in result

def run_migration_validation():
    """Run comprehensive migration validation"""
    
    print("🧪 Running Opportunity-First Migration Validation...")
    
    # Test 1: Data Models
    print("   ✓ Testing opportunity data models...")
    test_models = TestOpportunityDataModels()
    test_models.test_strategic_opportunity_creation()
    test_models.test_opportunity_transformer()
    test_models.test_opportunity_ranker()
    print("   ✅ Data models validated")
    
    # Test 2: Pipeline Components
    print("   ✓ Testing pipeline components...")
    test_pipeline = TestOpportunityPipeline()
    test_pipeline.test_pipeline_initialization()
    print("   ✅ Pipeline components validated")
    
    # Test 3: Backward Compatibility
    print("   ✓ Testing backward compatibility...")
    test_compat = TestBackwardCompatibility()
    test_compat.test_original_data_models_still_work()
    test_compat.test_original_pipeline_components_accessible()
    print("   ✅ Backward compatibility validated")
    
    # Test 4: Frontend Integration
    print("   ✓ Testing frontend integration...")
    test_integration = TestIntegration()
    test_integration.test_frontend_import_compatibility()
    print("   ✅ Frontend integration validated")
    
    # Test 5: Error Handling
    print("   ✓ Testing error handling...")
    test_errors = TestErrorHandling()
    test_errors.test_empty_competitors_list()
    test_errors.test_invalid_focus_area()
    print("   ✅ Error handling validated")
    
    print("✅ Migration validation complete! All tests passed.")
    return True

if __name__ == "__main__":
    # Run validation when script is executed directly
    run_migration_validation() 