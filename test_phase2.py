#!/usr/bin/env python3
"""
Test script for Phase 2: LangGraph Pipeline Integration
"""

from main_langgraph import OrthopedicIntelligenceGraph
from data_models import CategoryRouter

def test_cardiovascular_pipeline():
    """Test the pipeline with cardiovascular competitors"""
    print("🧪 Testing cardiovascular pipeline...")
    
    # Create graph instance
    graph = OrthopedicIntelligenceGraph()
    
    # Test cardiovascular competitors
    competitors = ["Medtronic", "Abbott"]
    focus_area = "stent clinical trials"
    
    # Test just the category detection and initialization
    initial_state = {
        "competitors": competitors,
        "focus_area": focus_area,
        "device_category": "",
        "search_queries": [],
        "raw_research_results": [],
        "clinical_gaps": [],
        "market_opportunities": [],
        "final_report": None,
        "current_competitor": None,
        "research_iteration": 0,
        "error_messages": []
    }
    
    try:
        # Test category detection node
        print("  Testing category detection...")
        result = graph.detect_category(initial_state)
        detected_category = result.update["device_category"]
        
        assert detected_category == "cardiovascular", f"Expected cardiovascular, got {detected_category}"
        print(f"  ✅ Category detected: {detected_category}")
        
        # Test initialize with detected category
        print("  Testing initialization with detected category...")
        state_with_category = {**initial_state, "device_category": detected_category}
        init_result = graph.initialize_research(state_with_category)
        
        queries = init_result.update["search_queries"]
        assert len(queries) > 0, "No search queries generated"
        
        # Check that queries are cardiovascular-specific
        query_text = " ".join(queries).lower()
        cardio_keywords = ["stent", "heart", "valve", "cardiovascular", "cardiac"]
        has_cardio_keywords = any(keyword in query_text for keyword in cardio_keywords)
        
        assert has_cardio_keywords, f"Queries don't contain cardiovascular keywords: {queries}"
        print(f"  ✅ Generated {len(queries)} cardiovascular-specific queries")
        print(f"     Sample: {queries[0]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Cardiovascular pipeline test failed: {e}")
        return False

def test_spine_pipeline_compatibility():
    """Test that spine fusion pipeline still works (backward compatibility)"""
    print("\n🔒 Testing spine fusion pipeline compatibility...")
    
    # Create graph instance
    graph = OrthopedicIntelligenceGraph()
    
    # Test spine competitors
    competitors = ["Stryker Spine", "Zimmer Biomet"]
    focus_area = "spine_fusion"
    
    initial_state = {
        "competitors": competitors,
        "focus_area": focus_area,
        "device_category": "",
        "search_queries": [],
        "raw_research_results": [],
        "clinical_gaps": [],
        "market_opportunities": [],
        "final_report": None,
        "current_competitor": None,
        "research_iteration": 0,
        "error_messages": []
    }
    
    try:
        # Test category detection
        result = graph.detect_category(initial_state)
        detected_category = result.update["device_category"]
        
        assert detected_category == "spine_fusion", f"Expected spine_fusion, got {detected_category}"
        print(f"  ✅ Category detected: {detected_category}")
        
        # Test initialization
        state_with_category = {**initial_state, "device_category": detected_category}
        init_result = graph.initialize_research(state_with_category)
        
        queries = init_result.update["search_queries"]
        assert len(queries) > 0, "No search queries generated"
        
        # Check that queries contain spine-related terms
        query_text = " ".join(queries).lower()
        spine_keywords = ["spine", "fusion", "vertebral", "spinal"]
        has_spine_keywords = any(keyword in query_text for keyword in spine_keywords)
        
        assert has_spine_keywords, f"Queries don't contain spine keywords: {queries}"
        print(f"  ✅ Generated {len(queries)} spine-specific queries")
        print(f"     Sample: {queries[0]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Spine pipeline compatibility test failed: {e}")
        return False

