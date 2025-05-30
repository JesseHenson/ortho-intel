#!/usr/bin/env python3
"""
Test the opportunity analysis system with cardiovascular medical device companies
"""

from main_langgraph_opportunity import opportunity_graph

def test_cardiovascular_system():
    """Test the system with cardiovascular device manufacturers"""
    print("🫀 Cardiovascular Device Competitive Intelligence Test")
    print("=" * 60)
    
    # Cardiovascular device competitors
    cardiovascular_competitors = [
        "Medtronic Cardiovascular", 
        "Abbott Vascular", 
        "Boston Scientific"
    ]
    
    # Focus area for cardiovascular
    focus_area = "coronary_stents"
    
    try:
        print(f"\n1. 🚀 Testing with Cardiovascular Companies...")
        print(f"   Client: Edwards Lifesciences (hypothetical)")
        print(f"   Competitors: {cardiovascular_competitors}")
        print(f"   Focus area: {focus_area}")
        
        result = opportunity_graph.run_analysis(cardiovascular_competitors, focus_area)
        
        print("✅ Analysis completed successfully!")
        
        # Check for validation errors
        if 'error' in result:
            print(f"❌ Validation error detected: {result['error']}")
            return False
        
        # Check opportunity generation
        final_report = result.get('final_report', {})
        if final_report:
            brand_opps = final_report.get('brand_opportunities', [])
            product_opps = final_report.get('product_opportunities', [])
            pricing_opps = final_report.get('pricing_opportunities', [])
            market_opps = final_report.get('market_opportunities', [])
            
            total_opportunities = len(brand_opps) + len(product_opps) + len(pricing_opps) + len(market_opps)
            
            print(f"\n2. 📊 Cardiovascular Opportunity Results:")
            print(f"   Brand opportunities: {len(brand_opps)}")
            print(f"   Product opportunities: {len(product_opps)}")
            print(f"   Pricing opportunities: {len(pricing_opps)}")
            print(f"   Market opportunities: {len(market_opps)}")
            print(f"   Total opportunities: {total_opportunities}")
            
            # Show sample opportunities
            if brand_opps:
                print(f"\n3. 🎯 Sample Brand Opportunity:")
                sample = brand_opps[0]
                print(f"   Title: {sample.get('opportunity', 'N/A')}")
                print(f"   Gap: {sample.get('current_gap', 'N/A')[:100]}...")
                print(f"   Recommendation: {sample.get('recommendation', 'N/A')[:100]}...")
            
            if product_opps:
                print(f"\n4. 🔬 Sample Product Opportunity:")
                sample = product_opps[0]
                print(f"   Title: {sample.get('opportunity', 'N/A')}")
                print(f"   Gap: {sample.get('current_gap', 'N/A')[:100]}...")
                print(f"   Timeline: {sample.get('timeline', 'N/A')}")
                print(f"   Investment: {sample.get('investment', 'N/A')}")
            
            # Check executive summary
            exec_summary = final_report.get('executive_summary', {})
            if exec_summary:
                print(f"\n5. 📋 Executive Summary:")
                print(f"   Key insight: {exec_summary.get('key_insight', 'N/A')[:150]}...")
                print(f"   Strategic focus: {exec_summary.get('strategic_focus', 'N/A')}")
            
            # Success criteria
            success = (
                total_opportunities >= 4 and
                len(brand_opps) >= 1 and
                len(product_opps) >= 1 and
                exec_summary is not None
            )
            
            print(f"\n6. 🏆 Test Result: {'✅ SUCCESS' if success else '❌ NEEDS IMPROVEMENT'}")
            
            if success:
                print(f"   🎉 Cardiovascular analysis working perfectly!")
                print(f"   📈 Generated {total_opportunities} opportunities")
                print(f"   🔬 System adapts well to different device categories")
            
            return success
        else:
            print("❌ No final report generated")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_cardiovascular_system() 