#!/usr/bin/env python3
"""
Debug script to examine the opportunity analysis result structure
"""

from main_langgraph_opportunity import opportunity_graph
import json

def debug_opportunity_data():
    """Debug the opportunity analysis data structure"""
    print("🔍 Debugging Opportunity Analysis Data Structure")
    print("=" * 60)
    
    try:
        print("\n1. 🚀 Running analysis...")
        result = opportunity_graph.run_analysis(['Stryker Spine', 'Zimmer Biomet'], 'spine_fusion')
        
        print("\n2. 📊 Result Structure Analysis:")
        print(f"   Result type: {type(result)}")
        print(f"   Top-level keys: {list(result.keys())}")
        
        print("\n3. 🎯 Opportunity Data Analysis:")
        
        # Check final_report structure
        final_report = result.get("final_report", {})
        if final_report:
            print(f"   final_report type: {type(final_report)}")
            print(f"   final_report keys: {list(final_report.keys())}")
            
            # Check each opportunity category in final_report
            for category in ["brand_opportunities", "product_opportunities", "pricing_opportunities", "market_opportunities"]:
                opps = final_report.get(category, [])
                print(f"   final_report.{category}: {len(opps)} opportunities")
                if opps:
                    print(f"      First opportunity keys: {list(opps[0].keys()) if opps else 'None'}")
        
        # Check direct access to opportunities
        print("\n4. 🔍 Direct Opportunity Access:")
        for category in ["brand_opportunities", "product_opportunities", "pricing_opportunities", "market_expansion_opportunities"]:
            opps = result.get(category, [])
            print(f"   result.{category}: {len(opps)} opportunities")
            if opps:
                print(f"      First opportunity: {opps[0] if opps else 'None'}")
        
        # Check top opportunities
        top_opps = result.get("top_opportunities", [])
        print(f"\n5. 🏆 Top Opportunities: {len(top_opps)} found")
        if top_opps:
            print(f"   First top opportunity: {top_opps[0]}")
        
        # Check executive summary
        exec_summary = result.get("executive_summary", {})
        print(f"\n6. 📋 Executive Summary: {type(exec_summary)}")
        if exec_summary:
            print(f"   Executive summary keys: {list(exec_summary.keys())}")
        
        # Save debug data to file
        with open("debug_opportunity_result.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n7. 💾 Full result saved to: debug_opportunity_result.json")
        
        return result
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_opportunity_data() 