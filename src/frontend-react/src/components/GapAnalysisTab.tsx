import React, { useMemo } from 'react';
import { 
  Target, 
  TrendingUp, 
  BarChart3, 
  Clock, 
  DollarSign, 
  AlertTriangle,
  Lightbulb,
  ArrowRight
} from 'lucide-react';
import type { AnalysisResult, GapAnalysisResult } from '../lib/api';
import { transformToGapAnalysis } from '../lib/api';
import GapMatrix from './GapMatrix';
import FeatureComparison from './FeatureComparison';
import CompetitiveRankings from './CompetitiveRankings';

interface GapAnalysisTabProps {
  analysisResult: AnalysisResult;
  className?: string;
}

const GapAnalysisTab: React.FC<GapAnalysisTabProps> = ({ analysisResult, className = '' }) => {
  // Transform analysis result to gap analysis format
  const gapAnalysis: GapAnalysisResult = useMemo(() => {
    return transformToGapAnalysis(analysisResult);
  }, [analysisResult]);

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Executive Summary Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
              <Target className="w-6 h-6 mr-2 text-blue-600" />
              Competitive Gap Analysis
            </h2>
            <p className="text-gray-600">
              Comprehensive analysis of competitive positioning and improvement opportunities
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Analysis Date</p>
            <p className="font-medium">{gapAnalysis.metadata.analysis_date}</p>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg p-4 border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Gaps</p>
                <p className="text-2xl font-bold text-gray-900">{gapAnalysis.gap_summary.total_gaps}</p>
              </div>
              <Target className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-red-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Critical Gaps</p>
                <p className="text-2xl font-bold text-red-600">{gapAnalysis.gap_summary.critical_gaps}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">High Priority</p>
                <p className="text-2xl font-bold text-orange-600">{gapAnalysis.gap_summary.high_priority_gaps}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Revenue Impact</p>
                <p className="text-lg font-bold text-green-600">{gapAnalysis.gap_summary.estimated_revenue_impact}</p>
              </div>
              <DollarSign className="w-8 h-8 text-green-500" />
            </div>
          </div>
        </div>

        {/* Quick Wins & Long-term Initiatives */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-4 border border-green-200">
            <h3 className="font-medium text-gray-900 mb-3 flex items-center">
              <Lightbulb className="w-4 h-4 mr-2 text-green-600" />
              Quick Wins
            </h3>
            {gapAnalysis.gap_summary.quick_wins.length === 0 ? (
              <p className="text-sm text-gray-500">No quick wins identified</p>
            ) : (
              <ul className="space-y-2">
                {gapAnalysis.gap_summary.quick_wins.slice(0, 3).map((win, index) => (
                  <li key={index} className="flex items-start text-sm">
                    <ArrowRight className="w-3 h-3 mt-0.5 mr-2 text-green-500 flex-shrink-0" />
                    <span>{win}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="bg-white rounded-lg p-4 border border-blue-200">
            <h3 className="font-medium text-gray-900 mb-3 flex items-center">
              <Clock className="w-4 h-4 mr-2 text-blue-600" />
              Long-term Initiatives
            </h3>
            {gapAnalysis.gap_summary.long_term_initiatives.length === 0 ? (
              <p className="text-sm text-gray-500">No long-term initiatives identified</p>
            ) : (
              <ul className="space-y-2">
                {gapAnalysis.gap_summary.long_term_initiatives.slice(0, 3).map((initiative, index) => (
                  <li key={index} className="flex items-start text-sm">
                    <ArrowRight className="w-3 h-3 mt-0.5 mr-2 text-blue-500 flex-shrink-0" />
                    <span>{initiative}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      {/* Gap Matrix Component */}
      <GapMatrix gaps={gapAnalysis.identified_gaps} />

      {/* Feature Comparison Component */}
      {gapAnalysis.feature_comparisons.length > 0 && (
        <FeatureComparison comparisons={gapAnalysis.feature_comparisons} />
      )}

      {/* Competitive Rankings Component */}
      {gapAnalysis.competitive_rankings.length > 0 && (
        <CompetitiveRankings rankings={gapAnalysis.competitive_rankings} />
      )}

      {/* Market Positioning Summary */}
      {gapAnalysis.market_positioning.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-blue-500" />
            Market Positioning Analysis
          </h3>
          
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {gapAnalysis.market_positioning.map((positioning, index) => (
              <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">{positioning.competitor_name}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    positioning.market_momentum === 'growing' ? 'bg-green-100 text-green-800' :
                    positioning.market_momentum === 'stable' ? 'bg-blue-100 text-blue-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {positioning.market_momentum}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-3">{positioning.positioning_statement}</p>
                
                <div className="space-y-2">
                  <div>
                    <p className="text-xs font-medium text-gray-700">Market Share</p>
                    <p className="text-sm text-gray-600">{positioning.market_share_estimate}</p>
                  </div>
                  
                  <div>
                    <p className="text-xs font-medium text-gray-700">Pricing Strategy</p>
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                      positioning.pricing_strategy === 'premium' ? 'bg-purple-100 text-purple-800' :
                      positioning.pricing_strategy === 'competitive' ? 'bg-blue-100 text-blue-800' :
                      positioning.pricing_strategy === 'value' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {positioning.pricing_strategy}
                    </span>
                  </div>

                  {positioning.key_differentiators.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-gray-700">Key Differentiators</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {positioning.key_differentiators.slice(0, 2).map((diff, diffIndex) => (
                          <span
                            key={diffIndex}
                            className="inline-flex px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-700"
                          >
                            {diff}
                          </span>
                        ))}
                        {positioning.key_differentiators.length > 2 && (
                          <span className="inline-flex px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-700">
                            +{positioning.key_differentiators.length - 2}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Metadata */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <h4 className="font-medium text-gray-900 mb-2">Analysis Metadata</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Focus Area</p>
            <p className="font-medium">{gapAnalysis.metadata.focus_area}</p>
          </div>
          <div>
            <p className="text-gray-600">Competitors</p>
            <p className="font-medium">{gapAnalysis.metadata.competitors_analyzed.length}</p>
          </div>
          <div>
            <p className="text-gray-600">Confidence Score</p>
            <p className="font-medium">{gapAnalysis.metadata.confidence_score}/10</p>
          </div>
          <div>
            <p className="text-gray-600">Analysis ID</p>
            <p className="font-medium text-xs">{gapAnalysis.analysis_id}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GapAnalysisTab; 