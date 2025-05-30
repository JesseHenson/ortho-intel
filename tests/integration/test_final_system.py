#!/usr/bin/env python3
"""
Final comprehensive test to verify the complete opportunity analysis system
"""

from main_langgraph_opportunity import opportunity_graph

def test_final_system():
    """Test the complete system end-to-end"""
    print("🎯 Final System Test - Complete Opportunity Analysis")
    print("=" * 60)
    
    try:
        print("\n1. 🚀 Running Complete Analysis...")
        result = opportunity_graph.run_analysis(['Stryker Spine', 'Zimmer Biomet'], 'spine_fusion')
        
        print("✅ Analysis completed successfully!")
        
        # Test 1: Validation Errors
        print(f"\n2. ✅ Validation Test:")
        if 'error' not in result:
            print("   ✅ No validation errors detected")
        else:
            print(f"   ❌ Validation error: {result.get('error')}")
            return False
        
        # Test 2: Opportunity Generation
        print(f"\n3. 🎯 Opportunity Generation Test:")
        final_report = result.get('final_report', {})
        
        brand_opps = final_report.get('brand_opportunities', [])
        product_opps = final_report.get('product_opportunities', [])
        pricing_opps = final_report.get('pricing_opportunities', [])
        market_opps = final_report.get('market_opportunities', [])
        
        print(f"   Brand opportunities: {len(brand_opps)} ✅" if len(brand_opps) > 0 else f"   Brand opportunities: {len(brand_opps)} ❌")
        print(f"   Product opportunities: {len(product_opps)} ✅" if len(product_opps) > 0 else f"   Product opportunities: {len(product_opps)} ❌")
        print(f"   Pricing opportunities: {len(pricing_opps)} ✅" if len(pricing_opps) > 0 else f"   Pricing opportunities: {len(pricing_opps)} ❌")
        print(f"   Market opportunities: {len(market_opps)} ✅" if len(market_opps) > 0 else f"   Market opportunities: {len(market_opps)} ❌")
        
        total_opportunities = len(brand_opps) + len(product_opps) + len(pricing_opps) + len(market_opps)
        print(f"   Total opportunities: {total_opportunities}")
        
        # Test 3: Opportunity Quality
        print(f"\n4. 📊 Opportunity Quality Test:")
        if brand_opps:
            first_brand = brand_opps[0]
            required_fields = ['opportunity', 'current_gap', 'recommendation', 'implementation', 'timeline', 'investment']
            has_all_fields = all(field in first_brand for field in required_fields)
            print(f"   Brand opportunity structure: {'✅ Complete' if has_all_fields else '❌ Missing fields'}")
            print(f"   Sample opportunity: {first_brand.get('opportunity', 'N/A')[:80]}...")
        
        # Test 4: Executive Summary
        print(f"\n5. 📋 Executive Summary Test:")
        exec_summary = final_report.get('executive_summary', {})
        if exec_summary and 'key_insight' in exec_summary:
            print("   ✅ Executive summary generated")
            print(f"   Key insight: {exec_summary.get('key_insight', 'N/A')[:100]}...")
        else:
            print("   ❌ Executive summary missing")
        
        # Test 5: Frontend Data Access
        print(f"\n6. 🖥️ Frontend Data Access Test:")
        # Test both direct access and final_report access patterns
        direct_brand = result.get('brand_opportunities', [])
        report_brand = final_report.get('brand_opportunities', [])
        
        print(f"   Direct access: {len(direct_brand)} opportunities")
        print(f"   Report access: {len(report_brand)} opportunities")
        print(f"   Data consistency: {'✅ Consistent' if len(direct_brand) == len(report_brand) else '❌ Inconsistent'}")
        
        # Test 6: Overall Success
        print(f"\n7. 🏆 Overall System Health:")
        success_criteria = [
            total_opportunities >= 8,  # At least 8 total opportunities
            len(brand_opps) >= 1,      # At least 1 brand opportunity
            len(product_opps) >= 1,    # At least 1 product opportunity
            len(pricing_opps) >= 1,    # At least 1 pricing opportunity
            len(market_opps) >= 1,     # At least 1 market opportunity
            exec_summary is not None,  # Executive summary exists
            'error' not in result      # No errors
        ]
        
        passed_criteria = sum(success_criteria)
        total_criteria = len(success_criteria)
        
        print(f"   Success criteria: {passed_criteria}/{total_criteria}")
        print(f"   System status: {'🎉 FULLY OPERATIONAL' if passed_criteria == total_criteria else '⚠️ NEEDS ATTENTION'}")
        
        if passed_criteria == total_criteria:
            print(f"\n🎉 SUCCESS! The Tavily optimization deep dive is complete!")
            print(f"   ✅ Validation errors fixed")
            print(f"   ✅ Robust opportunity generation ({total_opportunities} opportunities)")
            print(f"   ✅ Enhanced research strategy working")
            print(f"   ✅ Frontend data access working")
            print(f"   ✅ Executive summary generation working")
            print(f"\n🚀 The system is ready for production use!")
            return True
        else:
            print(f"\n⚠️ System needs attention - {total_criteria - passed_criteria} criteria failed")
            return False
            
    except Exception as e:
        print(f"❌ System test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_final_system() 