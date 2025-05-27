#!/usr/bin/env python3
"""
Comprehensive test showing the opportunity analysis system works across multiple medical device categories
"""

from main_langgraph_opportunity import opportunity_graph

def test_multi_category_system():
    """Test the system across multiple medical device categories"""
    print("🏥 Multi-Category Medical Device Competitive Intelligence Test")
    print("=" * 70)
    
    # Define test scenarios for different medical device categories
    test_scenarios = [
        {
            "category": "Cardiovascular",
            "client": "Edwards Lifesciences",
            "competitors": ["Medtronic Cardiovascular", "Abbott Vascular", "Boston Scientific"],
            "focus_area": "heart_valves"
        },
        {
            "category": "Diabetes Care", 
            "client": "Tandem Diabetes Care",
            "competitors": ["Dexcom", "Abbott Diabetes", "Insulet"],
            "focus_area": "insulin_pumps"
        },
        {
            "category": "Joint Replacement",
            "client": "Wright Medical",
            "competitors": ["Stryker Ortho", "Zimmer Biomet", "Smith+Nephew"],
            "focus_area": "knee_replacement"
        }
    ]
    
    results_summary = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*20} TEST {i}: {scenario['category'].upper()} {'='*20}")
        print(f"Client: {scenario['client']}")
        print(f"Competitors: {scenario['competitors']}")
        print(f"Focus Area: {scenario['focus_area']}")
        
        try:
            # Run analysis
            result = opportunity_graph.run_analysis(scenario['competitors'], scenario['focus_area'])
            
            # Check for errors
            if 'error' in result:
                print(f"❌ {scenario['category']} analysis failed: {result['error']}")
                results_summary.append({
                    "category": scenario['category'],
                    "status": "FAILED",
                    "error": result['error']
                })
                continue
            
            # Extract results
            final_report = result.get('final_report', {})
            if final_report:
                brand_opps = final_report.get('brand_opportunities', [])
                product_opps = final_report.get('product_opportunities', [])
                pricing_opps = final_report.get('pricing_opportunities', [])
                market_opps = final_report.get('market_opportunities', [])
                exec_summary = final_report.get('executive_summary', {})
                
                total_opportunities = len(brand_opps) + len(product_opps) + len(pricing_opps) + len(market_opps)
                
                print(f"✅ {scenario['category']} Analysis Results:")
                print(f"   Brand opportunities: {len(brand_opps)}")
                print(f"   Product opportunities: {len(product_opps)}")
                print(f"   Pricing opportunities: {len(pricing_opps)}")
                print(f"   Market opportunities: {len(market_opps)}")
                print(f"   Total opportunities: {total_opportunities}")
                
                # Show key insight
                if exec_summary and 'key_insight' in exec_summary:
                    print(f"   Key insight: {exec_summary['key_insight'][:100]}...")
                
                # Determine success
                success = (
                    total_opportunities >= 4 and
                    len(brand_opps) >= 1 and
                    len(product_opps) >= 1 and
                    exec_summary is not None
                )
                
                results_summary.append({
                    "category": scenario['category'],
                    "status": "SUCCESS" if success else "PARTIAL",
                    "total_opportunities": total_opportunities,
                    "brand": len(brand_opps),
                    "product": len(product_opps),
                    "pricing": len(pricing_opps),
                    "market": len(market_opps)
                })
                
                print(f"   Status: {'✅ SUCCESS' if success else '⚠️ PARTIAL SUCCESS'}")
            else:
                print(f"❌ {scenario['category']} analysis failed: No final report")
                results_summary.append({
                    "category": scenario['category'],
                    "status": "FAILED",
                    "error": "No final report generated"
                })
                
        except Exception as e:
            print(f"❌ {scenario['category']} analysis failed with exception: {e}")
            results_summary.append({
                "category": scenario['category'],
                "status": "FAILED",
                "error": str(e)
            })
    
    # Final summary
    print(f"\n{'='*25} FINAL SUMMARY {'='*25}")
    
    successful_tests = [r for r in results_summary if r['status'] == 'SUCCESS']
    partial_tests = [r for r in results_summary if r['status'] == 'PARTIAL']
    failed_tests = [r for r in results_summary if r['status'] == 'FAILED']
    
    print(f"✅ Successful tests: {len(successful_tests)}/{len(test_scenarios)}")
    print(f"⚠️ Partial success: {len(partial_tests)}/{len(test_scenarios)}")
    print(f"❌ Failed tests: {len(failed_tests)}/{len(test_scenarios)}")
    
    if successful_tests:
        print(f"\n🎉 SUCCESS CATEGORIES:")
        for result in successful_tests:
            print(f"   • {result['category']}: {result['total_opportunities']} opportunities")
    
    if partial_tests:
        print(f"\n⚠️ PARTIAL SUCCESS CATEGORIES:")
        for result in partial_tests:
            print(f"   • {result['category']}: {result['total_opportunities']} opportunities")
    
    if failed_tests:
        print(f"\n❌ FAILED CATEGORIES:")
        for result in failed_tests:
            print(f"   • {result['category']}: {result.get('error', 'Unknown error')}")
    
    # Overall assessment
    overall_success_rate = len(successful_tests) / len(test_scenarios) * 100
    print(f"\n🏆 OVERALL SUCCESS RATE: {overall_success_rate:.1f}%")
    
    if overall_success_rate >= 80:
        print("🎉 EXCELLENT! System works reliably across medical device categories")
    elif overall_success_rate >= 60:
        print("👍 GOOD! System works well with minor issues")
    else:
        print("⚠️ NEEDS IMPROVEMENT! System has significant issues")
    
    return overall_success_rate >= 60

if __name__ == "__main__":
    test_multi_category_system() 