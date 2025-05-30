# main_langgraph_opportunity_enhanced.py
"""
Enhanced Opportunity-First LangGraph implementation with client context support
Transforms clinical gaps into strategic opportunities with executive-ready insights
"""

import os
from typing import List, Dict, Any, Literal, Optional
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

class EnhancedOpportunityIntelligenceGraph:
    """Enhanced LangGraph implementation for opportunity-first competitive intelligence with client context"""
    
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
        client_name = state.get("client_name", "")
        
        # Detect category using CategoryRouter
        detected_category = CategoryRouter.detect_category(competitors, focus_area)
        
        print(f"🎯 Category detected: {detected_category}")
        print(f"   Client: {client_name if client_name else 'Not specified'}")
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
        client_name = state.get("client_name", "")
        
        print(f"🔍 Starting opportunity-first analysis for {len(competitors)} competitors in {device_category}")
        if client_name:
            print(f"   Client context: {client_name}")
        
        # Generate enhanced search queries for opportunity discovery
        all_queries = []
        for competitor in competitors:
            # Get standard competitor queries
            competitor_queries = SearchTemplates.get_competitor_queries(competitor, focus_area, device_category)
            all_queries.extend(competitor_queries)
            
            # Add opportunity-focused queries
            opportunity_queries = self._generate_opportunity_queries(competitor, device_category)
            all_queries.extend(opportunity_queries)
            
            # Add client-specific queries if client name provided
            if client_name:
                client_queries = self._generate_client_specific_queries(competitor, client_name, device_category)
                all_queries.extend(client_queries)
        
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
        client_name = state.get("client_name", "")
        
        print(f"📊 Researching {current_competitor} (iteration {iteration + 1})")
        if client_name:
            print(f"   Client context: {client_name}")
        
        try:
            # Generate competitor-specific query using detected category
            device_category = state["device_category"]
            competitor_queries = SearchTemplates.get_competitor_queries(current_competitor, state["focus_area"], device_category)
            
            # Add opportunity-focused queries
            opportunity_queries = self._generate_opportunity_queries(current_competitor, device_category)
            all_queries = competitor_queries + opportunity_queries
            
            # Add client-specific queries if available
            if client_name:
                client_queries = self._generate_client_specific_queries(current_competitor, client_name, device_category)
                all_queries.extend(client_queries)
            
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
                            "score": result.get("score", 0),
                            "client_context": client_name
                        })
                
                existing_results.extend(processed_results)
                print(f"   Found {len(processed_results)} results")
            
        except Exception as e:
            error_msg = f"Research failed for {current_competitor}: {str(e)}"
            print(f"   ❌ {error_msg}")
            state["error_messages"] = state["error_messages"] + [error_msg]
            state["research_iteration"] = iteration + 1
            return state
        
        # Advance to next state
        return self._advance_research_state(state, competitors, current_competitor, existing_results, iteration)
    
    def analyze_competitive_gaps(self, state: GraphState) -> Dict[str, Any]:
        """Analyze competitive gaps with enhanced opportunity focus"""
        raw_results = state["raw_research_results"]
        competitors = state["competitors"]
        device_category = state["device_category"]
        client_name = state.get("client_name", "")
        
        print(f"🔍 Analyzing competitive gaps for {len(competitors)} competitors")
        if client_name:
            print(f"   Client perspective: {client_name}")
        
        try:
            # Enhanced gap analysis with client context
            gap_analysis_prompt = f"""
            Analyze competitive gaps in {device_category} market for the following competitors: {', '.join(competitors)}
            
            {"Client context: " + client_name if client_name else ""}
            
            Based on this research data, identify:
            1. Clinical gaps and unmet needs
            2. Market positioning gaps
            3. Technology/innovation gaps
            4. Pricing and value proposition gaps
            5. Customer service and support gaps
            
            Research summary:
            {self._summarize_research_results(raw_results[:10])}
            
            For each gap, provide:
            - Gap type and description
            - Severity (high/medium/low)
            - Market opportunity size
            - Competitive advantage potential
            - Implementation complexity
            
            Focus on actionable gaps that represent clear opportunities.
            """
            
            response = llm.invoke(gap_analysis_prompt)
            
            if response.content and len(response.content) > 100:
                # Transform gaps into opportunities using enhanced transformer
                clinical_gaps = self._parse_gaps_from_response(response.content, "clinical")
                market_gaps = self._parse_gaps_from_response(response.content, "market")
                
                # Convert gaps to opportunities with client context
                clinical_opportunities = OpportunityTransformer.clinical_gaps_to_opportunities(clinical_gaps)
                market_opportunities = OpportunityTransformer.market_insights_to_opportunities(market_gaps)
                
                # Add client context to opportunities
                if client_name:
                    for opp in clinical_opportunities + market_opportunities:
                        opp.supporting_evidence = f"Analysis for {client_name}: {opp.supporting_evidence}"
                
                state.update({
                    "clinical_gaps": clinical_gaps,
                    "market_opportunities": market_gaps,
                    "preliminary_opportunities": clinical_opportunities + market_opportunities
                })
                
                print(f"   Found {len(clinical_gaps)} clinical gaps and {len(market_gaps)} market gaps")
            
        except Exception as e:
            error_msg = f"Gap analysis failed: {str(e)}"
            print(f"   ❌ {error_msg}")
            state["error_messages"] = state["error_messages"] + [error_msg]
        
        return state
    
    def generate_opportunities(self, state: GraphState) -> Dict[str, Any]:
        """Generate strategic opportunities with client context"""
        raw_results = state["raw_research_results"]
        competitors = state["competitors"]
        device_category = state["device_category"]
        client_name = state.get("client_name", "")
        
        print(f"💡 Generating strategic opportunities")
        if client_name:
            print(f"   Tailored for: {client_name}")
        
        try:
            # Generate AI-powered opportunities with client context
            ai_opportunities = self._generate_ai_opportunities_with_client_context(
                raw_results, competitors, device_category, client_name
            )
            
            # Combine with preliminary opportunities
            preliminary_opportunities = state.get("preliminary_opportunities", [])
            all_opportunities = preliminary_opportunities + ai_opportunities
            
            # Rank and prioritize opportunities
            ranked_opportunities = OpportunityRanker.rank_opportunities(all_opportunities)
            
            state.update({
                "top_opportunities": [opp.model_dump() for opp in ranked_opportunities[:5]],
                "all_opportunities": [opp.model_dump() for opp in all_opportunities]
            })
            
            print(f"   Generated {len(all_opportunities)} total opportunities")
            print(f"   Top 5 ranked opportunities identified")
            
        except Exception as e:
            error_msg = f"Opportunity generation failed: {str(e)}"
            print(f"   ❌ {error_msg}")
            state["error_messages"] = state["error_messages"] + [error_msg]
        
        return state
    
    def categorize_opportunities(self, state: GraphState) -> Dict[str, Any]:
        """Categorize opportunities by type with client context"""
        competitors = state["competitors"]
        device_category = state["device_category"]
        client_name = state.get("client_name", "")
        
        print(f"🎯 Categorizing opportunities by type")
        
        try:
            # Generate category-specific opportunities with client context
            brand_opportunities = self._generate_brand_opportunities_with_client(competitors, device_category, client_name)
            product_opportunities = self._generate_product_opportunities_with_client(competitors, device_category, client_name)
            pricing_opportunities = self._generate_pricing_opportunities_with_client(competitors, device_category, client_name)
            market_opportunities = self._generate_market_opportunities_with_client(competitors, device_category, client_name)
            
            # Create opportunity matrix
            all_strategic_opportunities = []
            for opp_dict in state.get("all_opportunities", []):
                try:
                    opp = StrategicOpportunity(**opp_dict)
                    all_strategic_opportunities.append(opp)
                except Exception:
                    continue
            
            opportunity_matrix = OpportunityRanker.create_opportunity_matrix(all_strategic_opportunities)
            
            state.update({
                "brand_opportunities": [opp.model_dump() for opp in brand_opportunities],
                "product_opportunities": [opp.model_dump() for opp in product_opportunities],
                "pricing_opportunities": [opp.model_dump() for opp in pricing_opportunities],
                "market_expansion_opportunities": [opp.model_dump() for opp in market_opportunities],
                "opportunity_matrix": opportunity_matrix.model_dump()
            })
            
            print(f"   Categorized opportunities across 4 categories")
            
        except Exception as e:
            error_msg = f"Opportunity categorization failed: {str(e)}"
            print(f"   ❌ {error_msg}")
            state["error_messages"] = state["error_messages"] + [error_msg]
        
        return state
    
    def synthesize_opportunity_report(self, state: GraphState) -> Dict[str, Any]:
        """Synthesize final opportunity report with client context"""
        competitors = state["competitors"]
        device_category = state["device_category"]
        client_name = state.get("client_name", "")
        top_opportunities = state.get("top_opportunities", [])
        
        print(f"📋 Synthesizing final opportunity report")
        if client_name:
            print(f"   Customized for: {client_name}")
        
        try:
            # Create competitive profiles
            competitive_profiles = self._create_competitive_profiles_with_client(competitors, state, client_name)
            
            # Generate executive summary with client context
            executive_summary = self._generate_executive_summary_with_client(
                top_opportunities, competitors, device_category, client_name
            )
            
            # Create final report structure
            final_report = {
                "analysis_metadata": {
                    "client_name": client_name,
                    "competitors": competitors,
                    "device_category": device_category,
                    "focus_area": state["focus_area"],
                    "analysis_date": datetime.now().isoformat(),
                    "total_opportunities": len(state.get("all_opportunities", [])),
                    "research_sources": len(state.get("raw_research_results", []))
                },
                "executive_summary": executive_summary.model_dump(),
                "top_opportunities": top_opportunities,
                "opportunity_matrix": state.get("opportunity_matrix", {}),
                "category_opportunities": {
                    "brand": state.get("brand_opportunities", []),
                    "product": state.get("product_opportunities", []),
                    "pricing": state.get("pricing_opportunities", []),
                    "market": state.get("market_expansion_opportunities", [])
                },
                "competitive_landscape": competitive_profiles,
                "confidence_score": 8.5
            }
            
            state.update({
                "final_report": final_report,
                "executive_summary": executive_summary.model_dump(),
                "competitive_landscape": competitive_profiles,
                "analysis_complete": True
            })
            
            print(f"✅ Final opportunity report completed")
            print(f"   Report includes {len(top_opportunities)} top opportunities")
            
        except Exception as e:
            error_msg = f"Report synthesis failed: {str(e)}"
            print(f"   ❌ {error_msg}")
            state["error_messages"] = state["error_messages"] + [error_msg]
        
        return state
    
    def _generate_opportunity_queries(self, competitor: str, device_category: str) -> List[str]:
        """Generate opportunity-focused search queries"""
        return [
            f"{competitor} {device_category} market gaps opportunities 2024",
            f"{competitor} competitive weaknesses {device_category}",
            f"{competitor} innovation gaps {device_category} market",
            f"{competitor} pricing strategy {device_category} opportunities"
        ]
    
    def _generate_client_specific_queries(self, competitor: str, client_name: str, device_category: str) -> List[str]:
        """Generate client-specific competitive queries"""
        return [
            f"{competitor} vs {client_name} {device_category} competitive analysis",
            f"{client_name} competitive position against {competitor}",
            f"{competitor} market share vs {client_name} {device_category}",
            f"{client_name} opportunities against {competitor} {device_category}"
        ]
    
    def _generate_strategic_queries(self, device_category: str, competitors: List[str]) -> List[str]:
        """Generate strategic market queries"""
        return [
            f"{device_category} market trends opportunities 2024",
            f"{device_category} unmet clinical needs market gaps",
            f"{device_category} digital innovation opportunities",
            f"{device_category} value-based care opportunities"
        ]
    
    def _advance_research_state(self, state: Dict[str, Any], competitors: List[str], 
                               current_competitor: str, existing_results: List[Dict], 
                               iteration: int) -> Dict[str, Any]:
        """Advance research state to next competitor or iteration"""
        
        # Update state with current results
        state["raw_research_results"] = existing_results
        
        # Determine next action
        if iteration + 1 < 3:  # Continue with current competitor
            state["research_iteration"] = iteration + 1
        else:
            # Move to next competitor
            current_index = competitors.index(current_competitor)
            if current_index + 1 < len(competitors):
                state["current_competitor"] = competitors[current_index + 1]
                state["research_iteration"] = 0
            else:
                # Research complete, move to analysis
                state["research_complete"] = True
        
        return state
    
    def _generate_ai_opportunities_with_client_context(self, raw_results: List[Dict], competitors: List[str], 
                                                      device_category: str, client_name: str = "") -> List[StrategicOpportunity]:
        """Generate AI-powered strategic opportunities with client context"""
        opportunities = []
        
        try:
            # Summarize research for AI analysis
            content_summary = "\n".join([
                f"- {r.get('title', '')}: {r.get('content', '')[:150]}..."
                for r in raw_results[:8]  # Top 8 results
            ])
            
            client_context = f"\nClient context: Analysis for {client_name}" if client_name else ""
            
            opportunity_prompt = f"""
            Based on this competitive research in {device_category}, identify 2-3 high-impact strategic opportunities:
            
            Competitors analyzed: {', '.join(competitors)}{client_context}
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
            {f"- Are specifically relevant for {client_name}" if client_name else ""}
            
            Format each opportunity clearly with numbered sections.
            """
            
            response = llm.invoke(opportunity_prompt)
            
            if response.content and len(response.content) > 100:
                # Parse AI response into structured opportunities
                content = response.content
                
                # Create AI-generated opportunity with client context
                title_suffix = f" for {client_name}" if client_name else ""
                ai_opportunity = StrategicOpportunity(
                    id=100,  # High ID to distinguish from transformed opportunities
                    title=f"AI-Identified Strategic Opportunity{title_suffix}",
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
                    supporting_evidence=(f"Analysis for {client_name}: " if client_name else "") + content[:500],
                    confidence_level=8.0
                )
                opportunities.append(ai_opportunity)
                
        except Exception as e:
            print(f"   ⚠️ AI opportunity generation failed: {str(e)}")
        
        return opportunities
    
    def _generate_brand_opportunities_with_client(self, competitors: List[str], device_category: str, client_name: str = "") -> List[CategoryOpportunity]:
        """Generate brand strategy opportunities with client context"""
        client_context = f" for {client_name}" if client_name else ""
        brand_owner = "your" if not client_name else f"{client_name}'s"
        
        return [
            CategoryOpportunity(
                opportunity=f"Outcome-Focused Brand Positioning{client_context}",
                current_gap="Competitors focus on device features, not patient outcomes",
                recommendation=f"Position {brand_owner} brand around patient outcomes and clinical results",
                implementation="Develop outcome-focused marketing, create clinical studies",
                timeline="3-6 months",
                investment="Low ($50K-150K)",
                competitive_advantage=f"First-mover advantage in outcome-based positioning{client_context}"
            )
        ]
    
    def _generate_product_opportunities_with_client(self, competitors: List[str], device_category: str, client_name: str = "") -> List[CategoryOpportunity]:
        """Generate product innovation opportunities with client context"""
        client_context = f" for {client_name}" if client_name else ""
        return [
            CategoryOpportunity(
                opportunity=f"Digital Integration Platform{client_context}",
                current_gap="Limited digital integration in competitor products",
                recommendation="Develop IoT-enabled devices with data analytics",
                implementation="Partner with tech company, develop MVP, pilot test",
                timeline="12-18 months",
                investment="High ($1M-3M)",
                competitive_advantage=f"Technology leadership in digital-enabled devices{client_context}"
            )
        ]
    
    def _generate_pricing_opportunities_with_client(self, competitors: List[str], device_category: str, client_name: str = "") -> List[CategoryOpportunity]:
        """Generate pricing strategy opportunities with client context"""
        client_context = f" for {client_name}" if client_name else ""
        return [
            CategoryOpportunity(
                opportunity=f"Value-Based Pricing Model{client_context}",
                current_gap="All competitors use traditional device pricing",
                recommendation="Implement outcome-based pricing with risk sharing",
                implementation="Pilot with health systems, track outcomes, scale",
                timeline="6-12 months",
                investment="Medium ($200K-500K)",
                competitive_advantage=f"Differentiated pricing model{client_context}"
            )
        ]
    
    def _generate_market_opportunities_with_client(self, competitors: List[str], device_category: str, client_name: str = "") -> List[CategoryOpportunity]:
        """Generate market expansion opportunities with client context"""
        client_context = f" for {client_name}" if client_name else ""
        return [
            CategoryOpportunity(
                opportunity=f"Ambulatory Surgery Center Focus{client_context}",
                current_gap="Competitors primarily target hospitals",
                recommendation="Develop ASC-specific products and support programs",
                implementation="ASC sales team, specialized products, training programs",
                timeline="6-12 months",
                investment="Medium ($300K-800K)",
                competitive_advantage=f"Market leadership in ASC segment{client_context}"
            )
        ]
    
    def _create_competitive_profiles_with_client(self, competitors: List[str], state: Dict[str, Any], client_name: str = "") -> Dict[str, CompetitorProfile]:
        """Create enhanced competitive profiles with client context"""
        profiles = {}
        
        for competitor in competitors:
            opportunities_against = ["Digital innovation", "Value-based positioning"]
            if client_name:
                opportunities_against.append(f"Partnership opportunities with {client_name}")
            
            profile = CompetitorProfile(
                name=competitor,
                market_share="Analysis-based",
                strengths=["Market presence", "Product portfolio"],
                weaknesses=["Innovation gaps", "Pricing pressure"],
                opportunities_against=opportunities_against,
                recent_moves=["Market expansion", "Product launches"],
                innovation_gaps=["Digital integration", "Value-based models"]
            )
            profiles[competitor] = profile.model_dump()
        
        return profiles
    
    def _generate_executive_summary_with_client(self, top_opportunities: List[Dict], competitors: List[str], 
                                               device_category: str, client_name: str = "") -> ExecutiveSummary:
        """Generate executive summary with client context"""
        top_3_titles = [opp.get("title", "") for opp in top_opportunities[:3]]
        
        client_context = f" for {client_name}" if client_name else ""
        key_insight = f"Significant opportunities exist in {device_category} through digital innovation and value-based positioning{client_context}"
        
        return ExecutiveSummary(
            key_insight=key_insight,
            top_3_opportunities=top_3_titles,
            immediate_actions=[
                "Prioritize digital integration initiatives",
                "Develop outcome-focused marketing strategy",
                "Explore value-based pricing pilots"
            ],
            strategic_focus="Digital innovation and outcome-based differentiation",
            competitive_advantage=f"First-mover advantage in digital-enabled devices{client_context}",
            revenue_potential="$10M-50M opportunity identified",
            market_share_opportunity="5-10% market share gain potential",
            investment_required="$2M-5M total investment"
        )
    
    def _summarize_research_results(self, results: List[Dict]) -> str:
        """Summarize research results for AI analysis"""
        summary_parts = []
        for result in results:
            title = result.get("title", "")
            content = result.get("content", "")[:200]
            summary_parts.append(f"- {title}: {content}...")
        return "\n".join(summary_parts)
    
    def _parse_gaps_from_response(self, response_content: str, gap_type: str) -> List[Dict[str, Any]]:
        """Parse gaps from AI response"""
        # Simple parsing - in production, would use more sophisticated NLP
        gaps = []
        if gap_type in response_content.lower():
            gaps.append({
                "gap_type": gap_type,
                "description": f"{gap_type.title()} gap identified in competitive analysis",
                "severity": "medium",
                "evidence": response_content[:300]
            })
        return gaps
    
    def run_analysis(self, competitors: List[str], focus_area: str = "spine_fusion", client_name: str = "") -> Dict[str, Any]:
        """Run the complete opportunity-first competitive analysis with client context"""
        print(f"🚀 Starting opportunity-first analysis...")
        print(f"   Client: {client_name if client_name else 'Not specified'}")
        print(f"   Competitors: {competitors}")
        print(f"   Focus area: {focus_area}")
        
        # Initialize state with client context
        initial_state = {
            "competitors": competitors,
            "focus_area": focus_area,
            "client_name": client_name,
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
                "client_name": client_name,
                "status": "failed"
            }

# Create global instance
enhanced_opportunity_graph = EnhancedOpportunityIntelligenceGraph() 