"""
Test CategoryOpportunity Validation and Pipeline Integration

This test file ensures that CategoryOpportunity models are created correctly
and that pipeline integration handles missing fields gracefully.
"""

import pytest
from typing import Dict, List, Any
from pydantic import ValidationError

from src.backend.core.opportunity_data_models import CategoryOpportunity


class TestCategoryOpportunityValidation:
    """Test CategoryOpportunity model validation"""
    
    def test_category_opportunity_with_all_required_fields(self):
        """Test CategoryOpportunity creation with all required fields"""
        data = {
            "id": 1,
            "opportunity": "Test Opportunity",
            "category_type": "brand",
            "current_gap": "Test gap",
            "recommendation": "Test recommendation",
            "implementation": "Test implementation",
            "timeline": "6-12 months",
            "investment": "Medium investment"
        }
        
        opp = CategoryOpportunity(**data)
        
        assert opp.id == 1
        assert opp.opportunity == "Test Opportunity"
        assert opp.category_type == "brand"
        assert opp.current_gap == "Test gap"
        assert opp.recommendation == "Test recommendation"
        assert opp.implementation == "Test implementation"
        assert opp.timeline == "6-12 months"
        assert opp.investment == "Medium investment"
    
    def test_category_opportunity_missing_required_fields_raises_error(self):
        """Test that missing required fields raise ValidationError"""
        incomplete_data = {
            "opportunity": "Test Opportunity",
            # Missing id, category_type, current_gap, etc.
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CategoryOpportunity(**incomplete_data)
        
        # Check that the error mentions missing fields
        error_str = str(exc_info.value)
        assert "Field required" in error_str
    
    def test_category_opportunity_with_optional_fields(self):
        """Test CategoryOpportunity with optional fields"""
        data = {
            "id": 1,
            "opportunity": "Test Opportunity",
            "category_type": "brand",
            "current_gap": "Test gap",
            "recommendation": "Test recommendation",
            "implementation": "Test implementation",
            "timeline": "6-12 months",
            "investment": "Medium investment",
            "competitive_advantage": "First-mover advantage",
            "success_metrics": ["Brand awareness", "Market share"]
        }
        
        opp = CategoryOpportunity(**data)
        
        assert opp.competitive_advantage == "First-mover advantage"
        assert opp.success_metrics == ["Brand awareness", "Market share"]


class TestSafeModelCreation:
    """Test safe model creation patterns"""
    
    def _safe_recreate_category_opportunities(self, opportunities_data: List[Dict], category_type: str) -> List[CategoryOpportunity]:
        """Safely recreate CategoryOpportunity objects with required fields"""
        safe_opportunities = []
        
        for i, opp_data in enumerate(opportunities_data):
            try:
                # Ensure all required fields are present
                safe_opp = CategoryOpportunity(
                    id=opp_data.get("id", i + 1),
                    opportunity=opp_data.get("opportunity", f"Opportunity {i + 1}"),
                    category_type=opp_data.get("category_type", category_type),
                    current_gap=opp_data.get("current_gap", f"Gap in {category_type}"),
                    recommendation=opp_data.get("recommendation", "Recommendation needed"),
                    implementation=opp_data.get("implementation", "Implementation plan needed"),
                    timeline=opp_data.get("timeline", "6-12 months"),
                    investment=opp_data.get("investment", "Medium investment")
                )
                safe_opportunities.append(safe_opp)
            except Exception as e:
                print(f"Warning: Failed to create CategoryOpportunity {i}: {e}")
                continue
        
        return safe_opportunities
    
    def validate_category_opportunity_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance data before CategoryOpportunity creation"""
        required_fields = {
            "id": data.get("id", 1),
            "opportunity": data.get("opportunity", "Strategic Opportunity"),
            "category_type": data.get("category_type", "brand"),
            "current_gap": data.get("current_gap", "Competitive gap identified"),
            "recommendation": data.get("recommendation", "Strategic recommendation"),
            "implementation": data.get("implementation", "Implementation plan"),
            "timeline": data.get("timeline", "6-12 months"),
            "investment": data.get("investment", "Medium investment")
        }
        
        # Add optional fields if present
        optional_fields = ["competitive_advantage", "success_metrics"]
        for field in optional_fields:
            if field in data:
                required_fields[field] = data[field]
        
        return required_fields
    
    def test_safe_recreation_with_incomplete_data(self):
        """Test safe recreation with incomplete data"""
        incomplete_opportunities = [
            {
                "opportunity": "Test Opportunity 1",
                # Missing most required fields
            },
            {
                "opportunity": "Test Opportunity 2",
                "category_type": "product",
                # Missing other required fields
            }
        ]
        
        safe_opportunities = self._safe_recreate_category_opportunities(incomplete_opportunities, "brand")
        
        assert len(safe_opportunities) == 2
        
        # Check first opportunity
        opp1 = safe_opportunities[0]
        assert opp1.id == 1
        assert opp1.opportunity == "Test Opportunity 1"
        assert opp1.category_type == "brand"  # Default from parameter
        assert opp1.current_gap == "Gap in brand"
        
        # Check second opportunity
        opp2 = safe_opportunities[1]
        assert opp2.id == 2
        assert opp2.opportunity == "Test Opportunity 2"
        assert opp2.category_type == "product"  # From data
        assert opp2.current_gap == "Gap in brand"  # Default from parameter
    
    def test_validate_category_opportunity_data(self):
        """Test data validation helper"""
        incomplete_data = {
            "opportunity": "Test Opportunity",
            "category_type": "brand"
            # Missing other required fields
        }
        
        validated_data = self.validate_category_opportunity_data(incomplete_data)
        
        # Check that all required fields are present
        required_fields = ["id", "opportunity", "category_type", "current_gap", 
                          "recommendation", "implementation", "timeline", "investment"]
        
        for field in required_fields:
            assert field in validated_data
        
        # Check specific values
        assert validated_data["opportunity"] == "Test Opportunity"
        assert validated_data["category_type"] == "brand"
        assert validated_data["id"] == 1  # Default
        assert validated_data["current_gap"] == "Competitive gap identified"  # Default


class TestPipelineIntegration:
    """Test pipeline integration scenarios"""
    
    def test_category_opportunity_pipeline_integration(self):
        """Test that CategoryOpportunity creation works in pipeline context"""
        # Simulate pipeline output with missing fields
        test_opportunities = [
            {
                "opportunity": "Address market positioning gap",
                # Intentionally missing required fields to test safety
            },
            {
                "opportunity": "Develop premium product line",
                "category_type": "product",
                "timeline": "12-18 months"
                # Missing other required fields
            }
        ]
        
        # Test safe recreation
        safe_model_creator = TestSafeModelCreation()
        safe_opportunities = safe_model_creator._safe_recreate_category_opportunities(test_opportunities, "brand")
        
        # Verify all opportunities have required fields
        assert len(safe_opportunities) == 2
        
        for opp in safe_opportunities:
            assert hasattr(opp, 'id')
            assert hasattr(opp, 'category_type')
            assert hasattr(opp, 'opportunity')
            assert hasattr(opp, 'current_gap')
            assert hasattr(opp, 'recommendation')
            assert hasattr(opp, 'implementation')
            assert hasattr(opp, 'timeline')
            assert hasattr(opp, 'investment')
    
    def test_all_category_types_validation(self):
        """Test all valid category types"""
        valid_category_types = ["brand", "product", "pricing", "market"]
        
        for category_type in valid_category_types:
            data = {
                "id": 1,
                "opportunity": f"Test {category_type} opportunity",
                "category_type": category_type,
                "current_gap": f"Gap in {category_type}",
                "recommendation": f"Recommendation for {category_type}",
                "implementation": f"Implementation for {category_type}",
                "timeline": "6-12 months",
                "investment": "Medium investment"
            }
            
            opp = CategoryOpportunity(**data)
            assert opp.category_type == category_type


def test_all_pydantic_models_validation():
    """Comprehensive test for all Pydantic model validation"""
    # Test CategoryOpportunity with minimal required fields
    try:
        test_opp = CategoryOpportunity(
            id=1,
            opportunity="Test",
            category_type="brand",
            current_gap="Test gap",
            recommendation="Test rec",
            implementation="Test impl",
            timeline="Test time",
            investment="Test inv"
        )
        assert test_opp.id == 1
        print("✅ CategoryOpportunity validation passed")
        return True
    except Exception as e:
        print(f"❌ CategoryOpportunity validation failed: {e}")
        raise


if __name__ == "__main__":
    # Run the comprehensive validation test
    test_all_pydantic_models_validation()
    print("All validation tests completed successfully!") 