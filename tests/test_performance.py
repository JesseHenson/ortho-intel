#!/usr/bin/env python3
"""
Performance benchmarks for multi-category expansion
"""

import time
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def benchmark_search_template_generation():
    """Benchmark search query generation performance"""
    try:
        from data_models import SearchTemplates
        from test_dataset import get_test_request
        
        print("Benchmarking search template generation...")
        
        test_req = get_test_request()
        competitor = test_req.competitors[0]
        focus_area = test_req.focus_area
        
        # Benchmark competitor queries
        start_time = time.time()
        for _ in range(100):  # Run 100 times for average
            queries = SearchTemplates.get_competitor_queries(competitor, focus_area)
        competitor_time = (time.time() - start_time) / 100
        
        # Benchmark market queries
        start_time = time.time()
        for _ in range(100):
            market_queries = SearchTemplates.get_market_queries(focus_area)
        market_time = (time.time() - start_time) / 100
        
        print(f"✅ Competitor query generation: {competitor_time*1000:.2f}ms average")
        print(f"✅ Market query generation: {market_time*1000:.2f}ms average")
        
        # Performance requirements
        assert competitor_time < 0.01, f"Competitor query generation too slow: {competitor_time*1000:.2f}ms"
        assert market_time < 0.01, f"Market query generation too slow: {market_time*1000:.2f}ms"
        
        return {
            "competitor_query_time_ms": competitor_time * 1000,
            "market_query_time_ms": market_time * 1000
        }
        
    except Exception as e:
        print(f"❌ Search template benchmark failed: {e}")
        return None

def benchmark_analysis_processor():
    """Benchmark analysis processing performance"""
    try:
        from data_models import AnalysisProcessor
        
        print("Benchmarking analysis processor...")
        
        # Create larger mock dataset for realistic testing
        mock_results = []
        for i in range(50):  # 50 search results
            mock_results.append({
                "competitor": f"Test Competitor {i % 3}",
                "content": f"Clinical study {i} shows device limitations and complications in spine fusion procedures. FDA warning letters indicate safety concerns.",
                "url": f"https://example.com/result-{i}",
                "title": f"Clinical Study {i}"
            })
        
        # Benchmark gap extraction
        start_time = time.time()
        gaps = AnalysisProcessor.extract_clinical_gaps(mock_results, "Test Competitor")
        gap_time = time.time() - start_time
        
        # Benchmark opportunity extraction
        start_time = time.time()
        opportunities = AnalysisProcessor.extract_market_opportunities(mock_results)
        opportunity_time = time.time() - start_time
        
        print(f"✅ Gap extraction (50 results): {gap_time*1000:.2f}ms")
        print(f"✅ Opportunity extraction (50 results): {opportunity_time*1000:.2f}ms")
        print(f"   Found {len(gaps)} gaps, {len(opportunities)} opportunities")
        
        # Performance requirements
        assert gap_time < 1.0, f"Gap extraction too slow: {gap_time:.2f}s"
        assert opportunity_time < 1.0, f"Opportunity extraction too slow: {opportunity_time:.2f}s"
        
        return {
            "gap_extraction_time_ms": gap_time * 1000,
            "opportunity_extraction_time_ms": opportunity_time * 1000,
            "gaps_found": len(gaps),
            "opportunities_found": len(opportunities)
        }
        
    except Exception as e:
        print(f"❌ Analysis processor benchmark failed: {e}")
        return None

def benchmark_graph_initialization():
    """Benchmark LangGraph initialization performance"""
    try:
        print("Benchmarking LangGraph initialization...")
        
        start_time = time.time()
        from main_langgraph import intelligence_graph
        init_time = time.time() - start_time
        
        print(f"✅ LangGraph initialization: {init_time*1000:.2f}ms")
        
        # Performance requirement
        assert init_time < 5.0, f"Graph initialization too slow: {init_time:.2f}s"
        
        return {
            "graph_init_time_ms": init_time * 1000
        }
        
    except Exception as e:
        print(f"❌ Graph initialization benchmark failed: {e}")
        return None

def benchmark_memory_usage():
    """Benchmark memory usage of core components"""
    try:
        import psutil
        import os
        
        print("Benchmarking memory usage...")
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Load all components
        from main_langgraph import intelligence_graph
        from data_models import SearchTemplates, AnalysisProcessor
        from test_dataset import get_test_request
        
        # Create some test data
        test_req = get_test_request()
        queries = SearchTemplates.get_competitor_queries(test_req.competitors[0], test_req.focus_area)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"✅ Initial memory: {initial_memory:.1f}MB")
        print(f"✅ Final memory: {final_memory:.1f}MB")
        print(f"✅ Memory increase: {memory_increase:.1f}MB")
        
        # Memory requirement (should be reasonable)
        assert memory_increase < 100, f"Memory usage too high: {memory_increase:.1f}MB"
        
        return {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase
        }
        
    except ImportError:
        print("⚠️ psutil not available, skipping memory benchmark")
        return {"memory_benchmark": "skipped"}
    except Exception as e:
        print(f"❌ Memory benchmark failed: {e}")
        return None

def run_performance_benchmarks():
    """Run all performance benchmarks"""
    print("⚡ PERFORMANCE BENCHMARKS")
    print("=" * 50)
    print("Establishing baseline performance metrics...")
    print()
    
    benchmarks = [
        ("Search Template Generation", benchmark_search_template_generation),
        ("Analysis Processor", benchmark_analysis_processor),
        ("Graph Initialization", benchmark_graph_initialization),
        ("Memory Usage", benchmark_memory_usage)
    ]
    
    results = {}
    passed = 0
    total = len(benchmarks)
    
    for benchmark_name, benchmark_func in benchmarks:
        print(f"Running {benchmark_name}...")
        result = benchmark_func()
        if result is not None:
            results[benchmark_name] = result
            passed += 1
        print()
    
    print("=" * 50)
    print(f"PERFORMANCE BENCHMARK RESULTS: {passed}/{total} benchmarks completed")
    
    if passed == total:
        print("✅ BASELINE PERFORMANCE ESTABLISHED")
        print("🎯 Performance requirements for multi-category expansion:")
        print("   - Category detection: <1 second")
        print("   - Analysis time: <5 minutes total")
        print("   - Memory increase: <50MB additional")
        print("   - Query generation: <10ms per competitor")
    else:
        print("❌ PERFORMANCE BENCHMARK ISSUES")
        print("⚠️ Address performance issues before expansion")
    
    # Save baseline results for comparison
    try:
        import json
        with open("performance_baseline.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📊 Baseline results saved to performance_baseline.json")
    except Exception as e:
        print(f"⚠️ Could not save baseline results: {e}")
    
    return passed == total

if __name__ == "__main__":
    success = run_performance_benchmarks()
    sys.exit(0 if success else 1) 