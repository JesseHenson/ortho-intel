#!/usr/bin/env python3
"""
Test script for enhanced data models with progressive disclosure.
Validates that the new models work correctly and integrate properly.
"""

from datetime import datetime
from src.backend.core.source_models import (
    SourceCitation, SourceCollection, SourceType, CredibilityLevel,
    AnalysisMetadata, SourceCredibilityCalculator
)
from src.backend.core.opportunity_data_models import (
    OpportunitySummary, OpportunityDetail, OpportunityFull,
    OpportunityCategory, ImplementationDifficulty, InvestmentLevel, CompetitiveRisk,
    OpportunityDisclosureTransformer, StrategicOpportunity
)

def test_source_models():
    """Test source citation and collection models"""
    print("Testing Source Models...")
    
    # Test source citation
    source = SourceCitation(
        url="https://reuters.com/medical-device-market-analysis",
        title="Medical Device Market Analysis 2024",
        domain="reuters.com",
        content_snippet="The medical device market is expected to grow by 15% with significant opportunities in cardiovascular devices.",
        source_type=SourceType.NEWS_ARTICLE,
        credibility_score=8.5,
        relevance_score=9.0,
        retrieved_at=datetime.now(),
        key_insights=["15% market growth", "Cardiovascular opportunities"],
        supporting_quotes=["significant opportunities in cardiovascular devices"]
    )
    
    print(f"  ✓ Source created: {source.title}")
    print(f"  ✓ Credibility Level: {source.credibility_level}")
    print(f"  ✓ Relevance Level: {source.relevance_level}")
    
    # Test source collection
    sources = [source]
    collection = SourceCollection(sources=sources)
    
    print(f"  ✓ Collection created with {collection.total_sources} sources")
    print(f"  ✓ Average credibility: {collection.average_credibility}")
    print(f"  ✓ High credibility count: {collection.high_credibility_count}")
    
    return collection

def test_opportunity_models(source_collection):
    """Test progressive disclosure opportunity models"""
    print("\nTesting Opportunity Models...")
    
    # Test opportunity summary
    summary = OpportunitySummary(
        id=1,
        title="Expand Cardiovascular Device Portfolio",
        category=OpportunityCategory.PRODUCT_INNOVATION,
        opportunity_score=8.5,
        implementation_difficulty=ImplementationDifficulty.MEDIUM,
        time_to_market="12-18 months",
        source_collection=source_collection
    )
    
    print(f"  ✓ Summary created: {summary.title}")
    print(f"  ✓ Detail level: {summary.detail_level}")
    print(f"  ✓ Credibility indicator: {summary.credibility_indicator}")
    print(f"  ✓ Source count display: {summary.source_count_display}")
    
    # Test opportunity detail
    detail = OpportunityDetail(
        **summary.model_dump(),
        description="Leverage market growth in cardiovascular devices by expanding our product portfolio",
        investment_level=InvestmentLevel.HIGH,
        competitive_risk=CompetitiveRisk.MEDIUM,
        potential_impact="$50M revenue opportunity over 3 years",
        next_steps=[
            "Conduct market research",
            "Identify acquisition targets",
            "Develop business case"
        ],
        supporting_evidence="Market analysis shows 15% growth in cardiovascular devices",
        risk_factors=["Regulatory approval delays", "Competitive response"],
        success_metrics=["Market share increase", "Revenue targets"]
    )
    
    print(f"  ✓ Detail created with {len(detail.next_steps)} next steps")
    print(f"  ✓ Investment level: {detail.investment_level}")
    
    # Test opportunity full
    full = OpportunityFull(
        **detail.model_dump(),
        detailed_analysis="Comprehensive analysis of cardiovascular device market opportunities...",
        market_context={"market_size": "$50B", "growth_rate": "15%"},
        implementation_roadmap=[
            {"phase": "Research", "duration": "3 months", "cost": "$500K"},
            {"phase": "Development", "duration": "12 months", "cost": "$5M"}
        ]
    )
    
    print(f"  ✓ Full model created with detailed analysis")
    print(f"  ✓ Implementation roadmap: {len(full.implementation_roadmap)} phases")
    
    return summary, detail, full

