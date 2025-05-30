#!/usr/bin/env python3
"""
Test script to verify the enhanced opportunity analysis system
"""

from main_langgraph_opportunity import opportunity_graph

def test_enhanced_system():
    """Test the enhanced opportunity analysis system"""
    print("🧪 Testing Enhanced Opportunity Analysis System")
    print("=" * 60)
    
    try:
        print("\n1. 🚀 Starting analysis with enhanced backend...")
        result = opportunity_graph.run_analysis(['Stryker Spine', 'Zimmer Biomet'], 'spine_fusion')
        
        print("✅ Analysis completed successfully!")
        print(f"📊 Result keys: {list(result.keys())}")
        
        if 'final_report' in result and result['final_report']:
            report = result['final_report']
            print(f"\n2. 📈 Opportunity Analysis Results:")
            print(f"   Brand opportunities: {len(report.get('brand_opportunities', []))}")
            print(f"   Product opportunities: {len(report.get('product_opportunities', []))}")
            print(f"   Pricing opportunities: {len(report.get('pricing_opportunities', []))}")
            print(f"   Market opportunities: {len(report.get('market_opportunities', []))}")
            
            # Check for enhanced opportunity details
            brand_opps = report.get('brand_opportunities', [])
            if brand_opps:
                first_opp = brand_opps[0]
                print(f"\n3. 🔍 Sample Brand Opportunity:")
                print(f"   Title: {first_opp.get('opportunity', 'N/A')}")
                print(f"   Gap: {first_opp.get('current_gap', 'N/A')[:100]}...")
                print(f"   Investment: {first_opp.get('investment', 'N/A')}")
                print(f"   Timeline: {first_opp.get('timeline', 'N/A')}")
                
                # Check for enhanced fields
                if 'competitive_advantage' in first_opp:
                    print(f"   ✅ Enhanced fields present (competitive_advantage, success_metrics)")
                else:
                    print(f"   ⚠️ Enhanced fields missing")
            
            print(f"\n4. 🎯 Quality Assessment:")
            total_opportunities = (
                len(report.get('brand_opportunities', [])) +
                len(report.get('product_opportunities', [])) +
                len(report.get('pricing_opportunities', [])) +
                len(report.get('market_opportunities', []))
            )
            print(f"   Total opportunities generated: {total_opportunities}")
            
            if total_opportunities >= 8:
                print(f"   ✅ Quality target met (8+ opportunities)")
            else:
                print(f"   ⚠️ Quality target not met (need 8+, got {total_opportunities})")
                
        else:
            print("❌ No final report generated")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n🎉 Enhanced system test completed successfully!")
    return True

if __name__ == "__main__":
    test_enhanced_system() 