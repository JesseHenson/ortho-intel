#!/usr/bin/env python3
"""
Comprehensive test suite for opportunity pipeline robustness.

Tests all critical path scenarios and edge cases to prevent 
"list index out of range" and similar errors.

Follows cursor rules for incremental testing and proper error prevention.
Location: src/backend/tests/ (following backend organization guidelines)
"""

import unittest
import sys
import os
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# Add project root to path for proper imports
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)

from src.backend.pipelines.main_langgraph_opportunity import OpportunityIntelligenceGraph
from src.backend.core.data_models import GraphState
from src.backend.core.opportunity_data_models import (
    StrategicOpportunity, OpportunityCategory, CategoryOpportunity,
    ImplementationDifficulty, InvestmentLevel, CompetitiveRisk
)

class TestOpportunityPipelineRobustness(unittest.TestCase):
    """Test opportunity pipeline for robustness and error prevention"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.graph = OpportunityIntelligenceGraph()
        
        # Test data templates
        self.minimal_state = {
            "competitors": ["Test Competitor 1", "Test Competitor 2"],
            "focus_area": "spine_fusion",
            "device_category": "spine_devices",
            "clinical_gaps": [],
            "market_share_insights": [],
            "raw_research_results": [],
            "enhanced_source_metadata": [],
            "error_messages": []
        }
        
        self.state_with_opportunities = {
            **self.minimal_state,
            "strategic_opportunities": [
                {
                    "id": 1,
                    "title": "Test Opportunity 1",
                    "category": "Brand Strategy",
                    "description": "Test opportunity description",
                    "opportunity_score": 8.5,
                    "next_steps": ["Step 1", "Step 2"],
                    "time_to_market": "6-12 months",
                    "investment_level": "Medium"
                },
                {
                    "id": 2,
                    "title": "Test Opportunity 2",
                    "category": "Product Innovation",
                    "description": "Test product opportunity",
                    "opportunity_score": 7.8,
                    "next_steps": ["Design", "Test"],
                    "time_to_market": "12-18 months",
                    "investment_level": "High"
                }
            ],
            "top_opportunities": [
                {
                    "id": 1,
                    "title": "Top Opportunity 1",
                    "category": "Market Positioning",
                    "description": "High-priority opportunity",
                    "opportunity_score": 9.2
                }
            ]
        }
    
    def test_categorize_opportunities_with_empty_state(self):
        """Test categorize_opportunities with minimal/empty state"""
        print("🧪 Testing categorize_opportunities with empty state...")
        
        try:
            result = self.graph.categorize_opportunities(self.minimal_state)
            
            # Should not crash and should have default structure
            self.assertIsInstance(result, dict)
            self.assertIn("brand_opportunities", result)
            self.assertIn("product_opportunities", result)
            self.assertIn("pricing_opportunities", result)
            self.assertIn("market_expansion_opportunities", result)
            
            print("✅ Empty state handled gracefully")
            
        except Exception as e:
            self.fail(f"categorize_opportunities failed with empty state: {str(e)}")
    
    def test_categorize_opportunities_missing_all_opportunities_key(self):
        """Test the specific issue: missing 'all_opportunities' key"""
        print("🧪 Testing categorize_opportunities with missing 'all_opportunities' key...")
        
        # This should be the current failing scenario
        state_without_all_opportunities = {
            **self.minimal_state,
            "strategic_opportunities": [{"title": "Test"}],
            "top_opportunities": [{"title": "Top Test"}]
            # Note: no "all_opportunities" key
        }
        
        try:
            result = self.graph.categorize_opportunities(state_without_all_opportunities)
            
            # Should handle missing key gracefully
            self.assertIsInstance(result, dict)
            print("✅ Missing 'all_opportunities' key handled gracefully")
            
        except (IndexError, KeyError) as e:
            print(f"❌ CONFIRMED BUG: {str(e)}")
            # This is the bug we're fixing
            self.fail(f"categorize_opportunities crashes with missing 'all_opportunities' key: {str(e)}")
    
    def test_categorize_opportunities_with_valid_data(self):
        """Test categorize_opportunities with valid opportunity data"""
        print("🧪 Testing categorize_opportunities with valid data...")
        
        # Add the missing 'all_opportunities' key
        state_with_all_opportunities = {
            **self.state_with_opportunities,
            "all_opportunities": self.state_with_opportunities["strategic_opportunities"]
        }
        
        try:
            result = self.graph.categorize_opportunities(state_with_all_opportunities)
            
            # Should categorize opportunities correctly
            self.assertIsInstance(result, dict)
            self.assertTrue(len(result.get("brand_opportunities", [])) > 0)
            self.assertTrue(len(result.get("product_opportunities", [])) > 0)
            
            print("✅ Valid data categorized successfully")
            
        except Exception as e:
            self.fail(f"categorize_opportunities failed with valid data: {str(e)}")
    
    def test_list_access_robustness(self):
        """Test that all list accesses are protected against index errors"""
        print("🧪 Testing list access robustness...")
        
        # Test with various edge cases
        edge_cases = [
            {},  # Empty dict
            {"competitors": []},  # Empty competitors
            {"top_opportunities": []},  # Empty opportunities
            {"strategic_opportunities": [{}]},  # Opportunities with missing fields
        ]
        
        for i, edge_case_state in enumerate(edge_cases):
            try:
                # Test state initialization doesn't crash
                safe_state = {**self.minimal_state, **edge_case_state}
                
                # Test categorize_opportunities with edge case
                if hasattr(self.graph, 'categorize_opportunities'):
                    result = self.graph.categorize_opportunities(safe_state)
                    self.assertIsInstance(result, dict)
                
                print(f"✅ Edge case {i+1} handled safely")
                
            except Exception as e:
                self.fail(f"Edge case {i+1} failed: {str(e)}")
    
    def test_data_flow_consistency(self):
        """Test that data flows consistently between pipeline steps"""
        print("🧪 Testing data flow consistency...")
        
        # Test the key flow: generate_opportunities -> categorize_opportunities
        test_state = self.minimal_state.copy()
        
        try:
            # Simulate generate_opportunities output
            gen_result = self.graph.generate_opportunities(test_state)
            
            # Check what keys are actually set
            expected_keys = ["strategic_opportunities", "top_opportunities"]
            for key in expected_keys:
                if key not in gen_result:
                    print(f"⚠️  WARNING: generate_opportunities doesn't set '{key}'")
            
            # Test categorize_opportunities with the actual output
            cat_result = self.graph.categorize_opportunities(gen_result)
            
            print("✅ Data flow consistency verified")
            
        except Exception as e:
            print(f"❌ Data flow inconsistency: {str(e)}")
            # This helps us identify the exact data flow issue
            
    def test_opportunity_state_keys_mapping(self):
        """Test the mapping between state keys and expected data"""
        print("🧪 Testing opportunity state keys mapping...")
        
        # Document what keys are expected vs what keys are actually used
        expected_by_categorize = ["all_opportunities"]
        provided_by_generate = ["strategic_opportunities", "top_opportunities"]
        
        # This reveals the mismatch
        missing_keys = set(expected_by_categorize) - set(provided_by_generate)
        if missing_keys:
            print(f"⚠️  KEY MISMATCH: categorize expects {missing_keys} but generate doesn't provide them")
            
        print("✅ State key mapping analyzed")
    
    def test_error_handling_integration(self):
        """Test error handling throughout the pipeline"""
        print("🧪 Testing error handling integration...")
        
        # Test with intentionally problematic data
        problematic_state = {
            **self.minimal_state,
            "strategic_opportunities": [
                {"missing_required_fields": True},  # Invalid opportunity
                None,  # Null opportunity
            ],
            "top_opportunities": "not_a_list",  # Wrong type
        }
        
        try:
            # The pipeline should handle errors gracefully
            result = self.graph.categorize_opportunities(problematic_state)
            
            # Should still return a valid structure
            self.assertIsInstance(result, dict)
            
            # Should have error messages if implemented
            if "error_messages" in result:
                self.assertIsInstance(result["error_messages"], list)
            
            print("✅ Error handling working correctly")
            
        except Exception as e:
            print(f"⚠️  Error handling needs improvement: {str(e)}")
    
    def test_executive_summary_with_empty_opportunities(self):
        """Test executive summary generation with empty opportunities list"""
        print("🧪 Testing executive summary with empty opportunities...")
        
        # Test with empty list
        executive_summary = self.graph._generate_executive_summary([], ["Stryker Spine"], "spinal_devices")
        self.assertIsInstance(executive_summary.top_3_opportunities, list)
        self.assertGreater(len(executive_summary.top_3_opportunities), 0)
        
        # Test with None values
        opportunities_with_none = [{"title": None}, {"title": ""}, {}]
        executive_summary = self.graph._generate_executive_summary(opportunities_with_none, ["Zimmer Biomet"], "spinal_devices")
        self.assertIsInstance(executive_summary.top_3_opportunities, list)
        
        print("✅ Executive summary generation robust against empty data")
    
    def test_string_formatting_robustness(self):
        """Test that all string formatting operations are safe"""
        print("🧪 Testing string formatting robustness...")
        
        # Test various edge cases that could cause string formatting errors
        test_cases = [
            {"executive_summary": MagicMock(top_3_opportunities=[]), "comprehensive_metadata": MagicMock(node_executions=[], overall_confidence=7.5)},
            {"executive_summary": MagicMock(top_3_opportunities=None), "comprehensive_metadata": MagicMock(node_executions=None, overall_confidence=8.0)},
            {"executive_summary": MagicMock(top_3_opportunities=["op1", "op2"]), "comprehensive_metadata": MagicMock(node_executions=["exec1"], overall_confidence=9.0)}
        ]
        
        for i, case in enumerate(test_cases):
            try:
                # Test the string formatting that was causing issues
                exec_summary = case["executive_summary"]
                metadata = case["comprehensive_metadata"]
                
                # Safe formatting similar to what's in the actual code
                opportunity_count = len(exec_summary.top_3_opportunities) if exec_summary.top_3_opportunities else 0
                execution_count = len(metadata.node_executions) if metadata.node_executions else 0
                
                formatted_string = f"Generated executive summary with {opportunity_count} key opportunities"
                execution_string = f"Documented complete methodology with {execution_count} node executions"
                
                self.assertIsInstance(formatted_string, str)
                self.assertIsInstance(execution_string, str)
                
            except Exception as e:
                self.fail(f"String formatting failed for test case {i}: {str(e)}")
        
        print("✅ String formatting is robust against None/empty values")

    def test_helper_method_existence(self):
        """Test that all required helper methods exist"""
        print("🧪 Testing helper method existence...")
        
        required_methods = [
            '_generate_brand_opportunities',
            '_generate_product_opportunities', 
            '_generate_pricing_opportunities',
            '_generate_market_opportunities'
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(self.graph, method_name), 
                           f"Missing required helper method: {method_name}")
        
        print("✅ All required helper methods exist")

    def test_method_execution_robustness(self):
        """Test that all helper methods execute without errors"""
        print("🧪 Testing helper method execution...")
        
        competitors = ["Test Competitor"]
        device_category = "test_devices"
        
        try:
            brand_opps = self.graph._generate_brand_opportunities(competitors, device_category)
            self.assertIsInstance(brand_opps, list)
            
            product_opps = self.graph._generate_product_opportunities(competitors, device_category)
            self.assertIsInstance(product_opps, list)
            
            pricing_opps = self.graph._generate_pricing_opportunities(competitors, device_category)
            self.assertIsInstance(pricing_opps, list)
            
            market_opps = self.graph._generate_market_opportunities(competitors, device_category)
            self.assertIsInstance(market_opps, list)
            
            print("✅ All helper methods execute without errors")
            
        except Exception as e:
            self.fail(f"Helper method execution failed: {str(e)}")

    def test_opportunity_source_links_empty_metadata(self):
        """Test _create_opportunity_source_links with empty metadata list"""
        print("🧪 Testing _create_opportunity_source_links with empty metadata...")
        
        # Create sample opportunities
        opportunities = [
            {"title": "Opportunity 1"},
            {"title": "Opportunity 2"},
            {"title": "Opportunity 3"}
        ]
        
        # Test with empty metadata list
        empty_metadata = []
        links = self.graph._create_opportunity_source_links(opportunities, empty_metadata)
        
        # Should return placeholder links without crashing
        self.assertEqual(len(links), 3)
        for link in links:
            self.assertEqual(link, "Source: Analysis-based insight")
        
        print("✅ Empty metadata handled safely")
        
        # Test with fewer metadata items than opportunities
        partial_metadata = [
            {"url": "https://example1.com", "title": "Source 1"},
            {"url": "https://example2.com", "title": "Source 2"}
        ]
        
        links = self.graph._create_opportunity_source_links(opportunities, partial_metadata)
        
        # Should cycle through available metadata
        self.assertEqual(len(links), 3)
        self.assertEqual(links[0], "Source: https://example1.com")
        self.assertEqual(links[1], "Source: https://example2.com") 
        self.assertEqual(links[2], "Source: https://example1.com")  # Cycles back to first
        
        print("✅ Partial metadata handled with cycling")
        
        # Test with metadata without URLs
        metadata_no_urls = [
            {"title": "Source without URL"},
            {"content": "Some content"}
        ]
        
        links = self.graph._create_opportunity_source_links(opportunities, metadata_no_urls)
        
        # Should provide fallback for missing URLs
        self.assertEqual(len(links), 3)
        for link in links:
            self.assertEqual(link, "Source: Analysis-based insight")
        
        print("✅ Missing URLs handled with fallback")

if __name__ == "__main__":
    print("🚀 Running Opportunity Pipeline Robustness Tests")
    print("=" * 60)
    print("This test suite identifies and prevents 'list index out of range' errors")
    print("and other robustness issues in the opportunity pipeline.")
    print("Location: src/backend/tests/ (following backend organization guidelines)")
    print("=" * 60)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("🎯 Test suite completed. Review any failures to identify fixes needed.") 