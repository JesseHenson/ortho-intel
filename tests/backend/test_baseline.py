#!/usr/bin/env python3
"""
Baseline test to verify core system functionality before multi-category expansion
"""

import os
import sys

def test_imports():
    """Test that all core modules can be imported"""
    try:
        from src.backend.pipelines.main_langgraph import intelligence_graph
        from src.backend.core.data_models import GraphState, SearchTemplates, AnalysisProcessor
        from tests.backend.test_dataset import get_test_request
        print("✅ All core modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_data_models():
    """Test data model functionality"""
    try:
        from src.backend.core.data_models import SearchTemplates
        from tests.backend.test_dataset import get_test_request
        
        test_req = get_test_request()
        queries = SearchTemplates.get_competitor_queries(
            test_req.competitors[0], 
            test_req.focus_area
        )
        
        assert len(queries) > 0, "No search queries generated"
        print(f"✅ Data models working - generated {len(queries)} queries")
        return True
    except Exception as e:
        print(f"❌ Data model test failed: {e}")
        return False

def test_graph_initialization():
    """Test LangGraph initialization"""
    try:
        from src.backend.pipelines.main_langgraph import intelligence_graph
        
        # Just test that the graph exists and has the expected structure
        assert intelligence_graph is not None, "Intelligence graph not initialized"
        assert hasattr(intelligence_graph, 'graph'), "Graph object missing"
        
        print("✅ LangGraph initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Graph initialization failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    try:
        required_vars = ['TAVILY_API_KEY', 'OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Missing environment variables: {missing_vars}")
            print("   (This will prevent full analysis but core system can be tested)")
        else:
            print("✅ All environment variables configured")
        
        return True
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def main():
    """Run baseline tests"""
    print("🧪 BASELINE SYSTEM TEST")
    print("=" * 50)
    print("Testing core system before multi-category expansion...")
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Data Models", test_data_models),
        ("Graph Initialization", test_graph_initialization),
        ("Environment", test_environment)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"BASELINE TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ BASELINE VERIFIED - System ready for multi-category expansion")
        return True
    else:
        print("❌ BASELINE FAILED - Fix issues before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 