"""
Permanent test suite for CategoryOpportunity validation.

This test ensures that CategoryOpportunity objects are created correctly
throughout the pipeline and prevents validation errors.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from pydantic import ValidationError
from datetime import datetime

from src.backend.core.opportunity_data_models import CategoryOpportunity
from src.backend.pipelines.main_langgraph_opportunity import OpportunityIntelligenceGraph


class TestCategoryOpportunityValidation:
    """Test suite for CategoryOpportunity validation"""
    
    def test_category_opportunity_requires_id_and_category_type(self):
        """Test that CategoryOpportunity requires id and category_type fields"""
        
        # This should fail - missing required fields
        invalid_data = {
            'opportunity': 'Test Opportunity',
            'current_gap': 'Test gap',
            'recommendation': 'Test recommendation',
            'implementation': 'Test implementation',
            'timeline': 'Test timeline',
            'investment': 'Test investment'
            # Missing: id and category_type
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CategoryOpportunity(**invalid_data)
        
        errors = exc_info.value.errors()
        missing_fields = [error['loc'][0] for error in errors if error['type'] == 'missing']
        assert 'id' in missing_fields
        assert 'category_type' in missing_fields
    
    def test_category_opportunity_with_required_fields(self):
        """Test that CategoryOpportunity works with all required fields"""
        
        valid_data = {
            'id': 1,
            'opportunity': 'Test Opportunity',
            'current_gap': 'Test gap',
            'recommendation': 'Test recommendation',
            'implementation': 'Test implementation',
            'timeline': 'Test timeline',
            'investment': 'Test investment',
            'category_type': 'test'
        }
        
        # This should work
        opp = CategoryOpportunity(**valid_data)
        assert opp.id == 1
        assert opp.category_type == 'test'
        assert opp.opportunity == 'Test Opportunity'
    
    def test_category_opportunity_round_trip_conversion(self):
        """Test that CategoryOpportunity can be converted to dict and back"""
        
        original_data = {
            'id': 2,
            'opportunity': 'Round Trip Test',
            'current_gap': 'Test gap',
            'recommendation': 'Test recommendation',
            'implementation': 'Test implementation',
            'timeline': 'Test timeline',
            'investment': 'Test investment',
            'category_type': 'test'
        }
        
        # Create -> Convert to dict -> Recreate
        original_opp = CategoryOpportunity(**original_data)
        opp_dict = original_opp.model_dump()
        recreated_opp = CategoryOpportunity(**opp_dict)
        
        # Verify they match
        assert recreated_opp.id == original_opp.id
        assert recreated_opp.category_type == original_opp.category_type
        assert recreated_opp.opportunity == original_opp.opportunity
    
    def test_pipeline_helper_methods_create_valid_objects(self):
        """Test that all pipeline helper methods create valid CategoryOpportunity objects"""
        
        pipeline = OpportunityIntelligenceGraph()
        competitors = ["Test Competitor 1", "Test Competitor 2"]
        device_category = "test_category"
        
        # Test all helper methods
        helper_methods = [
            pipeline._generate_brand_opportunities,
            pipeline._generate_product_opportunities,
            pipeline._generate_pricing_opportunities,
            pipeline._generate_market_opportunities
        ]
        
        for method in helper_methods:
            opportunities = method(competitors, device_category)
            assert len(opportunities) > 0, f"{method.__name__} should generate opportunities"
            
            for opp in opportunities:
                assert isinstance(opp, CategoryOpportunity)
                assert opp.id is not None
                assert opp.category_type is not None
                
                # Test round-trip conversion
                opp_dict = opp.model_dump()
                recreated_opp = CategoryOpportunity(**opp_dict)
                assert recreated_opp.id == opp.id
                assert recreated_opp.category_type == opp.category_type
    
    def test_categorize_opportunities_method(self):
        """Test the categorize_opportunities method creates valid objects"""
        
        pipeline = OpportunityIntelligenceGraph()
        
        mock_state = {
            "all_opportunities": [
                {
                    "title": "Test Opportunity",
                    "category": "Product Innovation",
                    "description": "Test description",
                    "next_steps": ["Step 1", "Step 2"],
                    "time_to_market": "12 months",
                    "investment_level": "Medium"
                }
            ],
            "competitors": ["Test Competitor"],
            "device_category": "test_category"
        }
        
        result_state = pipeline.categorize_opportunities(mock_state)
        
        # Verify all opportunity categories exist and contain valid data
        for category_key in ["brand_opportunities", "product_opportunities", 
                           "pricing_opportunities", "market_expansion_opportunities"]:
            assert category_key in result_state
            opportunities = result_state[category_key]
            
            for opp_dict in opportunities:
                # This is the critical test - can we recreate CategoryOpportunity?
                recreated_opp = CategoryOpportunity(**opp_dict)
                assert recreated_opp.id is not None
                assert recreated_opp.category_type is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 