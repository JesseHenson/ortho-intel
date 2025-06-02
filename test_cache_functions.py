#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.backend.utils.cache_service import get_cached_analysis, store_analysis

async def test_cache_functions():
    print("=== TESTING CACHE CONVENIENCE FUNCTIONS ===")
    
    competitors = ['Stryker Spine', 'Zimmer Biomet']
    focus_area = 'spine_fusion'
    
    print(f"Testing with: {competitors} + {focus_area}")
    
    # Test get function
    print("\n1. Testing get_cached_analysis...")
    result = await get_cached_analysis(competitors, focus_area)
    print(f"Get result: {result is not None}")
    if result:
        print(f"Found cached data with keys: {list(result.keys())}")
    
    # Test store function
    print("\n2. Testing store_analysis...")
    test_data = {
        'clinical_gaps': [{'test': 'gap'}],
        'top_opportunities': [{'test': 'opp'}],
        'metadata': {'test': True}
    }
    test_state = {'raw_research_results': []}
    
    success = await store_analysis(competitors, focus_area, test_data, test_state, 15.0)
    print(f"Store success: {success}")
    
    # Test get again
    print("\n3. Testing get after store...")
    result2 = await get_cached_analysis(competitors, focus_area)
    print(f"Get after store: {result2 is not None}")
    if result2:
        print(f"Retrieved data with keys: {list(result2.keys())}")

if __name__ == "__main__":
    asyncio.run(test_cache_functions()) 