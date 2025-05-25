#!/usr/bin/env python3
"""
Test script for Phase 1: Data Model Enhancement
"""

from data_models import CategoryRouter, DEVICE_CATEGORIES, SearchTemplates

def test_category_detection():
    """Test CategoryRouter functionality"""
    print("🧪 Testing CategoryRouter...")
    
    test_cases = [
        (["Medtronic", "Abbott"], "stent", "cardiovascular"),
        (["Stryker Spine"], "spine fusion", "spine_fusion"),
        (["Zimmer Biomet"], "hip replacement", "joint_replacement"),
        (["Dexcom"], "glucose monitoring", "diabetes_care"),
        (["Unknown Company"], "", "spine_fusion"),  # Should fallback
        (["Abbott"], "", "cardiovascular"),  # Abbott is in multiple categories, should pick highest score
    ]
    
    passed = 0
    for competitors, context, expected in test_cases:
        result = CategoryRouter.detect_category(competitors, context)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {competitors} + '{context}' → {result} (expected: {expected})")
        if result == expected:
            passed += 1
    
    print(f"Category detection: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)

def test_enhanced_search_templates():
    """Test enhanced SearchTemplates functionality"""
    print("\n🔍 Testing enhanced SearchTemplates...")
    
    # Test cardiovascular queries
    cardio_queries = SearchTemplates.get_competitor_queries("Medtronic", "cardiovascular", "cardiovascular")
    print(f"  ✅ Cardiovascular queries: {len(cardio_queries)} generated")
    print(f"     Sample: {cardio_queries[0]}")
    
    # Test spine queries (should work with new and old interface)
    spine_queries_new = SearchTemplates.get_competitor_queries("Stryker Spine", "spine_fusion", "spine_fusion")
    spine_queries_old = SearchTemplates.get_competitor_queries("Stryker Spine", "spine_fusion")  # Legacy interface
    
    print(f"  ✅ Spine queries (new): {len(spine_queries_new)} generated")
    print(f"  ✅ Spine queries (old): {len(spine_queries_old)} generated")
    print(f"     Sample new: {spine_queries_new[0]}")
    print(f"     Sample old: {spine_queries_old[0]}")
    
    # Test market queries
    market_queries = SearchTemplates.get_market_queries("cardiovascular", "cardiovascular")
    print(f"  ✅ Market queries: {len(market_queries)} generated")
    print(f"     Sample: {market_queries[0]}")
    
    return True

def test_backward_compatibility():
    """Test that existing functionality still works"""
    print("\n🔒 Testing backward compatibility...")
    
    # Test old interface still works
    try:
        old_queries = SearchTemplates.get_competitor_queries("Stryker Spine", "spine_fusion")
        old_market = SearchTemplates.get_market_queries("spine_fusion")
        
        assert len(old_queries) > 0, "Old competitor queries should work"
        assert len(old_market) > 0, "Old market queries should work"
        
        print("  ✅ Legacy SearchTemplates interface works")
        return True
    except Exception as e:
        print(f"  ❌ Backward compatibility failed: {e}")
        return False

def test_device_categories_config():
    """Test DEVICE_CATEGORIES configuration"""
    print("\n📋 Testing DEVICE_CATEGORIES configuration...")
    
    required_categories = ["cardiovascular", "spine_fusion", "joint_replacement", "diabetes_care"]
    
    for category in required_categories:
        assert category in DEVICE_CATEGORIES, f"Missing category: {category}"
        config = DEVICE_CATEGORIES[category]
        assert "competitors" in config, f"Missing competitors for {category}"
        assert "keywords" in config, f"Missing keywords for {category}"
        assert len(config["competitors"]) > 0, f"No competitors for {category}"
        assert len(config["keywords"]) > 0, f"No keywords for {category}"
    
    print(f"  ✅ All {len(required_categories)} categories properly configured")
    return True

def main():
    """Run all Phase 1 tests"""
    print("🚀 PHASE 1 VALIDATION: Data Model Enhancement")
    print("=" * 60)
    
    tests = [
        ("Category Detection", test_category_detection),
        ("Enhanced Search Templates", test_enhanced_search_templates),
        ("Backward Compatibility", test_backward_compatibility),
        ("Device Categories Config", test_device_categories_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"PHASE 1 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ PHASE 1 COMPLETE - Data models enhanced successfully!")
        print("🎯 Ready for Phase 2: LangGraph Pipeline Integration")
        return True
    else:
        print("❌ PHASE 1 INCOMPLETE - Fix issues before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 