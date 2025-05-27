#!/usr/bin/env python3
"""
Test script for enhanced opportunity analysis with client context
"""

from main_langgraph_opportunity_enhanced import enhanced_opportunity_graph

def test_enhanced_analysis():
    """Test the enhanced analysis with client name"""
    print("Testing enhanced opportunity analysis with client context...")
    
    # Test data
    client_name = "MedTech Solutions"
    competitors = ["Stryker Spine", "Zimmer Biomet"]
    focus_area = "spine"
    
    try:
        print(f"\nRunning analysis for client: {client_name}")
        print(f"Competitors: {competitors}")
        print(f"Focus area: {focus_area}")
        
        # Run the enhanced analysis
        result = enhanced_opportunity_graph.run_analysis(
            competitors=competitors,
            focus_area=focus_area,
            client_name=client_name
        )
        
        print("\n✅ Analysis completed successfully!")
        print(f"Result keys: {list(result.keys())}")
        
        # Check if client name appears in the analysis
        if 'executive_summary' in result:
            summary = result['executive_summary']
            if hasattr(summary, 'key_insights') and client_name in str(summary.key_insights):
                print(f"✅ Client name '{client_name}' found in analysis")
            else:
                print(f"⚠️ Client name '{client_name}' not found in analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def test_without_client_name():
    """Test the enhanced analysis without client name (backward compatibility)"""
    print("\nTesting enhanced analysis without client name...")
    
    competitors = ["Stryker Spine", "Zimmer Biomet"]
    focus_area = "spine"
    
    try:
        print(f"Competitors: {competitors}")
        print(f"Focus area: {focus_area}")
        
        # Run the enhanced analysis without client name
        result = enhanced_opportunity_graph.run_analysis(
            competitors=competitors,
            focus_area=focus_area
        )
        
        print("\n✅ Analysis without client name completed successfully!")
        print(f"Result keys: {list(result.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Enhanced Opportunity Analysis")
    print("=" * 50)
    
    # Test with client name
    test1_passed = test_enhanced_analysis()
    
    # Test without client name (backward compatibility)
    test2_passed = test_without_client_name()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"✅ With client name: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Without client name: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Enhanced backend is ready.")
    else:
        print("\n❌ Some tests failed. Check the errors above.") 