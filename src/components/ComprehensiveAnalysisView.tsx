import React, { useMemo } from 'react';
import { BackendAnalysisResult } from '../lib/api';
import { 
  FileText, 
  Search, 
  Target, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  BarChart3,
  Users,
  Lightbulb,
  Database,
  Clock,
  Award
} from 'lucide-react';

interface ComprehensiveAnalysisViewProps {
  analysisResult: BackendAnalysisResult;
}

const ComprehensiveAnalysisView: React.FC<ComprehensiveAnalysisViewProps> = ({ analysisResult }) => {
  const stats = useMemo(() => ({
    totalClinicalGaps: analysisResult.clinical_gaps?.length || 0,
    totalResearchResults: analysisResult.raw_research_results?.length || 0,
    totalOpportunities: analysisResult.top_opportunities?.length || 0,
    totalSources: analysisResult.metadata?.total_sources || 0,
    deviceCategory: analysisResult.device_category || 'Unknown',
    confidenceScore: analysisResult.confidence_score || 0,
    hasMethodology: !!analysisResult.comprehensive_methodology
  }), [analysisResult]);

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': 
      case 'high': return 'bg-red-100 text-red-800 border-red-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high': return <AlertTriangle className="w-4 h-4" />;
      case 'medium': return <Target className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-8">
      {/* Executive Dashboard */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">📊 Complete Analysis Dashboard</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold">{stats.totalClinicalGaps}</div>
            <div className="text-blue-100">Clinical Gaps</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold">{stats.totalOpportunities}</div>
            <div className="text-blue-100">Opportunities</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold">{stats.totalResearchResults}</div>
            <div className="text-blue-100">Sources</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold">{stats.confidenceScore.toFixed(1)}/10</div>
            <div className="text-blue-100">Confidence</div>
          </div>
        </div>
      </div>

      {/* Clinical Gaps Section */}
      {analysisResult.clinical_gaps && analysisResult.clinical_gaps.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <AlertTriangle className="w-6 h-6 text-red-500 mr-2" />
            <h3 className="text-xl font-bold text-gray-900">
              Clinical Gaps Analysis ({analysisResult.clinical_gaps.length} gaps identified)
            </h3>
          </div>
          <div className="space-y-4">
            {analysisResult.clinical_gaps.map((gap, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-gray-900">{gap.competitor}</span>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(gap.severity)}`}>
                      {getSeverityIcon(gap.severity)}
                      <span className="ml-1">{gap.severity}</span>
                    </span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-md">
                      {gap.gap_type}
                    </span>
                  </div>
                </div>
                
                <p className="text-gray-700 mb-3 leading-relaxed">{gap.description}</p>
                
                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                  <h5 className="font-medium text-gray-900 mb-2">Evidence:</h5>
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {gap.evidence.length > 300 ? `${gap.evidence.substring(0, 300)}...` : gap.evidence}
                  </p>
                </div>
                
                {gap.source_url && (
                  <div className="flex items-center text-sm text-blue-600 hover:text-blue-800">
                    <ExternalLink className="w-4 h-4 mr-1" />
                    <a href={gap.source_url} target="_blank" rel="noopener noreferrer" className="truncate">
                      {gap.source_url}
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Research Sources Section */}
      {analysisResult.raw_research_results && analysisResult.raw_research_results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Database className="w-6 h-6 text-blue-500 mr-2" />
            <h3 className="text-xl font-bold text-gray-900">
              Research Sources ({analysisResult.raw_research_results.length} sources analyzed)
            </h3>
          </div>
          <div className="space-y-3">
            {analysisResult.raw_research_results.slice(0, 10).map((result, index) => (
              <div key={index} className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded-r-lg">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-blue-900">{result.competitor}</span>
                      <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">
                        Score: {result.score.toFixed(1)}
                      </span>
                    </div>
                    <h5 className="font-medium text-gray-900 mb-1">{result.title}</h5>
                  </div>
                </div>
                
                <p className="text-gray-700 text-sm mb-2 leading-relaxed">
                  {result.content.length > 200 ? `${result.content.substring(0, 200)}...` : result.content}
                </p>
                
                <div className="flex items-center justify-between text-xs text-gray-600">
                  <span>Query: {result.query}</span>
                  <a href={result.url} target="_blank" rel="noopener noreferrer" 
                     className="flex items-center text-blue-600 hover:text-blue-800">
                    <ExternalLink className="w-3 h-3 mr-1" />
                    Source
                  </a>
                </div>
              </div>
            ))}
            {analysisResult.raw_research_results.length > 10 && (
              <div className="text-center py-2 text-gray-600">
                ... and {analysisResult.raw_research_results.length - 10} more sources
              </div>
            )}
          </div>
        </div>
      )}

      {/* Opportunities Breakdown */}
      {analysisResult.final_report && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <Lightbulb className="w-6 h-6 text-yellow-500 mr-2" />
            <h3 className="text-xl font-bold text-gray-900">Strategic Opportunities Matrix</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Brand Opportunities */}
            {analysisResult.final_report.brand_opportunities && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <Award className="w-5 h-5 text-purple-600 mr-2" />
                  <h4 className="font-semibold text-purple-900">Brand Strategy</h4>
                </div>
                <div className="text-2xl font-bold text-purple-700 mb-1">
                  {analysisResult.final_report.brand_opportunities.length}
                </div>
                <div className="text-purple-600 text-sm">Opportunities</div>
              </div>
            )}
            
            {/* Product Opportunities */}
            {analysisResult.final_report.product_opportunities && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <BarChart3 className="w-5 h-5 text-green-600 mr-2" />
                  <h4 className="font-semibold text-green-900">Product Innovation</h4>
                </div>
                <div className="text-2xl font-bold text-green-700 mb-1">
                  {analysisResult.final_report.product_opportunities.length}
                </div>
                <div className="text-green-600 text-sm">Opportunities</div>
              </div>
            )}
            
            {/* Pricing Opportunities */}
            {analysisResult.final_report.pricing_opportunities && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <TrendingUp className="w-5 h-5 text-orange-600 mr-2" />
                  <h4 className="font-semibold text-orange-900">Pricing Strategy</h4>
                </div>
                <div className="text-2xl font-bold text-orange-700 mb-1">
                  {analysisResult.final_report.pricing_opportunities.length}
                </div>
                <div className="text-orange-600 text-sm">Opportunities</div>
              </div>
            )}
            
            {/* Market Opportunities */}
            {analysisResult.final_report.market_opportunities && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <Users className="w-5 h-5 text-blue-600 mr-2" />
                  <h4 className="font-semibold text-blue-900">Market Expansion</h4>
                </div>
                <div className="text-2xl font-bold text-blue-700 mb-1">
                  {analysisResult.final_report.market_opportunities.length}
                </div>
                <div className="text-blue-600 text-sm">Opportunities</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Methodology Transparency */}
      {stats.hasMethodology && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <Clock className="w-6 h-6 text-gray-500 mr-2" />
            <h3 className="text-xl font-bold text-gray-900">Analysis Methodology & Transparency</h3>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Processing Summary:</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium">Device Category:</span> {stats.deviceCategory}
              </div>
              <div>
                <span className="font-medium">Search Queries:</span> {analysisResult.search_queries?.length || 0}
              </div>
              <div>
                <span className="font-medium">Analysis Stages:</span> Complete 7-stage pipeline
              </div>
            </div>
          </div>
          
          {analysisResult.methodology_transparency_report && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h5 className="font-medium text-blue-900 mb-2">🔍 Methodology Transparency Available</h5>
              <p className="text-blue-800 text-sm">
                Complete audit trail including LangGraph execution, reasoning chains, and decision points.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Quick Stats Summary */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📈 Analysis Impact Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Key Findings:</h4>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                {stats.totalClinicalGaps} detailed competitive gaps identified
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                {stats.totalOpportunities} strategic opportunities prioritized
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                {stats.totalSources} high-quality sources analyzed
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                Complete methodology transparency available
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Recommended Actions:</h4>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-center">
                <TrendingUp className="w-4 h-4 text-blue-500 mr-2" />
                Review high-severity gaps for immediate action
              </li>
              <li className="flex items-center">
                <TrendingUp className="w-4 h-4 text-blue-500 mr-2" />
                Prioritize opportunities by implementation difficulty
              </li>
              <li className="flex items-center">
                <TrendingUp className="w-4 h-4 text-blue-500 mr-2" />
                Validate findings with internal stakeholders
              </li>
              <li className="flex items-center">
                <TrendingUp className="w-4 h-4 text-blue-500 mr-2" />
                Develop 90-day action plan from insights
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveAnalysisView; 