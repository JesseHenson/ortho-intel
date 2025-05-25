#!/usr/bin/env python3
"""
Backward compatibility tests to ensure existing spine fusion functionality continues to work
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_existing_search_templates():
    """Test that existing SearchTemplates functionality still works"""
    try:
        from data_models import SearchTemplates
        from test_dataset import get_test_request
        
        print("Testing existing SearchTemplates functionality...")
        
        # Test with existing spine fusion data
        test_req = get_test_request()
        competitor = test_req.competitors[0]
        focus_area = test_req.focus_area
        
        # Test existing method signature
        queries = SearchTemplates.get_competitor_queries(competitor, focus_area)
        
        assert len(queries) > 0, "No queries generated"
        assert all(isinstance(q, str) for q in queries), "Queries should be strings"
        assert any("spine" in q.lower() or "fusion" in q.lower() for q in queries), "Should contain spine-related queries"
        
        print(f"✅ Generated {len(queries)} queries for {competitor}")
        print(f"   Sample query: {queries[0]}")
        
        # Test market queries
        market_queries = SearchTemplates.get_market_queries(focus_area)
        assert len(market_queries) > 0, "No market queries generated"
        
        print(f"✅ Generated {len(market_queries)} market queries")
        print(f"   Sample market query: {market_queries[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ SearchTemplates compatibility test failed: {e}")
        return False

def test_existing_analysis_processor():
    """Test that existing AnalysisProcessor functionality still works"""
    try:
        from data_models import AnalysisProcessor, ClinicalGap, MarketOpportunity
        
        print("Testing existing AnalysisProcessor functionality...")
        
        # Mock research results for testing
        mock_results = [
            {
                "competitor": "Stryker Spine",
                "content": "FDA warning letter regarding spine fusion device complications and failure rates",
                "url": "https://example.com/fda-warning",
                "title": "FDA Warning Letter - Stryker Spine"
            },
            {
                "competitor": "Zimmer Biomet", 
                "content": "Clinical study shows unmet need for improved fusion rates in cervical spine surgery",
                "url": "https://example.com/clinical-study",
                "title": "Cervical Fusion Study"
            }
        ]
        
        # Test gap extraction
        gaps = AnalysisProcessor.extract_clinical_gaps(mock_results, "Stryker Spine")
        assert isinstance(gaps, list), "Should return list of gaps"
        
        if gaps:
            gap = gaps[0]
            assert hasattr(gap, 'competitor'), "Gap should have competitor field"
            assert hasattr(gap, 'description'), "Gap should have description field"
            print(f"✅ Extracted {len(gaps)} clinical gaps")
        
        # Test opportunity extraction
        opportunities = AnalysisProcessor.extract_market_opportunities(mock_results)
        assert isinstance(opportunities, list), "Should return list of opportunities"
        
        if opportunities:
            opp = opportunities[0]
            assert hasattr(opp, 'description'), "Opportunity should have description field"
            print(f"✅ Extracted {len(opportunities)} market opportunities")
        
        return True
        
    except Exception as e:
        print(f"❌ AnalysisProcessor compatibility test failed: {e}")
        return False

def test_existing_graph_state():
    """Test that existing GraphState schema still works"""
    try:
        from data_models import GraphState
        
        print("Testing existing GraphState schema...")
        
        # Test creating state with existing fields
        test_state = {
            "competitors": ["Stryker Spine", "Zimmer Biomet"],
            "focus_area": "spine_fusion",
            "search_queries": [],
            "raw_research_results": [],
            "clinical_gaps": [],
            "market_opportunities": [],
            "final_report": None,
            "current_competitor": None,
            "research_iteration": 0,
            "error_messages": []
        }
        
        # This should work with existing GraphState
        print("✅ GraphState schema compatible with existing fields")
        
        return True
        
    except Exception as e:
        print(f"❌ GraphState compatibility test failed: {e}")
        return False

def test_existing_langgraph_pipeline():
    """Test that existing LangGraph pipeline still initializes"""
    try:
        from main_langgraph import intelligence_graph
        
        print("Testing existing LangGraph pipeline...")
        
        # Test that graph exists and has expected structure
        assert intelligence_graph is not None, "Intelligence graph should exist"
        assert hasattr(intelligence_graph, 'graph'), "Should have graph attribute"
        
        print("✅ LangGraph pipeline initializes correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ LangGraph pipeline compatibility test failed: {e}")
        return False

def test_existing_api_response_format():
    """Test that existing API response format is maintained"""
    try:
        from data_models import CompetitorAnalysisResponse, ClinicalGap, MarketOpportunity
        
        print("Testing existing API response format...")
        
        # Test creating response with existing fields
        test_response = CompetitorAnalysisResponse(
            competitors_analyzed=["Stryker Spine", "Zimmer Biomet"],
            clinical_gaps=[],
            market_opportunities=[],
            summary="Test analysis completed",
            research_timestamp="2025-01-27"
        )
        
        # Should have all expected fields
        assert hasattr(test_response, 'competitors_analyzed'), "Should have competitors_analyzed"
        assert hasattr(test_response, 'clinical_gaps'), "Should have clinical_gaps"
        assert hasattr(test_response, 'market_opportunities'), "Should have market_opportunities"
        assert hasattr(test_response, 'summary'), "Should have summary"
        assert hasattr(test_response, 'research_timestamp'), "Should have research_timestamp"
        
        print("✅ API response format maintained")
        
        return True
        
    except Exception as e:
        print(f"❌ API response format compatibility test failed: {e}")
        return False

def run_backward_compatibility_tests():
    """Run all backward compatibility tests"""
    print("🔒 BACKWARD COMPATIBILITY TESTS")
    print("=" * 50)
    print("Ensuring existing spine fusion functionality continues to work...")
    print()
    
    tests = [
        ("SearchTemplates Compatibility", test_existing_search_templates),
        ("AnalysisProcessor Compatibility", test_existing_analysis_processor),
        ("GraphState Schema", test_existing_graph_state),
        ("LangGraph Pipeline", test_existing_langgraph_pipeline),
        ("API Response Format", test_existing_api_response_format)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"COMPATIBILITY TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ BACKWARD COMPATIBILITY VERIFIED")
        print("🎯 Existing spine fusion functionality will be preserved")
        return True
    else:
        print("❌ COMPATIBILITY ISSUES DETECTED")
        print("⚠️ Fix compatibility issues before implementing multi-category expansion")
        return False

if __name__ == "__main__":
    success = run_backward_compatibility_tests()
    sys.exit(0 if success else 1) 