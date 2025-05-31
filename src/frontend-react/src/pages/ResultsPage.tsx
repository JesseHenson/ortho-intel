import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle,
  RefreshCw
} from 'lucide-react';

import { getAnalysisStatus, getAnalysisResult } from '../lib/api';
import type { AnalysisStatus, AnalysisResult } from '../lib/api';
import LoadingSpinner from '../components/LoadingSpinner';
import StreamingAnalytics from '../components/StreamingAnalytics';

const ResultsPage = () => {
  const { analysisId } = useParams<{ analysisId: string }>();

  // Get analysis status
  const { 
    data: status, 
    isLoading: statusLoading,
    refetch: refetchStatus
  } = useQuery<AnalysisStatus>({
    queryKey: ['analysis-status', analysisId],
    queryFn: () => getAnalysisStatus(analysisId!),
    enabled: !!analysisId,
    refetchInterval: (query) => {
      // Stop polling when analysis is complete
      return query.state.data?.status === 'completed' || query.state.data?.status === 'failed' ? false : 3000;
    },
  });

  // Get analysis result (only when completed)
  const { 
    data: result, 
    isLoading: resultLoading
  } = useQuery<AnalysisResult>({
    queryKey: ['analysis-result', analysisId],
    queryFn: () => getAnalysisResult(analysisId!),
    enabled: !!analysisId && status?.status === 'completed',
    retry: 1
  });

  // Check if analysis is recent (within last 30 seconds) to show streaming demo
  const isRecentAnalysis = (status: AnalysisStatus): boolean => {
    if (!status.created_at) return true; // Show for analyses without timestamp
    
    const createdAt = new Date(status.created_at);
    const now = new Date();
    const diffInSeconds = (now.getTime() - createdAt.getTime()) / 1000;
    
    return diffInSeconds <= 30; // Show streaming for analyses created within last 30 seconds
  };

  // Show loading state
  if (statusLoading) {
    return (
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analysis Results
          </h1>
          <p className="text-lg text-gray-600">
            Analysis ID: {analysisId}
          </p>
        </div>

        {/* Streaming Analytics - Show immediately during loading */}
        <StreamingAnalytics
          analysisId={analysisId!}
          isRunning={true}
          onInsightClick={(insight) => {
            console.log('Insight clicked:', insight);
          }}
        />

        {/* Loading Status Card */}
        <div className="bg-white rounded-lg shadow-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Analysis Status</h2>
          </div>

          <div className="flex items-center space-x-4">
            {/* Status Icon */}
            <RefreshCw className="w-6 h-6 text-blue-500 animate-spin" />

            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-blue-700 bg-blue-100 px-3 py-1 rounded-full text-sm font-medium">
                  Initializing Analysis
                </span>
                <span className="text-sm text-gray-600">
                  Starting...
                </span>
              </div>
              
              {/* Progress Bar */}
              <div className="progress-bar">
                <div 
                  className="progress-fill animate-pulse"
                  style={{ width: `25%` }}
                ></div>
              </div>
              
              <p className="text-sm text-gray-600 mt-2">
                Connecting to analysis engine and preparing competitive intelligence scan...
              </p>
            </div>
          </div>
        </div>

        {/* Helpful info during loading */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-3 h-3 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-medium text-blue-900">Analysis in Progress</h3>
              <p className="text-sm text-blue-700 mt-1">
                Our AI is scanning competitive landscapes, identifying market gaps, and discovering strategic opportunities. 
                Watch the insights appear in real-time above as we analyze your competitors.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (!status) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-lg font-medium text-gray-900">Analysis Not Found</h2>
          <p className="text-gray-600">Could not load analysis with ID: {analysisId}</p>
        </div>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'failed':
        return <AlertCircle className="w-6 h-6 text-red-500" />;
      case 'running':
        return <RefreshCw className="w-6 h-6 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-6 h-6 text-yellow-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'completed': return 'text-green-700 bg-green-100';
      case 'failed': return 'text-red-700 bg-red-100';
      case 'running': return 'text-blue-700 bg-blue-100';
      default: return 'text-yellow-700 bg-yellow-100';
    }
  };

  // Determine if we should show streaming analytics
  const shouldShowStreaming = (status.status === 'running' || status.status === 'pending') || 
                             (status.status === 'completed' && isRecentAnalysis(status));

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Analysis Results
        </h1>
        <p className="text-lg text-gray-600">
          Analysis ID: {analysisId}
        </p>
      </div>

      {/* Streaming Analytics - Show when analysis is running OR recently completed */}
      {shouldShowStreaming && (
        <StreamingAnalytics
          analysisId={analysisId!}
          isRunning={status.status === 'running' || status.status === 'pending'}
          onInsightClick={(insight) => {
            console.log('Insight clicked:', insight);
          }}
        />
      )}

      {/* Status Card */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Analysis Status</h2>
          
          {status.status !== 'completed' && status.status !== 'failed' && (
            <button
              onClick={() => refetchStatus()}
              className="btn-secondary flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {/* Status Icon */}
          {getStatusIcon()}

          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <span className={getStatusColor()}>
                {status.status === 'running' ? 'In Progress' : status.status}
              </span>
              <span className="text-sm text-gray-600">
                {Math.round(status.progress * 100)}%
              </span>
            </div>
            
            {/* Progress Bar */}
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${status.progress * 100}%` }}
              ></div>
            </div>
            
            <p className="text-sm text-gray-600 mt-2">
              {status.message}
            </p>
          </div>
        </div>

        {status.error_message && (
          <div className="mt-4 p-3 bg-risk-50 border border-risk-200 rounded-lg">
            <p className="text-risk-800 text-sm">
              <strong>Error:</strong> {status.error_message}
            </p>
          </div>
        )}
      </div>

      {/* Results Section */}
      {status.status === 'completed' && (
        <>
          {resultLoading ? (
            <div className="bg-white rounded-lg shadow-card p-12">
              <div className="text-center">
                <LoadingSpinner size="lg" className="mx-auto mb-4" />
                <p className="text-gray-600">Loading results...</p>
              </div>
            </div>
          ) : result ? (
            <div className="space-y-6">
              {/* Executive Summary Section */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
                    Executive Summary
                  </h2>
                </div>
                <div className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <div className="metric-card">
                      <div className="metric-value text-2xl font-bold text-primary-600">
                        {result.confidence_score.toFixed(1)}/10
                      </div>
                      <div className="metric-label">Confidence Score</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-value text-2xl font-bold text-strategic-600">
                        {result.top_opportunities.length}
                      </div>
                      <div className="metric-label">Strategic Opportunities</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-value text-2xl font-bold text-secondary-600">
                        {result.metadata.total_sources}
                      </div>
                      <div className="metric-label">Sources Analyzed</div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">Key Insight</h3>
                      <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">
                        {result.executive_summary.key_insight}
                      </p>
                    </div>
                    
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">Strategic Recommendations</h3>
                      <ul className="space-y-2">
                        {result.executive_summary.strategic_recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start">
                            <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                            <span className="text-gray-700">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Strategic Opportunities */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Strategic Opportunities ({result.top_opportunities.length})
                  </h2>
                </div>
                <div className="p-6">
                  {result.top_opportunities.length > 0 ? (
                    <div className="space-y-8">
                      {result.top_opportunities.map((opportunity, index) => (
                        <div key={index} className="opportunity-card border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                {opportunity.title}
                              </h3>
                              <div className="flex items-center space-x-3">
                                <span className="inline-flex items-center px-3 py-1 bg-strategic-100 text-strategic-800 rounded-full text-sm font-medium">
                                  Score: {opportunity.opportunity_score.toFixed(1)}/10
                                </span>
                                <span className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                                  {opportunity.market_size}
                                </span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="mb-6">
                            <h4 className="font-medium text-gray-900 mb-2">Opportunity Description</h4>
                            <p className="text-gray-700 leading-relaxed">
                              {opportunity.description}
                            </p>
                          </div>

                          {/* Source Evidence Analysis */}
                          <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
                            <h4 className="font-medium text-amber-900 mb-3 flex items-center">
                              <AlertCircle className="w-4 h-4 mr-2" />
                              Source Evidence & Analysis
                            </h4>
                            <div className="space-y-3">
                              <div>
                                <span className="text-sm font-medium text-amber-800">Key Evidence:</span>
                                <p className="text-sm text-amber-700 mt-1 leading-relaxed">
                                  {opportunity.evidence}
                                </p>
                              </div>
                              <div>
                                <span className="text-sm font-medium text-amber-800">Market Indicators:</span>
                                <p className="text-sm text-amber-700 mt-1">
                                  {opportunity.key_phrases}
                                </p>
                              </div>
                              {opportunity.competitive_advantage && (
                                <div>
                                  <span className="text-sm font-medium text-amber-800">Competitive Advantage:</span>
                                  <p className="text-sm text-amber-700 mt-1 leading-relaxed">
                                    {opportunity.competitive_advantage}
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                            <div className="bg-gray-50 rounded-lg p-4">
                              <span className="font-medium text-gray-600 text-sm">Time to Market</span>
                              <p className="text-gray-900 font-semibold">{opportunity.time_to_market}</p>
                            </div>
                            <div className="bg-gray-50 rounded-lg p-4">
                              <span className="font-medium text-gray-600 text-sm">Investment Level</span>
                              <p className="text-gray-900 font-semibold">{opportunity.investment_level}</p>
                            </div>
                            <div className="bg-gray-50 rounded-lg p-4">
                              <span className="font-medium text-gray-600 text-sm">Implementation</span>
                              <p className="text-gray-900 font-semibold">{opportunity.implementation_difficulty}</p>
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div>
                              <h4 className="font-medium text-gray-900 mb-3">Implementation Roadmap</h4>
                              <ul className="space-y-2">
                                {opportunity.next_steps.map((step, stepIndex) => (
                                  <li key={stepIndex} className="text-sm text-gray-700 flex items-start">
                                    <span className="w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5 flex-shrink-0">
                                      {stepIndex + 1}
                                    </span>
                                    {step}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            
                            {opportunity.sources && opportunity.sources.length > 0 && (
                              <div>
                                <h4 className="font-medium text-gray-900 mb-3">Supporting Evidence</h4>
                                <div className="space-y-3">
                                  {opportunity.sources.slice(0, 2).map((source, sourceIndex) => (
                                    <div key={sourceIndex} className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                                      <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm font-medium text-gray-900">
                                          {source.title}
                                        </span>
                                        <div className="flex items-center space-x-2">
                                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                            Credibility: {source.credibility_score}/10
                                          </span>
                                        </div>
                                      </div>
                                      <p className="text-xs text-gray-600 leading-relaxed">
                                        {source.content_snippet}
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <p>No strategic opportunities identified yet.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Debug Section - Raw Data */}
              <div className="bg-gray-50 rounded-lg border border-gray-200">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-lg font-medium text-gray-900">Analysis Metadata</h2>
                </div>
                <div className="p-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-600">Competitors:</span>
                      <p className="text-gray-900">{result.metadata.competitors_analyzed.join(', ')}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">Focus Area:</span>
                      <p className="text-gray-900">{result.metadata.focus_area}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">Analysis Type:</span>
                      <p className="text-gray-900">{result.metadata.analysis_type}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">Sources:</span>
                      <p className="text-gray-900">{result.metadata.total_sources}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-card p-12 text-center">
              <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Results Available
              </h3>
              <p className="text-gray-600">
                The analysis completed but no results were returned.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ResultsPage; 