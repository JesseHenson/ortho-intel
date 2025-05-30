"""
Comprehensive test suite for opportunity API endpoints.

Tests the new progressive disclosure API endpoints for opportunity details,
ensuring proper data transformation and error handling.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the FastAPI app
from src.backend.api.fastapi_server import app, analysis_cache
from src.backend.core.opportunity_data_models import (
    StrategicOpportunity, OpportunityCategory, ImplementationDifficulty,
    InvestmentLevel, CompetitiveRisk
)

# Create test client
client = TestClient(app)

class TestOpportunityAPIEndpoints:
    """Test suite for opportunity API endpoints"""
    
    def setup_method(self):
        """Set up test data before each test"""
        # Clear cache
        analysis_cache.clear()
        
        # Create mock analysis result
        self.test_analysis_id = "test_analysis_123"
        self.mock_strategic_opportunity = {
            "id": 1,
            "title": "AI-Powered Surgical Planning",
            "category": "Product Innovation",
            "description": "Develop AI-enabled surgical planning platform",
            "opportunity_score": 8.5,
            "implementation_difficulty": "Medium",
            "time_to_market": "12-18 months",
            "investment_level": "High",
            "competitive_risk": "Medium",
            "potential_impact": "Significant competitive advantage",
            "next_steps": [
                "Conduct market research",
                "Develop prototype",
                "Validate with surgeons"
            ],
            "supporting_evidence": "Market research shows 70% of surgeons want AI integration",
            "source_urls": [
                "https://example.com/source1",
                "https://example.com/source2"
            ],
            "confidence_level": 8.0
        }
        
        # Create mock analysis result
        self.mock_analysis_result = {
            "top_opportunities": [self.mock_strategic_opportunity],
            "final_report": {
                "top_opportunities_summary": [
                    {
                        "id": 1,
                        "title": "AI-Powered Surgical Planning",
                        "category": "Product Innovation",
                        "opportunity_score": 8.5,
                        "implementation_difficulty": "Medium",
                        "time_to_market": "12-18 months",
                        "credibility_indicator": "🟢",
                        "source_count_display": "2 sources",
                        "has_detailed_analysis": True,
                        "has_source_analysis": True
                    }
                ],
                "brand_opportunities": [
                    {
                        "id": 1001,
                        "opportunity": "Outcome-Focused Brand Positioning",
                        "current_gap": "Competitors focus on features rather than outcomes",
                        "recommendation": "Position brand around patient outcomes",
                        "implementation": "Develop outcome-focused campaigns",
                        "timeline": "3-6 months",
                        "investment": "Medium ($100K-300K)",
                        "category_type": "brand"
                    }
                ],
                "product_opportunities": [],
                "pricing_opportunities": [],
                "market_opportunities": [],
                "analysis_metadata": {
                    "analysis_id": "test_analysis_123",
                    "analysis_type": "Competitive Intelligence",
                    "started_at": datetime.now().isoformat(),
                    "client_name": "Test Client"
                }
            },
            "raw_research_results": [
                {
                    "url": "https://example.com/source1",
                    "title": "AI in Surgery Research",
                    "content": "Research shows AI benefits..."
                },
                {
                    "url": "https://example.com/source2", 
                    "title": "Surgical Planning Technology",
                    "content": "Technology trends in surgery..."
                }
            ]
        }
        
        # Add to cache
        analysis_cache[self.test_analysis_id] = self.mock_analysis_result
    
    def test_get_opportunities_summary_success(self):
        """Test successful retrieval of opportunity summary"""
        response = client.get(f"/api/opportunities/{self.test_analysis_id}/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["analysis_id"] == self.test_analysis_id
        assert data["detail_level"] == "summary"
        assert data["total_count"] == 1
        assert len(data["opportunities"]) == 1
        
        opportunity = data["opportunities"][0]
        assert opportunity["title"] == "AI-Powered Surgical Planning"
        assert opportunity["credibility_indicator"] == "🟢"
        assert opportunity["source_count_display"] == "2 sources"
    
    def test_get_opportunities_summary_not_found(self):
        """Test summary endpoint with non-existent analysis"""
        response = client.get("/api/opportunities/nonexistent/summary")
        
        assert response.status_code == 404
        assert "Analysis not found" in response.json()["detail"]
    
    def test_get_opportunities_details_success(self):
        """Test successful retrieval of opportunity details"""
        response = client.get(f"/api/opportunities/{self.test_analysis_id}/details")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["analysis_id"] == self.test_analysis_id
        assert data["detail_level"] == "detail"
        assert data["total_count"] == 1
        assert len(data["opportunities"]) == 1
        
        opportunity = data["opportunities"][0]
        assert opportunity["title"] == "AI-Powered Surgical Planning"
        assert "description" in opportunity
        assert "next_steps" in opportunity
    
    def test_get_opportunities_details_with_filter(self):
        """Test opportunity details with ID filter"""
        response = client.get(
            f"/api/opportunities/{self.test_analysis_id}/details?opportunity_ids=1"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_count"] == 1
        assert data["opportunities"][0]["id"] == 1
    
    def test_get_opportunities_details_invalid_filter(self):
        """Test opportunity details with invalid ID filter"""
        response = client.get(
            f"/api/opportunities/{self.test_analysis_id}/details?opportunity_ids=invalid"
        )
        
        assert response.status_code == 400
        assert "Invalid opportunity IDs format" in response.json()["detail"]
    
    def test_get_opportunities_full_analysis_success(self):
        """Test successful retrieval of full opportunity analysis"""
        response = client.get(f"/api/opportunities/{self.test_analysis_id}/analysis")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["analysis_id"] == self.test_analysis_id
        assert data["detail_level"] == "full"
        assert data["includes_source_analysis"] == True
        assert data["total_count"] == 1
        
        opportunity = data["opportunities"][0]
        assert opportunity["title"] == "AI-Powered Surgical Planning"
        assert "detailed_analysis" in opportunity
        assert "Methodology" in opportunity["detailed_analysis"]
    
    def test_get_category_opportunities_success(self):
        """Test successful retrieval of category opportunities"""
        response = client.get(f"/api/opportunities/{self.test_analysis_id}/categories")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["analysis_id"] == self.test_analysis_id
        assert "category_opportunities" in data
        assert "brand" in data["category_opportunities"]
        assert len(data["category_opportunities"]["brand"]) == 1
        
        brand_opp = data["category_opportunities"]["brand"][0]
        assert brand_opp["opportunity"] == "Outcome-Focused Brand Positioning"
    
    def test_get_category_opportunities_filtered(self):
        """Test category opportunities with category filter"""
        response = client.get(
            f"/api/opportunities/{self.test_analysis_id}/categories?category=brand"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["filtered_category"] == "brand"
        assert "brand" in data["category_opportunities"]
        assert "product" not in data["category_opportunities"]
    
    def test_get_opportunity_sources_overall(self):
        """Test retrieval of overall opportunity sources"""
        response = client.get(f"/api/opportunities/{self.test_analysis_id}/sources")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["analysis_id"] == self.test_analysis_id
        assert data["raw_research_count"] == 2
        assert "analysis_metadata" in data
        assert data["analysis_metadata"]["analysis_id"] == self.test_analysis_id
    
    def test_get_opportunity_sources_specific(self):
        """Test retrieval of sources for specific opportunity"""
        response = client.get(
            f"/api/opportunities/{self.test_analysis_id}/sources?opportunity_id=1"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["analysis_id"] == self.test_analysis_id
        assert data["opportunity_id"] == 1
        assert len(data["source_urls"]) == 2
        assert data["confidence_level"] == 8.0
    
    def test_get_opportunity_sources_not_found(self):
        """Test sources endpoint with non-existent opportunity"""
        response = client.get(
            f"/api/opportunities/{self.test_analysis_id}/sources?opportunity_id=999"
        )
        
        assert response.status_code == 404
        assert "Opportunity 999 not found" in response.json()["detail"]
    
    def test_legacy_format_conversion(self):
        """Test that legacy format is properly converted to progressive disclosure"""
        # Create analysis with only legacy format (no final_report)
        legacy_analysis_id = "legacy_test_123"
        legacy_result = {
            "top_opportunities": [self.mock_strategic_opportunity],
            "raw_research_results": []
        }
        analysis_cache[legacy_analysis_id] = legacy_result
        
        # Test summary conversion
        response = client.get(f"/api/opportunities/{legacy_analysis_id}/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["detail_level"] == "summary"
        assert len(data["opportunities"]) == 1
    
    def test_error_handling_malformed_data(self):
        """Test error handling with malformed opportunity data"""
        # Create analysis with malformed opportunity data
        malformed_analysis_id = "malformed_test_123"
        malformed_result = {
            "top_opportunities": [
                {
                    "id": 1,
                    "title": "Test Opportunity"
                    # Missing required fields
                }
            ]
        }
        analysis_cache[malformed_analysis_id] = malformed_result
        
        # Should handle gracefully and return empty results
        response = client.get(f"/api/opportunities/{malformed_analysis_id}/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_count"] == 0  # Should skip malformed opportunities
    
    def test_endpoint_performance_with_large_dataset(self):
        """Test endpoint performance with larger dataset"""
        # Create analysis with multiple opportunities
        large_analysis_id = "large_test_123"
        large_opportunities = []
        
        for i in range(10):
            opp = self.mock_strategic_opportunity.copy()
            opp["id"] = i + 1
            opp["title"] = f"Opportunity {i + 1}"
            large_opportunities.append(opp)
        
        large_result = {
            "top_opportunities": large_opportunities,
            "raw_research_results": []
        }
        analysis_cache[large_analysis_id] = large_result
        
        # Test that all endpoints handle larger datasets
        response = client.get(f"/api/opportunities/{large_analysis_id}/summary")
        assert response.status_code == 200
        assert response.json()["total_count"] == 10
        
        response = client.get(f"/api/opportunities/{large_analysis_id}/details")
        assert response.status_code == 200
        assert response.json()["total_count"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 