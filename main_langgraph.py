# main_langgraph.py
"""
Core LangGraph implementation for orthopedic competitive intelligence
"""

import os
from typing import List, Dict, Any, Literal
from langgraph.graph import StateGraph
from langgraph.types import Command
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

from data_models import (
    GraphState, 
    SearchTemplates, 
    AnalysisProcessor,
    ClinicalGap,
    MarketOpportunity,
    Config,
    CategoryRouter
)

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

class OrthopedicIntelligenceGraph:
    """Main LangGraph implementation for competitive intelligence"""
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("detect_category", self.detect_category)
        workflow.add_node("initialize", self.initialize_research)
        workflow.add_node("research_competitor", self.research_competitor)
        workflow.add_node("analyze_gaps", self.analyze_gaps)
        workflow.add_node("market_share_analysis", self.market_share_analysis)  # NEW: Market intelligence
        workflow.add_node("identify_opportunities", self.identify_opportunities)
        workflow.add_node("synthesize_report", self.synthesize_report)
        
        # Set entry point
        workflow.set_entry_point("detect_category")
        
        # Compile and return
        return workflow.compile()
    
    def detect_category(self, state: GraphState) -> Command[Literal["initialize"]]:
        """Detect device category based on competitors and context"""
        competitors = state["competitors"]
        focus_area = state["focus_area"]
        
        # Detect category using CategoryRouter
        detected_category = CategoryRouter.detect_category(competitors, focus_area)
        
        print(f"🎯 Category detected: {detected_category}")
        print(f"   Competitors: {competitors}")
        print(f"   Context: {focus_area}")
        
        return Command(
            update={"device_category": detected_category},
            goto="initialize"
        )
    
    def initialize_research(self, state: GraphState) -> Command[Literal["research_competitor"]]:
        """Initialize the research process"""
        competitors = state["competitors"]
        focus_area = state["focus_area"]
        device_category = state["device_category"]
        
        print(f"🔍 Starting analysis for {len(competitors)} competitors in {device_category}")
        
        # Generate search queries using detected category
        all_queries = []
        for competitor in competitors:
            competitor_queries = SearchTemplates.get_competitor_queries(competitor, focus_area, device_category)
            all_queries.extend(competitor_queries)
        
        # Add market-level queries
        market_queries = SearchTemplates.get_market_queries(focus_area, device_category)
        all_queries.extend(market_queries)
        
        return Command(
            update={
                "search_queries": all_queries,
                "current_competitor": competitors[0],
                "research_iteration": 0,
                "raw_research_results": [],
                "clinical_gaps": [],
                "market_opportunities": [],
                "error_messages": []
            },
            goto="research_competitor"
        )
    
    def research_competitor(self, state: GraphState) -> Command[Literal["research_competitor", "analyze_gaps"]]:
        """Research individual competitor using Tavily"""
        current_competitor = state["current_competitor"]
        competitors = state["competitors"]
        iteration = state["research_iteration"]
        existing_results = state["raw_research_results"]
        
        print(f"📊 Researching {current_competitor} (iteration {iteration + 1})")
        
        try:
            # Generate competitor-specific query using detected category
            device_category = state["device_category"]
            competitor_queries = SearchTemplates.get_competitor_queries(current_competitor, state["focus_area"], device_category)
            
            if iteration < len(competitor_queries):
                query = competitor_queries[iteration]
            else:
                # Fallback query based on category
                category_info = CategoryRouter.get_category_info(device_category)
                primary_keyword = category_info["keywords"][0] if category_info["keywords"] else "medical device"
                query = f"{current_competitor} {primary_keyword} clinical issues 2024"
            
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
            return Command(
                update={
                    "error_messages": state["error_messages"] + [error_msg],
                    "research_iteration": iteration + 1
                },
                goto="analyze_gaps" if iteration >= 2 else "research_competitor"
            )
        
        # Decide next action
        next_iteration = iteration + 1
        current_idx = competitors.index(current_competitor)
        
        if next_iteration >= 3:  # Max 3 searches per competitor
            if current_idx < len(competitors) - 1:
                # Move to next competitor
                next_competitor = competitors[current_idx + 1]
                return Command(
                    update={
                        "raw_research_results": existing_results,
                        "current_competitor": next_competitor,
                        "research_iteration": 0
                    },
                    goto="research_competitor"
                )
            else:
                # Done with all competitors
                return Command(
                    update={
                        "raw_research_results": existing_results,
                        "research_iteration": next_iteration
                    },
                    goto="analyze_gaps"
                )
        else:
            # Continue with current competitor
            return Command(
                update={
                    "raw_research_results": existing_results,
                    "research_iteration": next_iteration
                },
                goto="research_competitor"
            )
    
    def analyze_gaps(self, state: GraphState) -> Command[Literal["market_share_analysis"]]:
        """Analyze research results to identify clinical gaps"""
        print("🔬 Analyzing clinical gaps...")
        
        raw_results = state["raw_research_results"]
        competitors = state["competitors"]
        all_gaps = []
        
        for competitor in competitors:
            # Filter results for this competitor
            competitor_results = [r for r in raw_results if r.get("competitor") == competitor]
            
            # Extract gaps using our processor
            gaps = AnalysisProcessor.extract_clinical_gaps(competitor_results, competitor)
            all_gaps.extend(gaps)
            
            # Enhanced gap analysis using LLM
            if competitor_results:
                try:
                    # Prepare content for LLM analysis
                    content_summary = "\n".join([
                        f"- {r.get('title', '')}: {r.get('content', '')[:200]}..."
                        for r in competitor_results[:3]
                    ])
                    
                    gap_analysis_prompt = f"""
                    Analyze this research about {competitor} for clinical gaps and limitations:
                    
                    {content_summary}
                    
                    Identify specific clinical limitations, regulatory issues, or competitive weaknesses.
                    Focus on factual, evidence-based gaps. Format as brief bullet points.
                    """
                    
                    response = llm.invoke(gap_analysis_prompt)
                    
                    # Create structured gap from LLM analysis
                    if response.content and len(response.content) > 50:
                        llm_gap = ClinicalGap(
                            competitor=competitor,
                            gap_type="clinical_analysis",
                            description=response.content[:300],
                            evidence=content_summary[:500],
                            severity="medium",
                            source_url=competitor_results[0].get("url") if competitor_results else None
                        )
                        all_gaps.append(llm_gap)
                        
                except Exception as e:
                    print(f"   ⚠️ LLM analysis failed for {competitor}: {str(e)}")
        
        print(f"   Identified {len(all_gaps)} clinical gaps")
        
        return Command(
            update={"clinical_gaps": [gap.model_dump() for gap in all_gaps]},
            goto="market_share_analysis"
        )
    
    def market_share_analysis(self, state: GraphState) -> Command[Literal["identify_opportunities"]]:
        """NEW: Analyze market share and positioning insights"""
        print("📈 Analyzing market share and positioning...")
        
        raw_results = state["raw_research_results"]
        competitors = state["competitors"]
        device_category = state["device_category"]
        all_insights = []
        
        for competitor in competitors:
            # Filter results for this competitor
            competitor_results = [r for r in raw_results if r.get("competitor") == competitor]
            
            if competitor_results:
                try:
                    # Prepare content for market share analysis
                    content_summary = "\n".join([
                        f"- {r.get('title', '')}: {r.get('content', '')[:200]}..."
                        for r in competitor_results[:3]
                    ])
                    
                    market_analysis_prompt = f"""
                    Analyze this research about {competitor} in {device_category} for market positioning and share insights:
                    
                    {content_summary}
                    
                    Extract specific information about:
                    1. Market position (leader/challenger/follower/niche)
                    2. Estimated market share or revenue indicators
                    3. Growth trends (growing/stable/declining)
                    4. Key geographic or segment markets
                    
                    Provide factual, evidence-based insights. If specific data isn't available, indicate "Not specified" rather than guessing.
                    Format as structured bullet points.
                    """
                    
                    response = llm.invoke(market_analysis_prompt)
                    
                    if response.content and len(response.content) > 50:
                        # Parse the response to extract structured data
                        content = response.content
                        
                        # Extract market position
                        market_position = "Not specified"
                        if "leader" in content.lower():
                            market_position = "Market Leader"
                        elif "challenger" in content.lower():
                            market_position = "Challenger"
                        elif "follower" in content.lower():
                            market_position = "Follower"
                        elif "niche" in content.lower():
                            market_position = "Niche Player"
                        
                        # Extract growth trend
                        growth_trend = "Not specified"
                        if "growing" in content.lower() or "growth" in content.lower():
                            growth_trend = "Growing"
                        elif "declining" in content.lower() or "decline" in content.lower():
                            growth_trend = "Declining"
                        elif "stable" in content.lower():
                            growth_trend = "Stable"
                        
                        # Create market share insight
                        from data_models import MarketShareInsight
                        insight = MarketShareInsight(
                            competitor=competitor,
                            market_position=market_position,
                            estimated_market_share="Analysis-based",
                            revenue_estimate="Not specified",
                            growth_trend=growth_trend,
                            key_markets=["Analysis-based"],
                            evidence=content[:500],
                            source_url=competitor_results[0].get("url") if competitor_results else None
                        )
                        all_insights.append(insight)
                        
                except Exception as e:
                    print(f"   ⚠️ Market share analysis failed for {competitor}: {str(e)}")
        
        print(f"   Generated {len(all_insights)} market share insights")
        
        return Command(
            update={"market_share_insights": [insight.model_dump() for insight in all_insights]},
            goto="identify_opportunities"
        )
    
    def identify_opportunities(self, state: GraphState) -> Command[Literal["synthesize_report"]]:
        """Identify market opportunities from research data"""
        print("💡 Identifying market opportunities...")
        
        raw_results = state["raw_research_results"]
        
        # Extract opportunities using processor
        opportunities = AnalysisProcessor.extract_market_opportunities(raw_results)
        
        # Enhanced opportunity analysis with LLM
        try:
            # Summarize all research for opportunity identification
            all_content = "\n".join([
                f"- {r.get('title', '')}: {r.get('content', '')[:150]}..."
                for r in raw_results[:5]  # Top 5 results
            ])
            
            opportunity_prompt = f"""
            Based on this competitive research in orthopedic spine fusion, identify market opportunities:
            
            {all_content}
            
            Look for:
            1. Unmet clinical needs
            2. Technology gaps
            3. Market segments with weak competition
            4. Emerging trends
            
            Provide 2-3 specific, actionable opportunities. Be concise and evidence-based.
            """
            
            response = llm.invoke(opportunity_prompt)
            
            if response.content and len(response.content) > 50:
                llm_opportunity = MarketOpportunity(
                    opportunity_type="market_analysis",
                    description=response.content[:400],
                    market_size_indicator="Analysis-based",
                    competitive_landscape="Mixed",
                    evidence=all_content[:500],
                    source_url="Multiple sources"
                )
                opportunities.append(llm_opportunity)
                
        except Exception as e:
            print(f"   ⚠️ LLM opportunity analysis failed: {str(e)}")
        
        print(f"   Identified {len(opportunities)} market opportunities")
        
        return Command(
            update={"market_opportunities": [opp.model_dump() for opp in opportunities]},
            goto="synthesize_report"
        )
    
    def synthesize_report(self, state: GraphState) -> Command[Literal["__end__"]]:
        """Generate final competitive intelligence report"""
        print("📝 Synthesizing final report...")
        
        competitors = state["competitors"]
        gaps = state["clinical_gaps"]
        opportunities = state["market_opportunities"]
        # NEW: Market intelligence data
        market_insights = state["market_share_insights"]
        brand_positioning = state["brand_positioning"]
        feature_gaps = state["product_feature_gaps"]
        competitive_landscape = state["competitive_landscape"]
        
        # Generate executive summary
        try:
            summary_prompt = f"""
            Create an executive summary for a competitive intelligence report on {', '.join(competitors)} 
            in {state.get('device_category', 'medical devices')}.
            
            Key findings:
            - {len(gaps)} clinical gaps identified
            - {len(opportunities)} market opportunities found
            - {len(market_insights)} market share insights generated
            - Brand positioning analysis: {'completed' if brand_positioning else 'pending'}
            
            Clinical Gaps: {gaps[:1] if gaps else 'None identified'}
            Market Opportunities: {opportunities[:1] if opportunities else 'None identified'}
            Market Insights: {market_insights[:1] if market_insights else 'None identified'}
            
            Write a 2-3 sentence executive summary for marketing professionals.
            Focus on actionable insights for product positioning and market strategy.
            Include both clinical and market intelligence findings.
            """
            
            response = llm.invoke(summary_prompt)
            summary = response.content if response.content else "Analysis completed with limited findings."
            
        except Exception as e:
            summary = f"Competitive analysis completed for {', '.join(competitors)} with {len(gaps)} gaps and {len(opportunities)} opportunities identified."
            print(f"   ⚠️ Summary generation failed: {str(e)}")
        
        # Build final report
        final_report = {
            "competitors_analyzed": competitors,
            "clinical_gaps": gaps,
            "market_opportunities": opportunities,
            # NEW: Market intelligence results
            "market_share_insights": market_insights,
            "brand_positioning": brand_positioning,
            "product_feature_gaps": feature_gaps,
            "competitive_landscape": competitive_landscape,
            "summary": summary,
            "research_timestamp": "2025-05-25",  # Could use datetime.now()
            "total_sources_analyzed": len(state["raw_research_results"]),
            "analysis_metadata": {
                "total_searches": len(state["search_queries"]),
                "successful_searches": len(state["raw_research_results"]),
                "errors_encountered": len(state["error_messages"])
            }
        }
        
        print(f"✅ Report generated: {len(gaps)} gaps, {len(opportunities)} opportunities, {len(market_insights)} market insights")
        
        return Command(
            update={"final_report": final_report},
            goto="__end__"
        )
    
    def run_analysis(self, competitors: List[str], focus_area: str = "spine_fusion") -> Dict[str, Any]:
        """Execute the full competitive intelligence analysis"""
        
        initial_state = {
            "competitors": competitors,
            "focus_area": focus_area,
            "device_category": "",  # Will be auto-detected
            "search_queries": [],
            "raw_research_results": [],
            "clinical_gaps": [],
            "market_opportunities": [],
            # NEW: Market intelligence fields
            "market_share_insights": [],
            "brand_positioning": [],
            "product_feature_gaps": [],
            "competitive_landscape": None,
            "final_report": None,
            "current_competitor": None,
            "research_iteration": 0,
            "error_messages": []
        }
        
        print(f"🚀 Starting competitive intelligence analysis...")
        print(f"   Competitors: {competitors}")
        print(f"   Focus Area: {focus_area}")
        
        try:
            # Execute the graph
            result = self.graph.invoke(initial_state)
            
            final_report = result.get("final_report")
            if final_report:
                print("\n🎯 Analysis Complete!")
                print(f"   📊 {len(final_report['clinical_gaps'])} clinical gaps identified")
                print(f"   💡 {len(final_report['market_opportunities'])} opportunities found")
                return final_report
            else:
                raise Exception("No final report generated")
                
        except Exception as e:
            print(f"\n❌ Analysis failed: {str(e)}")
            # Return partial results if available
            return {
                "competitors_analyzed": competitors,
                "clinical_gaps": [],
                "market_opportunities": [],
                "summary": f"Analysis failed: {str(e)}",
                "research_timestamp": "2025-05-25",
                "error": str(e)
            }

# Initialize the graph
intelligence_graph = OrthopedicIntelligenceGraph()

if __name__ == "__main__":
    # Quick test
    from test_dataset import get_test_request
    
    test_req = get_test_request()
    result = intelligence_graph.run_analysis(
        competitors=test_req.competitors,
        focus_area=test_req.focus_area
    )
    
    print("\n" + "="*50)
    print("TEST RESULT SUMMARY:")
    print("="*50)
    print(f"Summary: {result.get('summary', 'No summary')}")
    print(f"Gaps found: {len(result.get('clinical_gaps', []))}")
    print(f"Opportunities found: {len(result.get('market_opportunities', []))}")