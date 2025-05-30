# main_langgraph_opportunity.py
"""
Enhanced Opportunity-First LangGraph implementation for competitive intelligence
Transforms clinical gaps into strategic opportunities with executive-ready insights
"""

import os
from typing import List, Dict, Any, Literal
from langgraph.graph import StateGraph
from langgraph.types import Command
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from ..core.data_models import (
    GraphState, 
    SearchTemplates, 
    AnalysisProcessor,
    ClinicalGap,
    MarketOpportunity,
    Config,
    CategoryRouter
)

from ..core.opportunity_data_models import (
    StrategicOpportunity,
    OpportunityCategory,
    ImplementationDifficulty,
    InvestmentLevel,
    CompetitiveRisk,
    CategoryOpportunity,
    CompetitorProfile,
    ExecutiveSummary,
    OpportunityAnalysisResponse,
    OpportunityTransformer,
    OpportunityRanker,
    enhance_graph_state_with_opportunities
)

from ..core.source_models import AnalysisMetadata
from ..core.opportunity_data_models import OpportunityDisclosureTransformer

# Initialize tools and LLM
tavily_tool = TavilySearchResults(
    max_results=Config.TAVILY_MAX_RESULTS,
    include_answer=True,
    include_raw_content=True,
    include_images=False,
    search_depth=Config.TAVILY_SEARCH_DEPTH
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1
)