def test_joint_replacement_pipeline():
    """Test joint replacement category detection and pipeline"""
    print("\n🦴 Testing joint replacement pipeline...")
    
    # Create graph instance
    graph = OrthopedicIntelligenceGraph()
    
    # Test joint replacement competitors
    competitors = ["Stryker Ortho", "Smith+Nephew"]
    focus_area = "hip replacement"
    
    initial_state = {
        "competitors": competitors,
        "focus_area": focus_area,
        "device_category": "",
        "search_queries": [],
        "raw_research_results": [],
        "clinical_gaps": [],
        "market_opportunities": [],
        "final_report": None,
        "current_competitor": None,
        "research_iteration": 0,
        "error_messages": []
    }
    
    try:
        # Test category detection
        result = graph.detect_category(initial_state)
        detected_category = result.update["device_category"]
        
        assert detected_category == "joint_replacement", f"Expected joint_replacement, got {detected_category}"
        print(f"  ✅ Category detected: {detected_category}")
        
        # Test initialization
        state_with_category = {**initial_state, "device_category": detected_category}
        init_result = graph.initialize_research(state_with_category)
        
        queries = init_result.update["search_queries"]
        assert len(queries) > 0, "No search queries generated"
        
        # Check that queries contain joint-related terms
        query_text = " ".join(queries).lower()
        joint_keywords = ["hip", "knee", "replacement", "arthroplasty", "joint"]
        has_joint_keywords = any(keyword in query_text for keyword in joint_keywords)
        
        assert has_joint_keywords, f"Queries don't contain joint keywords: {queries}"
        print(f"  ✅ Generated {len(queries)} joint replacement-specific queries")
        print(f"     Sample: {queries[0]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Joint replacement pipeline test failed: {e}")
        return False

def test_pipeline_error_handling():
    """Test pipeline error handling with unknown competitors"""
    print("\n⚠️ Testing pipeline error handling...")
    
    # Create graph instance
    graph = OrthopedicIntelligenceGraph()
    
    # Test unknown competitors (should fallback to spine_fusion)
    competitors = ["Unknown Company", "Another Unknown"]
    focus_area = ""
    
    initial_state = {
        "competitors": competitors,
        "focus_area": focus_area,
        "device_category": "",
        "search_queries": [],
        "raw_research_results": [],
        "clinical_gaps": [],
        "market_opportunities": [],
        "final_report": None,
        "current_competitor": None,
        "research_iteration": 0,
        "error_messages": []
    }
    
    try:
        # Test category detection fallback
        result = graph.detect_category(initial_state)
        detected_category = result.update["device_category"]
        
        assert detected_category == "spine_fusion", f"Expected fallback to spine_fusion, got {detected_category}"
        print(f"  ✅ Fallback category: {detected_category}")
        
        # Test that initialization still works
        state_with_category = {**initial_state, "device_category": detected_category}
        init_result = graph.initialize_research(state_with_category)
        
        queries = init_result.update["search_queries"]
        assert len(queries) > 0, "No search queries generated"
        print(f"  ✅ Generated {len(queries)} fallback queries")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        return False

def main():
    """Run all Phase 2 tests"""
    print("🚀 PHASE 2 VALIDATION: LangGraph Pipeline Integration")
    print("=" * 70)
    
    tests = [
        ("Cardiovascular Pipeline", test_cardiovascular_pipeline),
        ("Spine Pipeline Compatibility", test_spine_pipeline_compatibility),
        ("Joint Replacement Pipeline", test_joint_replacement_pipeline),
        ("Pipeline Error Handling", test_pipeline_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
    
    print("\n" + "=" * 70)
    print(f"PHASE 2 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ PHASE 2 COMPLETE - LangGraph pipeline enhanced successfully!")
        print("🎯 Multi-category analysis pipeline ready")
        print("🎯 Ready for Phase 3: Frontend Integration")
        return True
    else:
        print("❌ PHASE 2 INCOMPLETE - Fix issues before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 