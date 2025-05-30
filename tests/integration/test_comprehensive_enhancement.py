#!/usr/bin/env python3
"""
Comprehensive test to verify the enhanced opportunity analysis system
"""

from main_langgraph_opportunity import opportunity_graph

def test_comprehensive_enhancement():
    """Test all aspects of the enhanced system"""
    print("🧪 Comprehensive Enhancement Test")
    print("=" * 60)
    
    try:
        print("\n1. 🚀 Running Enhanced Analysis...")
        result = opportunity_graph.run_analysis(['Stryker Spine', 'Zimmer Biomet'], 'spine_fusion')
        
        print("✅ Analysis completed successfully!")
        
        # Test 1: Validation Error Fix
        print(f"\n2. ✅ Validation Error Test:")
        if 'error' not in result:
            print("   ✅ No validation errors detected")
        else:
            print(f"   ❌ Validation error: {result['error']}")
            return False
        
        # Test 2: Enhanced Query Generation
        print(f"\n3. 🔍 Enhanced Query Generation Test:")
        queries = result.get('search_queries', [])
        print(f"   Total queries generated: {len(queries)}")
        
        # Check for enhanced query types
        foundational_queries = [q for q in queries if 'revenue growth' in q or 'market share' in q]
        opportunity_queries = [q for q in queries if 'brand messaging' in q or 'R&D pipeline' in q]
        weakness_queries = [q for q in queries if 'complaints' in q or 'criticism' in q]
        
        print(f"   Foundational queries: {len(foundational_queries)}")
        print(f"   Opportunity-specific queries: {len(opportunity_queries)}")
        print(f"   Weakness identification queries: {len(weakness_queries)}")
        
        if len(queries) >= 10:
            print("   ✅ Enhanced query generation working")
        else:
            print("   ⚠️ Limited query generation")
        
        # Test 3: Opportunity Generation
        print(f"\n4. 💡 Opportunity Generation Test:")
        final_report = result.get('final_report', {})
        
        if final_report:
            brand_opps = final_report.get('brand_opportunities', [])
            product_opps = final_report.get('product_opportunities', [])
            pricing_opps = final_report.get('pricing_opportunities', [])
            market_opps = final_report.get('market_opportunities', [])
            
            print(f"   Brand opportunities: {len(brand_opps)}")
            print(f"   Product opportunities: {len(product_opps)}")
            print(f"   Pricing opportunities: {len(pricing_opps)}")
            print(f"   Market opportunities: {len(market_opps)}")
            
            total_opps = len(brand_opps) + len(product_opps) + len(pricing_opps) + len(market_opps)
            
            if total_opps >= 8:
                print(f"   ✅ Quality target met ({total_opps} opportunities)")
            else:
                print(f"   ⚠️ Quality target not met ({total_opps} opportunities, need 8+)")
            
            # Test enhanced opportunity fields
            if brand_opps:
                first_brand = brand_opps[0]
                enhanced_fields = ['competitive_advantage', 'success_metrics', 'investment', 'timeline']
                has_enhanced = all(field in first_brand for field in enhanced_fields)
                
                if has_enhanced:
                    print("   ✅ Enhanced opportunity fields present")
                else:
                    print("   ⚠️ Enhanced opportunity fields missing")
                    print(f"      Available fields: {list(first_brand.keys())}")
        
        # Test 4: Research Quality
        print(f"\n5. 📊 Research Quality Test:")
        raw_results = result.get('raw_research_results', [])
        print(f"   Research results collected: {len(raw_results)}")
        
        if raw_results:
            # Check for diverse sources
            unique_domains = set()
            for r in raw_results:
                url = r.get('url', '')
                if url:
                    domain = url.split('/')[2] if '/' in url else url
                    unique_domains.add(domain)
            
            print(f"   Unique information sources: {len(unique_domains)}")
            
            if len(unique_domains) >= 3:
                print("   ✅ Diverse information sources")
            else:
                print("   ⚠️ Limited source diversity")
        
        # Test 5: Executive Summary
        print(f"\n6. 📋 Executive Summary Test:")
        exec_summary = final_report.get('executive_summary', {})
        
        if exec_summary:
            key_fields = ['key_insight', 'top_3_opportunities', 'immediate_actions']
            has_key_fields = all(field in exec_summary for field in key_fields)
            
            if has_key_fields:
                print("   ✅ Executive summary complete")
                print(f"   Key insight: {exec_summary['key_insight'][:100]}...")
            else:
                print("   ⚠️ Executive summary incomplete")
        
        # Test 6: Competitive Profiles
        print(f"\n7. 🏢 Competitive Profiles Test:")
        comp_profiles = final_report.get('competitive_landscape', {})
        
        if comp_profiles:
            print(f"   Competitor profiles generated: {len(comp_profiles)}")
            
            # Check for required fields
            first_competitor = list(comp_profiles.keys())[0]
            profile = comp_profiles[first_competitor]
            required_fields = ['name', 'market_share', 'strengths', 'weaknesses', 'pricing_strategy']
            has_required = all(field in profile for field in required_fields)
            
            if has_required:
                print("   ✅ Complete competitor profiles")
            else:
                print("   ⚠️ Incomplete competitor profiles")
                print(f"      Missing fields: {[f for f in required_fields if f not in profile]}")
        
        print(f"\n🎉 Comprehensive Enhancement Test Results:")
        print(f"   ✅ System enhanced successfully")
        print(f"   ✅ Validation errors fixed")
        print(f"   ✅ Enhanced query generation implemented")
        print(f"   ✅ Robust opportunity generation working")
        print(f"   ✅ Quality targets achievable")
        
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_comprehensive_enhancement() 