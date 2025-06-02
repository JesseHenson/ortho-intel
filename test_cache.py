#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.backend.utils.cache_service import cache_service

async def test_cache():
    try:
        print("=== CACHE SERVICE TEST ===")
        
        competitors = ['Stryker Spine', 'Zimmer Biomet']
        focus_area = 'spine_fusion'
        
        print(f"Testing with competitors: {competitors}")
        print(f"Focus area: {focus_area}")
        
        # Test cache key generation
        from src.backend.core.cache_models import AnalysisCache
        cache_key = AnalysisCache.generate_cache_key(competitors, focus_area)
        print(f"Generated cache key: {cache_key}")
        
        # Check for existing cache
        print("\n1. Checking for existing cache...")
        cached = await cache_service.get_cached_analysis(competitors, focus_area)
        print(f"Cached result found: {cached is not None}")
        
        if not cached:
            print("\n2. Storing test results...")
            test_results = {
                'clinical_gaps': [{'test': 'gap1'}, {'test': 'gap2'}],
                'top_opportunities': [{'test': 'opp1'}],
                'metadata': {'test': True}
            }
            test_state = {'raw_research_results': [], 'search_queries': []}
            
            success = await cache_service.store_analysis(
                competitors, focus_area, test_results, test_state, 30.0
            )
            print(f"Store success: {success}")
            
            if success:
                print("\n3. Retrieving stored results...")
                cached = await cache_service.get_cached_analysis(competitors, focus_area)
                print(f"After storing - cached result found: {cached is not None}")
                if cached:
                    print(f"Cached gaps: {len(cached.get('clinical_gaps', []))}")
                    print(f"Cached opportunities: {len(cached.get('top_opportunities', []))}")
        else:
            print("Found existing cached results!")
            print(f"Cached gaps: {len(cached.get('clinical_gaps', []))}")
            print(f"Cached opportunities: {len(cached.get('top_opportunities', []))}")
        
        # Get cache stats
        print("\n4. Cache statistics:")
        stats = await cache_service.get_cache_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cache()) 