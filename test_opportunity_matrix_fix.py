"""
Test for OpportunityMatrix validation error fix
Reproduces the Pydantic validation error and validates the fix
"""

import pytest
from typing import List, Dict, Any
from opportunity_data_models import (
    OpportunityMatrix, 
    StrategicOpportunity, 
    OpportunityCategory,
    ImplementationDifficulty,
    InvestmentLevel,
    CompetitiveRisk,
    OpportunityRanker
)

class TestOpportunityMatrixValidation:
    """Test suite for OpportunityMatrix validation issues"""
    
    def test_opportunity_matrix_validation_fixed(self):
        """Test that the validation error has been fixed"""
        
        # This data previously caused validation errors but should now work
        previously_problematic_data = {
            "high_impact_hard": [
                {"name": "Market Position Opportunity", "impact": 8.0, "difficulty": 7.0},
                {"name": "AI-Identified Strategic Opportunity", "impact": 8.5, "difficulty": 8.0}
            ],
            "low_impact_hard": [
                {"name": "Address clinical Gap", "impact": 5.0, "difficulty": 7.0},
                {"name": "Address clinical Gap", "impact": 4.5, "difficulty": 7.5},
                {"name": "Address clinical Gap", "impact": 4.0, "difficulty": 8.0},
                {"name": "Address clinical Gap", "impact": 3.5, "difficulty": 7.0},
                {"name": "Address clinical Gap", "impact": 3.0, "difficulty": 8.5},
                {"name": "Address comprehensive_analysis Gap", "impact": 4.0, "difficulty": 9.0}
            ],
            "high_impact_easy": [],
            "low_impact_easy": []
        }
        
        # This should now work without raising a validation error
        matrix = OpportunityMatrix(**previously_problematic_data)
        
        # Verify the data is correctly stored
        assert len(matrix.high_impact_hard) == 2
        assert matrix.high_impact_hard[0]["name"] == "Market Position Opportunity"
        assert matrix.high_impact_hard[0]["impact"] == 8.0
        assert matrix.high_impact_hard[0]["difficulty"] == 7.0
        
        assert len(matrix.low_impact_hard) == 6
        assert matrix.low_impact_hard[0]["name"] == "Address clinical Gap"
        assert matrix.low_impact_hard[0]["impact"] == 5.0
    
    def test_opportunity_matrix_with_correct_structure(self):
        """Test that OpportunityMatrix works with the correct data structure"""
        
        # This should work after the fix
        correct_data = {
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
        
        # This should not raise an error after the fix
        matrix = OpportunityMatrix(**correct_data)
        
        # Verify the data is correctly stored
        assert len(matrix.high_impact_easy) == 1
        assert matrix.high_impact_easy[0]["name"] == "Quick Win Opportunity"
        assert matrix.high_impact_easy[0]["impact"] == 8.0
        assert matrix.high_impact_easy[0]["difficulty"] == 3.0
    
    def test_create_opportunity_matrix_from_strategic_opportunities(self):
        """Test the OpportunityRanker.create_opportunity_matrix method"""
        
        # Create test strategic opportunities
        opportunities = [
            StrategicOpportunity(
                id=1,
                title="High Impact Easy Opportunity",
                category=OpportunityCategory.PRODUCT_INNOVATION,
                description="Test opportunity",
                opportunity_score=8.5,
                implementation_difficulty=ImplementationDifficulty.EASY,
                time_to_market="6 months",
                investment_level=InvestmentLevel.LOW,
                competitive_risk=CompetitiveRisk.LOW,
                potential_impact="High revenue impact",
                next_steps=["Step 1", "Step 2"],
                supporting_evidence="Test evidence"
            ),
            StrategicOpportunity(
                id=2,
                title="High Impact Hard Opportunity",
                category=OpportunityCategory.MARKET_POSITIONING,
                description="Complex opportunity",
                opportunity_score=9.0,
                implementation_difficulty=ImplementationDifficulty.HARD,
                time_to_market="18 months",
                investment_level=InvestmentLevel.HIGH,
                competitive_risk=CompetitiveRisk.MEDIUM,
                potential_impact="Market leadership",
                next_steps=["Research", "Plan", "Execute"],
                supporting_evidence="Market analysis"
            ),
            StrategicOpportunity(
                id=3,
                title="Low Impact Easy Opportunity",
                category=OpportunityCategory.OPERATIONAL_EFFICIENCY,
                description="Simple improvement",
                opportunity_score=5.0,
                implementation_difficulty=ImplementationDifficulty.EASY,
                time_to_market="3 months",
                investment_level=InvestmentLevel.LOW,
                competitive_risk=CompetitiveRisk.LOW,
                potential_impact="Cost savings",
                next_steps=["Implement"],
                supporting_evidence="Internal analysis"
            )
        ]
        
        # Create matrix - this should not raise an error after the fix
        matrix = OpportunityRanker.create_opportunity_matrix(opportunities)
        
        # Verify the matrix structure
        assert isinstance(matrix, OpportunityMatrix)
        
        # Check that opportunities are correctly categorized
        assert len(matrix.high_impact_easy) == 1
        assert matrix.high_impact_easy[0]["name"] == "High Impact Easy Opportunity"
        assert matrix.high_impact_easy[0]["impact"] == 8.5
        
        assert len(matrix.high_impact_hard) == 1
        assert matrix.high_impact_hard[0]["name"] == "High Impact Hard Opportunity"
        assert matrix.high_impact_hard[0]["impact"] == 9.0
        
        assert len(matrix.low_impact_easy) == 1
        assert matrix.low_impact_easy[0]["name"] == "Low Impact Easy Opportunity"
        assert matrix.low_impact_easy[0]["impact"] == 5.0
    
    def test_opportunity_matrix_empty_categories(self):
        """Test OpportunityMatrix with empty categories"""
        
        empty_data = {
            "high_impact_easy": [],
            "high_impact_hard": [],
            "low_impact_easy": [],
            "low_impact_hard": []
        }
        
        # This should work
        matrix = OpportunityMatrix(**empty_data)
        assert len(matrix.high_impact_easy) == 0
        assert len(matrix.high_impact_hard) == 0
        assert len(matrix.low_impact_easy) == 0
        assert len(matrix.low_impact_hard) == 0
    
    def test_opportunity_matrix_data_types(self):
        """Test that OpportunityMatrix enforces correct data types"""
        
        # Test with correct types
        correct_data = {
            "high_impact_easy": [
                {"name": "Test Opportunity", "impact": 8.0, "difficulty": 3.0}
            ],
            "high_impact_hard": [],
            "low_impact_easy": [],
            "low_impact_hard": []
        }
        
        matrix = OpportunityMatrix(**correct_data)
        assert matrix.high_impact_easy[0]["name"] == "Test Opportunity"
        assert isinstance(matrix.high_impact_easy[0]["impact"], float)
        assert isinstance(matrix.high_impact_easy[0]["difficulty"], float)
    
    def test_integration_with_demo_frontend_adapter(self):
        """Test that the fixed OpportunityMatrix works with the demo frontend adapter"""
        
        # Simulate the data structure that would come from the live pipeline
        live_result = {
            "final_report": {
                "top_opportunities": [
                    {
                        "title": "Market Position Opportunity",
                        "category": "Market Positioning",
                        "description": "Strategic market opportunity",
                        "opportunity_score": 8.0,
                        "implementation_difficulty": "Medium",
                        "time_to_market": "6-12 months",
                        "investment_level": "Medium",
                        "competitive_risk": "Medium",
                        "potential_impact": "Significant opportunity",
                        "next_steps": ["Analyze", "Plan", "Execute"],
                        "supporting_evidence": "Market research"
                    }
                ]
            }
        }
        
        # Import and test the adapter
        from demo_frontend_adapter import DemoFrontendAdapter
        
        # This should not raise an error after the fix
        adapted_data = DemoFrontendAdapter._adapt_live_data_to_demo_format(
            live_result, 
            ["Stryker Spine"], 
            "spine_fusion"
        )
        
        # Verify the adapted data has the correct structure
        assert "opportunity_matrix" in adapted_data
        matrix_data = adapted_data["opportunity_matrix"]
        
        # Verify it's a valid structure (should have the required keys)
        required_keys = ["high_impact_easy", "high_impact_hard", "low_impact_easy", "low_impact_hard"]
        for key in required_keys:
            assert key in matrix_data

if __name__ == "__main__":
    # Run the tests
    test_suite = TestOpportunityMatrixValidation()
    
    print("Testing OpportunityMatrix validation fix...")
    
    try:
        test_suite.test_opportunity_matrix_validation_fixed()
        print("✅ OpportunityMatrix validation fix confirmed - previously problematic data now works")
    except Exception as e:
        print(f"❌ OpportunityMatrix validation fix failed: {e}")
    
    print("\nRunning other tests...")
    
    try:
        test_suite.test_opportunity_matrix_with_correct_structure()
        print("✅ Correct structure test passed")
    except Exception as e:
        print(f"❌ Correct structure test failed: {e}")
    
    try:
        test_suite.test_create_opportunity_matrix_from_strategic_opportunities()
        print("✅ Strategic opportunities matrix creation test passed")
    except Exception as e:
        print(f"❌ Strategic opportunities test failed: {e}")
    
    try:
        test_suite.test_opportunity_matrix_empty_categories()
        print("✅ Empty categories test passed")
    except Exception as e:
        print(f"❌ Empty categories test failed: {e}")
    
    try:
        test_suite.test_opportunity_matrix_data_types()
        print("✅ Data types test passed")
    except Exception as e:
        print(f"❌ Data types test failed: {e}")
    
    try:
        test_suite.test_integration_with_demo_frontend_adapter()
        print("✅ Demo frontend adapter integration test passed")
    except Exception as e:
        print(f"❌ Demo frontend adapter test failed: {e}")
    
    print("\nTest suite completed!") 