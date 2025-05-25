# test_dataset.py
"""
Test data for validating the orthopedic competitive intelligence prototype
"""

from data_models import CompetitorAnalysisRequest, ClinicalGap, MarketOpportunity

# Test Input Data
TEST_COMPETITORS = [
    "Stryker Spine",
    "Zimmer Biomet", 
    "Orthofix"
]

TEST_REQUESTS = [
    CompetitorAnalysisRequest(
        competitors=["Stryker Spine", "Zimmer Biomet"],
        focus_area="spine_fusion"
    ),
    CompetitorAnalysisRequest(
        competitors=["Orthofix"], 
        focus_area="spine_fusion"
    ),
    CompetitorAnalysisRequest(
        competitors=TEST_COMPETITORS,
        focus_area="spine_fusion"
    )
]

# Expected Output Patterns (for validation)
EXPECTED_GAPS_PATTERNS = [
    # From our Tavily research, we know these should be found
    {
        "competitor": "Zimmer Biomet",
        "keywords": ["recall", "FDA", "Class I", "spinal fusion stimulator"],
        "gap_type": "regulatory"
    },
    {
        "competitor": "Stryker Spine", 
        "keywords": ["clinical", "fusion", "complications"],
        "gap_type": "clinical"
    }
]

EXPECTED_OPPORTUNITIES_PATTERNS = [
    {
        "keywords": ["minimally invasive", "outpatient", "less invasive"],
        "opportunity_type": "procedural_innovation"
    },
    {
        "keywords": ["unmet need", "gap", "conservative care", "surgery"],
        "opportunity_type": "treatment_gap"
    }
]

# Sample Expected Output (based on our research)
SAMPLE_EXPECTED_RESPONSE = {
    "competitors_analyzed": ["Stryker Spine", "Zimmer Biomet"],
    "clinical_gaps": [
        {
            "competitor": "Zimmer Biomet",
            "gap_type": "regulatory",
            "description": "Multiple FDA Class I recalls for spinal fusion stimulators due to quality control issues",
            "evidence": "FDA recall notices for SpF PLUS-Mini and SpF-XL IIb devices",
            "severity": "high"
        }
    ],
    "market_opportunities": [
        {
            "opportunity_type": "less_invasive_procedures",
            "description": "Growing demand for minimally invasive spine fusion alternatives",
            "market_size_indicator": "Emerging trend",
            "competitive_landscape": "Limited options between conservative care and surgery"
        }
    ],
    "summary": "Analysis identified significant regulatory compliance gaps at Zimmer Biomet and market opportunities in less invasive fusion procedures."
}

# Test Search Queries (that we know work from our validation)
WORKING_SEARCH_QUERIES = [
    "Stryker spine fusion clinical limitations surgeon feedback",
    "Zimmer Biomet spine fusion complications clinical study results", 
    "unmet clinical needs spine surgery 2024 surgeon survey orthopedic gaps",
    "Orthofix spine fusion device issues FDA warnings",
    "minimally invasive spine fusion market opportunities 2024"
]

# Validation Functions
def validate_response_structure(response_dict):
    """Validate that response has required structure"""
    required_keys = [
        "competitors_analyzed", 
        "clinical_gaps", 
        "market_opportunities", 
        "summary"
    ]
    
    for key in required_keys:
        if key not in response_dict:
            return False, f"Missing required key: {key}"
    
    return True, "Structure valid"

def validate_content_quality(response_dict):
    """Validate that response has meaningful content"""
    gaps = response_dict.get("clinical_gaps", [])
    opportunities = response_dict.get("market_opportunities", [])
    
    if len(gaps) < 1:
        return False, "No clinical gaps identified"
    
    if len(opportunities) < 1:
        return False, "No market opportunities identified"
    
    # Check for evidence
    for gap in gaps:
        if not gap.get("evidence") or len(gap.get("evidence", "")) < 50:
            return False, f"Insufficient evidence for gap: {gap.get('description', 'Unknown')}"
    
    return True, "Content quality acceptable"

def validate_competitor_coverage(response_dict, requested_competitors):
    """Validate that all requested competitors were analyzed"""
    analyzed = response_dict.get("competitors_analyzed", [])
    
    for competitor in requested_competitors:
        if competitor not in analyzed:
            return False, f"Missing analysis for competitor: {competitor}"
    
    return True, "All competitors covered"

# Test Execution Helper
class TestRunner:
    """Helper class to run validation tests"""
    
    @staticmethod
    def run_basic_validation(response_dict, request):
        """Run all basic validation tests"""
        results = []
        
        # Structure validation
        is_valid, message = validate_response_structure(response_dict)
        results.append(("Structure", is_valid, message))
        
        # Content quality validation  
        is_valid, message = validate_content_quality(response_dict)
        results.append(("Content Quality", is_valid, message))
        
        # Competitor coverage validation
        is_valid, message = validate_competitor_coverage(
            response_dict, 
            request.competitors
        )
        results.append(("Competitor Coverage", is_valid, message))
        
        return results
    
    @staticmethod
    def print_validation_results(results):
        """Print validation results in readable format"""
        print("\n=== VALIDATION RESULTS ===")
        for test_name, passed, message in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}: {message}")
        
        total_tests = len(results)
        passed_tests = sum(1 for _, passed, _ in results if passed)
        print(f"\nSummary: {passed_tests}/{total_tests} tests passed")
        
        return passed_tests == total_tests

# Quick Test Data Access
def get_test_request():
    """Get a simple test request for development"""
    return TEST_REQUESTS[0]

def get_comprehensive_test_request():
    """Get the most comprehensive test request"""
    return TEST_REQUESTS[2]

if __name__ == "__main__":
    # Quick test of data models
    test_req = get_test_request()
    print("Test request:", test_req.model_dump())
    
    # Test validation functions
    sample_response = SAMPLE_EXPECTED_RESPONSE
    results = TestRunner.run_basic_validation(sample_response, test_req)
    TestRunner.print_validation_results(results)