def test_transformation_utilities():
    """Test transformation between model types"""
    print("\nTesting Transformation Utilities...")
    
    # Create legacy strategic opportunity
    legacy_opp = StrategicOpportunity(
        id=1,
        title="Legacy Opportunity",
        category=OpportunityCategory.MARKET_POSITIONING,
        description="Legacy opportunity description",
        opportunity_score=7.5,
        implementation_difficulty=ImplementationDifficulty.EASY,
        time_to_market="6 months",
        investment_level=InvestmentLevel.LOW,
        competitive_risk=CompetitiveRisk.LOW,
        potential_impact="Market positioning improvement",
        next_steps=["Step 1", "Step 2"],
        supporting_evidence="Market research data",
        source_urls=["https://example.com/source1", "https://example.com/source2"]
    )
    
    # Transform to progressive disclosure models
    summary = OpportunityDisclosureTransformer.strategic_to_summary(legacy_opp)
    detail = OpportunityDisclosureTransformer.strategic_to_detail(legacy_opp)
    full = OpportunityDisclosureTransformer.strategic_to_full(legacy_opp)
    
    print(f"  ✓ Transformed to summary: {summary.title}")
    print(f"  ✓ Transformed to detail: {detail.description}")
    print(f"  ✓ Transformed to full: {full.detail_level}")
    
    # Test source collection creation
    if summary.source_collection:
        print(f"  ✓ Source collection created with {summary.source_collection.total_sources} sources")
    
    return summary, detail, full

def test_credibility_calculator():
    """Test source credibility calculation utilities"""
    print("\nTesting Credibility Calculator...")
    
    # Test high credibility domain
    score1 = SourceCredibilityCalculator.calculate_credibility_score(
        "https://pubmed.ncbi.nlm.nih.gov/article123",
        SourceType.ACADEMIC_PAPER,
        "This study shows significant data on medical device efficacy"
    )
    print(f"  ✓ PubMed source score: {score1}")
    
    # Test medium credibility domain
    score2 = SourceCredibilityCalculator.calculate_credibility_score(
        "https://forbes.com/medical-devices",
        SourceType.NEWS_ARTICLE,
        "Industry experts believe this trend will continue"
    )
    print(f"  ✓ Forbes source score: {score2}")
    
    # Test relevance calculation
    relevance = SourceCredibilityCalculator.calculate_relevance_score(
        "Medical device market cardiovascular opportunities growth",
        ["medical device", "cardiovascular", "market"]
    )
    print(f"  ✓ Relevance score: {relevance}")
    
    return score1, score2, relevance

def test_analysis_metadata():
    """Test analysis metadata model"""
    print("\nTesting Analysis Metadata...")
    
    metadata = AnalysisMetadata(
        analysis_id="test_analysis_001",
        analysis_type="competitive_intelligence",
        pipeline_version="1.0.0",
        primary_model="gpt-4",
        started_at=datetime.now(),
        confidence_score=8.5,
        completeness_score=9.0,
        source_coverage=7.5,
        client_name="Test Client"
    )
    
    print(f"  ✓ Metadata created: {metadata.analysis_id}")
    print(f"  ✓ Analysis type: {metadata.analysis_type}")
    print(f"  ✓ Confidence score: {metadata.confidence_score}")
    
    return metadata

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Data Models for Progressive Disclosure\n")
    
    try:
        # Test source models
        source_collection = test_source_models()
        
        # Test opportunity models
        summary, detail, full = test_opportunity_models(source_collection)
        
        # Test transformation utilities
        trans_summary, trans_detail, trans_full = test_transformation_utilities()
        
        # Test credibility calculator
        score1, score2, relevance = test_credibility_calculator()
        
        # Test analysis metadata
        metadata = test_analysis_metadata()
        
        print("\n✅ All tests passed successfully!")
        print("\nModel Enhancement Summary:")
        print("  • Source citation models with credibility scoring")
        print("  • Progressive disclosure opportunity models (Summary/Detail/Full)")
        print("  • Transformation utilities for backward compatibility")
        print("  • Analysis metadata tracking")
        print("  • Automated credibility and relevance calculation")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 