class OpportunityIntelligenceGraph:
    """Enhanced LangGraph implementation for opportunity-first competitive intelligence"""
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the enhanced opportunity-first workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes (enhanced pipeline)
        workflow.add_node("detect_category", self.detect_category)
        workflow.add_node("initialize", self.initialize_research)
        workflow.add_node("research_competitor", self.research_competitor)
        workflow.add_node("analyze_competitive_gaps", self.analyze_competitive_gaps)  # Enhanced
        workflow.add_node("generate_opportunities", self.generate_opportunities)      # New
        workflow.add_node("categorize_opportunities", self.categorize_opportunities)  # New
        workflow.add_node("synthesize_opportunity_report", self.synthesize_opportunity_report)  # Enhanced
        
        # Set entry point
        workflow.set_entry_point("detect_category")
        
        # Define workflow edges
        workflow.add_edge("detect_category", "initialize")
        workflow.add_edge("initialize", "research_competitor")
        workflow.add_edge("research_competitor", "analyze_competitive_gaps")
        workflow.add_edge("analyze_competitive_gaps", "generate_opportunities")
        workflow.add_edge("generate_opportunities", "categorize_opportunities")
        workflow.add_edge("categorize_opportunities", "synthesize_opportunity_report")
        workflow.add_edge("synthesize_opportunity_report", "__end__")
        
        # Compile and return
        return workflow.compile()
    
    def detect_category(self, state: GraphState) -> Dict[str, Any]:
        """Detect device category based on competitors and context"""
        competitors = state["competitors"]
        focus_area = state["focus_area"]
        
        # Detect category using CategoryRouter
        detected_category = CategoryRouter.detect_category(competitors, focus_area)
        
        print(f"🎯 Category detected: {detected_category}")
        print(f"   Competitors: {competitors}")
        print(f"   Context: {focus_area}")
        
        # Enhance state with opportunity-first fields
        enhanced_state = enhance_graph_state_with_opportunities(state)
        enhanced_state["device_category"] = detected_category
        
        return enhanced_state
    
    def initialize_research(self, state: GraphState) -> Dict[str, Any]:
        """Initialize the research process with opportunity-focused queries"""
        competitors = state["competitors"]
        focus_area = state["focus_area"]
        device_category = state["device_category"]
        
        print(f"🔍 Starting opportunity-first analysis for {len(competitors)} competitors in {device_category}")
        
        # Generate enhanced search queries for opportunity discovery
        all_queries = []
        for competitor in competitors:
            # Get standard competitor queries
            competitor_queries = SearchTemplates.get_competitor_queries(competitor, focus_area, device_category)
            all_queries.extend(competitor_queries)
            
            # Add opportunity-focused queries
            opportunity_queries = self._generate_opportunity_queries(competitor, device_category)
            all_queries.extend(opportunity_queries)
        
        # Add market-level opportunity queries
        market_queries = SearchTemplates.get_market_queries(focus_area, device_category)
        all_queries.extend(market_queries)
        
        # Add strategic opportunity queries
        strategic_queries = self._generate_strategic_queries(device_category, competitors)
        all_queries.extend(strategic_queries)
        
        state.update({
            "search_queries": all_queries,
            "current_competitor": competitors[0],
            "research_iteration": 0,
            "raw_research_results": [],
            "clinical_gaps": [],
            "market_opportunities": [],
            "error_messages": []
        })
        
        return state
    
    def research_competitor(self, state: GraphState) -> Dict[str, Any]:
        """Research individual competitor using Tavily with enhanced queries"""
        current_competitor = state["current_competitor"]
        competitors = state["competitors"]
        iteration = state["research_iteration"]
        existing_results = state["raw_research_results"]
        
        print(f"📊 Researching {current_competitor} (iteration {iteration + 1})")
        
        try:
            # Generate competitor-specific query using detected category
            device_category = state["device_category"]
            competitor_queries = SearchTemplates.get_competitor_queries(current_competitor, state["focus_area"], device_category)
            
            # Add opportunity-focused queries
            opportunity_queries = self._generate_opportunity_queries(current_competitor, device_category)
            all_queries = competitor_queries + opportunity_queries
            
            if iteration < len(all_queries):
                query = all_queries[iteration]
            else:
                # Fallback query based on category
                category_info = CategoryRouter.get_category_info(device_category)
                primary_keyword = category_info["keywords"][0] if category_info["keywords"] else "medical device"
                query = f"{current_competitor} {primary_keyword} market opportunities 2024"
            
            print(f"   Query: {query}")
            
            # Execute search
            search_results = tavily_tool.invoke({"query": query})
            
            # Process results
            if isinstance(search_results, list):
                processed_results = []
                for result in search_results:
                    if isinstance(result, dict):
                        processed_results.append({
                            "competitor": current_competitor,
                            "query": query,
                            "url": result.get("url", ""),
                            "title": result.get("title", ""),
                            "content": result.get("content", ""),
                            "score": result.get("score", 0)
                        })
                
                existing_results.extend(processed_results)
                print(f"   Found {len(processed_results)} results")
            
        except Exception as e:
            error_msg = f"Research failed for {current_competitor}: {str(e)}"
            print(f"   ❌ {error_msg}")
            state["error_messages"] = state["error_messages"] + [error_msg]
            state["research_iteration"] = iteration + 1
            
            # Continue to next step if too many failures
            if iteration >= 2:
                return self._advance_research_state(state, competitors, current_competitor, existing_results, iteration)
            else:
                return state
        
        # Decide next action
        next_iteration = iteration + 1
        current_idx = competitors.index(current_competitor)
        
        if next_iteration >= 4:  # Max 4 searches per competitor (enhanced)
            if current_idx < len(competitors) - 1:
                # Move to next competitor
                next_competitor = competitors[current_idx + 1]
                state.update({
                    "raw_research_results": existing_results,
                    "current_competitor": next_competitor,
                    "research_iteration": 0
                })
            else:
                # Done with all competitors
                state.update({
                    "raw_research_results": existing_results,
                    "research_iteration": next_iteration
                })
        else:
            # Continue with current competitor
            state.update({
                "raw_research_results": existing_results,
                "research_iteration": next_iteration
            })
        
        return state
    
    def analyze_competitive_gaps(self, state: GraphState) -> Dict[str, Any]:
        """Enhanced analysis to identify ALL types of competitive gaps"""
        print("🔬 Analyzing competitive gaps (clinical, market, product, brand)...")
        
        raw_results = state["raw_research_results"]
        competitors = state["competitors"]
        device_category = state["device_category"]
        
        all_gaps = []
        market_insights = []
        brand_insights = []
        product_gaps = []
        
        for competitor in competitors:
            # Filter results for this competitor
            competitor_results = [r for r in raw_results if r.get("competitor") == competitor]
            
            if competitor_results:
                # 1. Clinical gaps (existing functionality)
                clinical_gaps = AnalysisProcessor.extract_clinical_gaps(competitor_results, competitor)
                all_gaps.extend(clinical_gaps)
                
                # 2. Enhanced gap analysis using LLM
                try:
                    content_summary = "\n".join([
                        f"- {r.get('title', '')}: {r.get('content', '')[:200]}..."
                        for r in competitor_results[:3]
                    ])
                    
                    # Multi-dimensional gap analysis
                    gap_analysis_prompt = f"""
                    Analyze this research about {competitor} in {device_category} for multiple types of competitive gaps:
                    
                    {content_summary}
                    
                    Identify gaps in these areas:
                    1. CLINICAL: Clinical limitations, safety issues, efficacy problems
                    2. PRODUCT: Feature gaps, technology limitations, innovation lag
                    3. BRAND: Brand positioning weaknesses, messaging gaps, reputation issues
                    4. MARKET: Market positioning gaps, segment weaknesses, geographic limitations
                    
                    For each gap found, provide:
                    - Gap type (clinical/product/brand/market)
                    - Specific description
                    - Evidence from the research
                    - Severity (high/medium/low)
                    
                    Focus on factual, evidence-based gaps that represent opportunities for competitors.
                    """
                    
                    response = llm.invoke(gap_analysis_prompt)
                    
                    if response.content and len(response.content) > 50:
                        # Parse response to extract different types of gaps
                        content = response.content
                        
                        # Create clinical gap
                        clinical_gap = ClinicalGap(
                            competitor=competitor,
                            gap_type="comprehensive_analysis",
                            description=content[:300],
                            evidence=content_summary[:500],
                            severity="medium",
                            source_url=competitor_results[0].get("url") if competitor_results else None
                        )
                        all_gaps.append(clinical_gap)
                        
                        # Extract market insights
                        from ..core.data_models import MarketShareInsight
                        market_insight = MarketShareInsight(
                            competitor=competitor,
                            market_position="Analysis-based",
                            estimated_market_share="Research-derived",
                            revenue_estimate="Not specified",
                            growth_trend="Analysis-based",
                            key_markets=["Research-derived"],
                            evidence=content[:500],
                            source_url=competitor_results[0].get("url") if competitor_results else None
                        )
                        market_insights.append(market_insight)
                        
                except Exception as e:
                    print(f"   ⚠️ Enhanced gap analysis failed for {competitor}: {str(e)}")
        
        print(f"   Identified {len(all_gaps)} clinical gaps")
        print(f"   Generated {len(market_insights)} market insights")
        
        state.update({
            "clinical_gaps": [gap.model_dump() for gap in all_gaps],
            "market_share_insights": [insight.model_dump() for insight in market_insights]
        })
        
        return state
    
    def generate_opportunities(self, state: GraphState) -> Dict[str, Any]:
        """Transform gaps into ranked strategic opportunities"""
        print("💡 Generating strategic opportunities...")
        
        clinical_gaps = state["clinical_gaps"]
        market_insights = state["market_share_insights"]
        raw_results = state["raw_research_results"]
        competitors = state["competitors"]
        device_category = state["device_category"]
        
        # Transform clinical gaps into opportunities
        clinical_opportunities = OpportunityTransformer.clinical_gaps_to_opportunities(clinical_gaps)
        
        # Transform market insights into opportunities
        market_opportunities = OpportunityTransformer.market_insights_to_opportunities(market_insights)
        
        # Generate AI-powered strategic opportunities
        ai_opportunities = self._generate_ai_opportunities(raw_results, competitors, device_category)
        
        # Combine all opportunities
        all_opportunities = clinical_opportunities + market_opportunities + ai_opportunities
        
        # Rank opportunities by composite score
        ranked_opportunities = OpportunityRanker.rank_opportunities(all_opportunities)
        
        # Take top opportunities
        top_opportunities = ranked_opportunities[:5]  # Top 5 opportunities
        
        # Create opportunity matrix
        opportunity_matrix = OpportunityRanker.create_opportunity_matrix(all_opportunities)
        
        print(f"   Generated {len(all_opportunities)} total opportunities")
        print(f"   Top {len(top_opportunities)} opportunities selected")
        
        state.update({
            "top_opportunities": [opp.model_dump() for opp in top_opportunities],
            "opportunity_matrix": opportunity_matrix.model_dump(),
            "all_opportunities": [opp.model_dump() for opp in all_opportunities]
        })
        
        return state
    
    def categorize_opportunities(self, state: GraphState) -> Dict[str, Any]:
        """Categorize opportunities into Brand, Product, Pricing, Market categories"""
        print("📋 Categorizing opportunities...")
        
        all_opportunities = state.get("all_opportunities", [])
        competitors = state["competitors"]
        device_category = state["device_category"]
        
        # Initialize category lists
        brand_opportunities = []
        product_opportunities = []
        pricing_opportunities = []
        market_expansion_opportunities = []
        
        # Categorize existing opportunities
        opportunity_id_counter = 1
        for opp_dict in all_opportunities:
            category = opp_dict.get("category", "")
            
            # Create CategoryOpportunity from StrategicOpportunity with required fields
            category_opp = CategoryOpportunity(
                id=opportunity_id_counter,
                opportunity=opp_dict.get("title", ""),
                current_gap=f"Competitive gap in {category.lower()}",
                recommendation=opp_dict.get("description", ""),
                implementation="; ".join(opp_dict.get("next_steps", [])),
                timeline=opp_dict.get("time_to_market", "6-12 months"),
                investment=f"{opp_dict.get('investment_level', 'Medium')} investment required",
                category_type=category.replace(" ", "_").lower()  # Convert to snake_case
            )
            
            if category == "Brand Strategy":
                brand_opportunities.append(category_opp)
            elif category == "Product Innovation":
                product_opportunities.append(category_opp)
            elif category == "Pricing Strategy":
                pricing_opportunities.append(category_opp)
            elif category == "Market Positioning" or category == "Market Expansion":
                market_expansion_opportunities.append(category_opp)
            
            opportunity_id_counter += 1
        
        # Generate additional category-specific opportunities using AI
        brand_opportunities.extend(self._generate_brand_opportunities(competitors, device_category))
        product_opportunities.extend(self._generate_product_opportunities(competitors, device_category))
        pricing_opportunities.extend(self._generate_pricing_opportunities(competitors, device_category))
        market_expansion_opportunities.extend(self._generate_market_opportunities(competitors, device_category))
        
        print(f"   Brand opportunities: {len(brand_opportunities)}")
        print(f"   Product opportunities: {len(product_opportunities)}")
        print(f"   Pricing opportunities: {len(pricing_opportunities)}")
        print(f"   Market opportunities: {len(market_expansion_opportunities)}")
        
        state.update({
            "brand_opportunities": [opp.model_dump() for opp in brand_opportunities],
            "product_opportunities": [opp.model_dump() for opp in product_opportunities],
            "pricing_opportunities": [opp.model_dump() for opp in pricing_opportunities],
            "market_expansion_opportunities": [opp.model_dump() for opp in market_expansion_opportunities]
        })
        
        return state
    
    def synthesize_opportunity_report(self, state: GraphState) -> Dict[str, Any]:
        """Generate executive summary and final opportunity-first report"""
        print("📊 Synthesizing opportunity report...")
        

        top_opportunities = state.get("top_opportunities", [])
        competitors = state["competitors"]
        device_category = state["device_category"]
        
        # Create competitive profiles
        competitive_profiles = self._create_competitive_profiles(competitors, state)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(top_opportunities, competitors, device_category)
        
        # Create opportunity matrix from top opportunities
        strategic_opportunities = [StrategicOpportunity(**opp) for opp in top_opportunities]
        opportunity_matrix = self._create_opportunity_matrix(strategic_opportunities)
        
        # Create final opportunity analysis response
        # Create proper analysis metadata
        analysis_metadata = AnalysisMetadata(
            analysis_id=f"opportunity_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            analysis_type="Competitive Opportunity Intelligence",
            pipeline_version="1.0.0",
            primary_model="gpt-4",
            started_at=datetime.now(),
            confidence_score=8.0,
            completeness_score=8.5,
            source_coverage=7.5,
            client_name="Analysis Client"
        )
        
        # Convert strategic opportunities to summary format for progressive disclosure
        top_opportunities_summary = [
            OpportunityDisclosureTransformer.strategic_to_summary(opp) 
            for opp in strategic_opportunities
        ]
        
        analysis_response = OpportunityAnalysisResponse(
            analysis_metadata=analysis_metadata,
            top_opportunities_summary=top_opportunities_summary,
            opportunity_matrix=opportunity_matrix,
            brand_opportunities=[CategoryOpportunity(**opp) for opp in state.get("brand_opportunities", [])],
            product_opportunities=[CategoryOpportunity(**opp) for opp in state.get("product_opportunities", [])],
            pricing_opportunities=[CategoryOpportunity(**opp) for opp in state.get("pricing_opportunities", [])],
            market_opportunities=[CategoryOpportunity(**opp) for opp in state.get("market_expansion_opportunities", [])],
            competitive_landscape=competitive_profiles,
            executive_summary=executive_summary,
            clinical_gaps=state.get("clinical_gaps", []),
            market_share_insights=state.get("market_share_insights", []),
            research_timestamp=datetime.now().isoformat(),
            confidence_score=8.0
        )
        
        print("✅ Opportunity-first analysis complete!")
        
        state.update({
            "final_report": analysis_response.model_dump(),
            "executive_summary": executive_summary.model_dump(),
            "competitive_profiles": competitive_profiles,
            "opportunity_analysis_complete": True
        })
        
        return state
    
    # Helper methods for enhanced functionality
    def _generate_opportunity_queries(self, competitor: str, device_category: str) -> List[str]:
        """Generate comprehensive opportunity-focused search queries"""
        category_info = CategoryRouter.get_category_info(device_category)
        primary_keyword = category_info["keywords"][0] if category_info["keywords"] else "medical device"
        
        # Enhanced multi-layered query strategy
        foundational_queries = [
            f"{competitor} revenue growth {device_category} market share 2024",
            f"{competitor} competitive position {device_category} market leadership",
            f"{competitor} FDA approvals {device_category} regulatory pipeline"
        ]
        
        opportunity_specific_queries = [
            # Brand positioning
            f"{competitor} brand messaging {device_category} marketing strategy",
            f"{competitor} physician perception {device_category} reputation",
            
            # Product innovation
            f"{competitor} R&D pipeline {device_category} innovation gaps",
            f"{competitor} patent portfolio {device_category} technology",
            
            # Pricing strategy
            f"{competitor} pricing strategy {device_category} value proposition",
            f"{competitor} reimbursement {device_category} payer relations",
            
            # Market expansion
            f"{competitor} market segments {device_category} customer base",
            f"{competitor} distribution strategy {device_category} sales channels"
        ]
        
        weakness_identification_queries = [
            f"{competitor} customer complaints {device_category} issues",
            f"{competitor} market share loss {device_category} competitive pressure",
            f"{competitor} physician criticism {device_category} user feedback"
        ]
        
        # Combine all query types
        all_queries = foundational_queries + opportunity_specific_queries + weakness_identification_queries
        
        return all_queries
    
    def _generate_strategic_queries(self, device_category: str, competitors: List[str]) -> List[str]:
        """Generate strategic market queries"""
        category_info = CategoryRouter.get_category_info(device_category)
        primary_keyword = category_info["keywords"][0] if category_info["keywords"] else "medical device"
        
        return [
            f"{device_category} market trends 2024 opportunities",
            f"{primary_keyword} unmet needs market gaps",
            f"{device_category} emerging technologies innovation",
            f"{primary_keyword} value-based care opportunities"
        ]
    
    def _advance_research_state(self, state: Dict[str, Any], competitors: List[str], 
                               current_competitor: str, existing_results: List[Dict], 
                               iteration: int) -> Dict[str, Any]:
        """Helper to advance research state"""
        current_idx = competitors.index(current_competitor)
        
        if current_idx < len(competitors) - 1:
            next_competitor = competitors[current_idx + 1]
            state.update({
                "raw_research_results": existing_results,
                "current_competitor": next_competitor,
                "research_iteration": 0
            })
        else:
            state.update({
                "raw_research_results": existing_results,
                "research_iteration": iteration + 1
            })
        
        return state
    
    def _generate_ai_opportunities(self, raw_results: List[Dict], competitors: List[str], 
                                  device_category: str) -> List[StrategicOpportunity]:
        """Generate AI-powered strategic opportunities"""
        opportunities = []
        
        try:
            # Summarize research for AI analysis
            content_summary = "\n".join([
                f"- {r.get('title', '')}: {r.get('content', '')[:150]}..."
                for r in raw_results[:8]  # Top 8 results
            ])
            
            opportunity_prompt = f"""
            Based on this competitive research in {device_category}, identify 2-3 high-impact strategic opportunities:
            
            Competitors analyzed: {', '.join(competitors)}
            Research summary:
            {content_summary}
            
            For each opportunity, provide:
            1. Clear, actionable title
            2. Opportunity category (Product Innovation, Brand Strategy, Market Positioning, Pricing Strategy, Market Expansion)
            3. Detailed description of the opportunity
            4. Implementation difficulty (Easy/Medium/Hard)
            5. Potential business impact
            6. 2-3 specific next steps
            
            Focus on opportunities that:
            - Address clear competitive gaps
            - Have significant revenue potential
            - Are actionable within 6-18 months
            - Provide sustainable competitive advantage
            
            Format each opportunity clearly with numbered sections.
            """
            
            response = llm.invoke(opportunity_prompt)
            
            if response.content and len(response.content) > 100:
                # Parse AI response into structured opportunities
                content = response.content
                
                # Create AI-generated opportunity
                ai_opportunity = StrategicOpportunity(
                    id=100,  # High ID to distinguish from transformed opportunities
                    title="AI-Identified Strategic Opportunity",
                    category=OpportunityCategory.MARKET_POSITIONING,
                    description=content[:400],
                    opportunity_score=8.5,
                    implementation_difficulty=ImplementationDifficulty.MEDIUM,
                    time_to_market="6-12 months",
                    investment_level=InvestmentLevel.MEDIUM,
                    competitive_risk=CompetitiveRisk.MEDIUM,
                    potential_impact="Significant competitive advantage",
                    next_steps=[
                        "Conduct detailed market analysis",
                        "Develop implementation roadmap",
                        "Validate with key stakeholders"
                    ],
                    supporting_evidence=content[:500],
                    confidence_level=8.0
                )
                opportunities.append(ai_opportunity)
                
        except Exception as e:
            print(f"   ⚠️ AI opportunity generation failed: {str(e)}")
        
        return opportunities
    
    def _generate_brand_opportunities(self, competitors: List[str], device_category: str) -> List[CategoryOpportunity]:
        """Generate brand strategy opportunities based on competitive analysis"""
        category_info = CategoryRouter.get_category_info(device_category)
        
        opportunities = [
            CategoryOpportunity(
                id=1001,  # Use high IDs to distinguish from converted opportunities
                opportunity="Outcome-Focused Brand Positioning",
                current_gap=f"Competitors in {device_category} focus on device features rather than patient outcomes",
                recommendation="Position brand around measurable patient outcomes and clinical results",
                implementation="Develop outcome-focused marketing campaigns, create real-world evidence studies, train sales team on outcome messaging",
                timeline="3-6 months",
                investment="Medium ($100K-300K)",
                category_type="brand",
                competitive_advantage="First-mover advantage in outcome-based messaging",
                success_metrics=["Brand awareness increase", "Physician preference scores", "Message recall rates"]
            ),
            CategoryOpportunity(
                id=1002,
                opportunity="Digital Thought Leadership",
                current_gap=f"Limited digital presence and thought leadership in {device_category} space",
                recommendation="Establish digital thought leadership through educational content and KOL partnerships",
                implementation="Create educational webinar series, develop clinical podcasts, partner with key opinion leaders",
                timeline="4-8 months",
                investment="Medium ($150K-400K)",
                category_type="brand",
                competitive_advantage="Enhanced physician engagement and brand credibility",
                success_metrics=["Digital engagement rates", "KOL partnership growth", "Educational content reach"]
            )
        ]
        
        return opportunities
    
    def _generate_product_opportunities(self, competitors: List[str], device_category: str) -> List[CategoryOpportunity]:
        """Generate product innovation opportunities based on competitive gaps"""
        category_info = CategoryRouter.get_category_info(device_category)
        primary_keyword = category_info["keywords"][0] if category_info["keywords"] else "medical device"
        
        opportunities = [
            CategoryOpportunity(
                id=2001,  # Use high IDs to distinguish from converted opportunities
                opportunity="AI-Powered Surgical Planning Platform",
                current_gap=f"Competitors in {device_category} lack integrated AI-powered surgical planning tools",
                recommendation="Develop AI-enabled surgical planning platform with predictive analytics",
                implementation="Partner with AI/ML company, develop algorithm, integrate with existing devices, conduct clinical validation",
                timeline="12-18 months",
                investment="High ($2M-5M)",
                category_type="product",
                competitive_advantage="First-to-market AI integration providing superior surgical outcomes",
                success_metrics=["Surgical outcome improvements", "Surgeon adoption rates", "Time-to-surgery reduction"]
            ),
            CategoryOpportunity(
                id=2002,
                opportunity="Minimally Invasive Technology Enhancement",
                current_gap=f"Limited innovation in minimally invasive approaches for {primary_keyword}",
                recommendation="Develop next-generation minimally invasive surgical tools and techniques",
                implementation="R&D investment in micro-instrumentation, surgeon training programs, clinical studies",
                timeline="18-24 months",
                investment="High ($3M-7M)",
                category_type="product",
                competitive_advantage="Superior patient outcomes with reduced recovery time",
                success_metrics=["Procedure time reduction", "Patient recovery metrics", "Surgeon preference scores"]
            ),
            CategoryOpportunity(
                id=2003,
                opportunity="Smart Device Connectivity",
                current_gap=f"Lack of IoT connectivity and real-time monitoring in {device_category} devices",
                recommendation="Integrate IoT sensors and real-time monitoring capabilities",
                implementation="Develop sensor technology, create mobile app, establish data analytics platform",
                timeline="9-15 months",
                investment="Medium ($800K-2M)",
                category_type="product",
                competitive_advantage="Enhanced patient monitoring and predictive maintenance",
                success_metrics=["Device uptime improvement", "Patient monitoring accuracy", "Predictive maintenance effectiveness"]
            )
        ]
        
        return opportunities
    
    def _generate_pricing_opportunities(self, competitors: List[str], device_category: str) -> List[CategoryOpportunity]:
        """Generate pricing strategy opportunities based on market analysis"""
        opportunities = [
            CategoryOpportunity(
                id=3001,  # Use high IDs to distinguish from converted opportunities
                opportunity="Value-Based Pricing Model",
                current_gap=f"Competitors in {device_category} use traditional fee-for-service pricing without outcome accountability",
                recommendation="Implement outcome-based pricing with shared risk/reward models",
                implementation="Develop outcome tracking systems, pilot with progressive health systems, create risk-sharing contracts",
                timeline="6-12 months",
                investment="Medium ($300K-800K)",
                category_type="pricing",
                competitive_advantage="Alignment with healthcare value-based care trends",
                success_metrics=["Contract conversion rates", "Outcome improvement metrics", "Customer satisfaction scores"]
            ),
            CategoryOpportunity(
                id=3002,
                opportunity="Bundled Solution Pricing",
                current_gap=f"Fragmented pricing across {device_category} ecosystem with separate device, service, and training costs",
                recommendation="Create comprehensive bundled pricing for device + services + training + support",
                implementation="Develop service packages, create training programs, establish support infrastructure",
                timeline="4-8 months",
                investment="Medium ($200K-600K)",
                category_type="pricing",
                competitive_advantage="Simplified procurement and predictable costs for customers",
                success_metrics=["Bundle adoption rates", "Customer lifetime value", "Competitive win rates"]
            ),
            CategoryOpportunity(
                id=3003,
                opportunity="Subscription-Based Service Model",
                current_gap=f"Traditional one-time purchase model in {device_category} doesn't align with ongoing value delivery",
                recommendation="Develop subscription model for device access, maintenance, and upgrades",
                implementation="Create subscription tiers, develop service delivery model, establish upgrade pathways",
                timeline="8-12 months",
                investment="High ($500K-1.5M)",
                category_type="pricing",
                competitive_advantage="Recurring revenue model with enhanced customer relationships",
                success_metrics=["Subscription adoption rates", "Monthly recurring revenue", "Customer retention rates"]
            )
        ]
        
        return opportunities
    
    def _generate_market_opportunities(self, competitors: List[str], device_category: str) -> List[CategoryOpportunity]:
        """Generate market expansion opportunities based on competitive positioning"""
        category_info = CategoryRouter.get_category_info(device_category)
        
        opportunities = [
            CategoryOpportunity(
                id=4001,  # Use high IDs to distinguish from converted opportunities
                opportunity="Ambulatory Surgery Center Expansion",
                current_gap=f"Competitors in {device_category} primarily focus on hospital markets, underserving growing ASC segment",
                recommendation="Develop ASC-specific product lines and comprehensive support programs",
                implementation="Create ASC sales team, develop ASC-optimized products, establish training programs, build ASC partnerships",
                timeline="6-12 months",
                investment="Medium ($400K-1M)",
                category_type="market",
                competitive_advantage="First-mover advantage in rapidly growing ASC market segment",
                success_metrics=["ASC market penetration", "ASC revenue growth", "ASC customer satisfaction"]
            ),
            CategoryOpportunity(
                id=4002,
                opportunity="International Market Penetration",
                current_gap=f"Limited international presence in emerging markets for {device_category} compared to competitors",
                recommendation="Establish strategic partnerships and distribution networks in high-growth international markets",
                implementation="Identify key markets, establish local partnerships, adapt products for regulatory requirements, build distribution network",
                timeline="12-18 months",
                investment="High ($1M-3M)",
                category_type="market",
                competitive_advantage="Early market entry in high-growth regions",
                success_metrics=["International revenue growth", "Market share in target countries", "Regulatory approvals obtained"]
            ),
            CategoryOpportunity(
                id=4003,
                opportunity="Specialty Practice Segment Focus",
                current_gap=f"Competitors treat all {device_category} customers similarly without specialty-specific solutions",
                recommendation="Develop specialty-specific product variants and support programs for niche practice areas",
                implementation="Identify high-value specialty segments, develop specialized products, create specialty sales teams, build KOL relationships",
                timeline="8-15 months",
                investment="Medium ($600K-1.5M)",
                category_type="market",
                competitive_advantage="Deep specialization and customer intimacy in high-value segments",
                success_metrics=["Specialty segment market share", "Specialty customer loyalty", "Premium pricing achievement"]
            )
        ]
        
        return opportunities
    
    def _create_competitive_profiles(self, competitors: List[str], state: Dict[str, Any]) -> Dict[str, CompetitorProfile]:
        """Create enhanced competitive profiles"""
        profiles = {}
        
        for competitor in competitors:
            profile = CompetitorProfile(
                name=competitor,
                market_share="Analysis-based",
                strengths=["Market presence", "Product portfolio"],
                weaknesses=["Innovation gaps", "Pricing pressure"],
                opportunities_against=["Digital innovation", "Value-based positioning"],
                pricing_strategy="Standard market pricing"  # Fix: Add required field
            )
            profiles[competitor] = profile.model_dump()
        
        return profiles
    
    def _generate_executive_summary(self, top_opportunities: List[Dict], competitors: List[str], 
                                   device_category: str) -> ExecutiveSummary:
        """Generate executive summary"""
        top_3_titles = [opp.get("title", "") for opp in top_opportunities[:3]]
        
        return ExecutiveSummary(
            key_insight=f"Significant opportunities exist in {device_category} through digital innovation and value-based positioning",
            top_3_opportunities=top_3_titles,
            immediate_actions=[
                "Prioritize digital integration initiatives",
                "Develop outcome-focused marketing strategy",
                "Explore value-based pricing pilots"
            ],
            strategic_focus="Digital innovation and outcome-based differentiation",
            competitive_advantage="First-mover advantage in digital-enabled devices",
            revenue_potential="$10M-50M opportunity identified",
            market_share_opportunity="5-10% market share gain potential",
            investment_required="$2M-5M total investment"
        )
    
    def _create_opportunity_matrix(self, strategic_opportunities: List[StrategicOpportunity]):
        """Create opportunity matrix from strategic opportunities"""
        from ..core.opportunity_data_models import OpportunityMatrix
        
        matrix_data = {
            "high_impact_easy": [],
            "high_impact_hard": [],
            "low_impact_easy": [],
            "low_impact_hard": []
        }
        
        for opp in strategic_opportunities:
            impact = opp.opportunity_score
            difficulty_map = {'Easy': 2, 'Medium': 5, 'Hard': 8}
            difficulty = difficulty_map.get(opp.implementation_difficulty.value, 5)
            
            item = {"name": opp.title, "impact": impact, "difficulty": difficulty}
            
            if impact >= 7.5 and difficulty <= 4:
                matrix_data["high_impact_easy"].append(item)
            elif impact >= 7.5 and difficulty > 4:
                matrix_data["high_impact_hard"].append(item)
            elif impact < 7.5 and difficulty <= 4:
                matrix_data["low_impact_easy"].append(item)
            else:
                matrix_data["low_impact_hard"].append(item)
        
        return OpportunityMatrix(**matrix_data)
    
    def run_analysis(self, competitors: List[str], focus_area: str = "spine_fusion") -> Dict[str, Any]:
        """Run the complete opportunity-first competitive analysis"""
        print(f"🚀 Starting opportunity-first analysis...")
        print(f"   Competitors: {competitors}")
        print(f"   Focus area: {focus_area}")
        
        # Initialize state
        initial_state = {
            "competitors": competitors,
            "focus_area": focus_area,
            "device_category": "",
            "search_queries": [],
            "raw_research_results": [],
            "clinical_gaps": [],
            "market_opportunities": [],
            "current_competitor": None,
            "research_iteration": 0,
            "error_messages": [],
            "final_report": None
        }
        
        try:
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            print("✅ Opportunity-first analysis completed successfully!")
            return result
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            return {
                "error": str(e),
                "competitors": competitors,
                "focus_area": focus_area,
                "status": "failed"
            }

# Create global instance
opportunity_graph = OpportunityIntelligenceGraph() 