import { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  TrendingUp,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Eye,
  BarChart3,
  Activity,
  Brain,
  Zap,
  Target,
  FileText
} from 'lucide-react';

import { getAnalysisResult } from '../lib/api';
import type { AnalysisResult } from '../lib/api';
import { useStreamingAnalysis } from '../hooks/useStreamingAnalysis';
import GapAnalysisTab from '../components/GapAnalysisTab';

// Tab types for navigation
type TabType = 'analysis' | 'gaps';

const ResultsPage = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const location = useLocation();
  const [expandedOpportunities, setExpandedOpportunities] = useState<Set<number>>(new Set());
  const [liveInsights, setLiveInsights] = useState<Array<{id: string, type: string, message: string, timestamp: string}>>([]);
  const [hasStreamingCompleted, setHasStreamingCompleted] = useState(false);
  // NEW: Tab state for navigation
  const [activeTab, setActiveTab] = useState<TabType>('analysis');

  // Get analysis parameters from navigation state
  const analysisParams = location.state as {
    competitors?: string[];
    focusArea?: string;
    researchEnabled?: boolean;
    startAnalysis?: boolean;
  } | null;

  // Streaming analysis hook - use LangGraph streaming
  const {
    isConnected,
    isRunning: streamingIsRunning,
    events,
    progress: streamingProgress,
    currentMessage: streamingMessage,
    error: streamingError,
    connectToLangGraphStream,
    disconnect
  } = useStreamingAnalysis(analysisId || null, false);

  // Start LangGraph streaming if navigated from form
  useEffect(() => {
    if (analysisParams?.startAnalysis && analysisId && !hasStreamingCompleted) {
      const researchEnabled = analysisParams.researchEnabled ?? true;
      console.log('🚀 Starting LangGraph streaming analysis...', { 
        analysisId, 
        researchEnabled,
        ...analysisParams 
      });
      connectToLangGraphStream(analysisId, researchEnabled);
    }
  }, [analysisParams, analysisId, connectToLangGraphStream, hasStreamingCompleted]);

  // Detect streaming completion and mark it as completed
  useEffect(() => {
    const hasCompletionEvent = events.some(event => 
      event.type === 'analysis_completed' || event.type === 'stream_completed'
    );
    
    if (hasCompletionEvent && !hasStreamingCompleted) {
      console.log('🏁 Streaming completed detected, marking as finished');
      setHasStreamingCompleted(true);
      // Disconnect to prevent any further state changes
      setTimeout(() => disconnect(), 1000);
    }
  }, [events, hasStreamingCompleted, disconnect]);

  // Convert streaming events to live insights
  useEffect(() => {
    if (events.length > 0 && !hasStreamingCompleted) {
      const latestEvent = events[events.length - 1];
      
      // Create insights from different event types
      let insight = null;
      switch (latestEvent.type) {
        case 'node_execution':
          insight = {
            id: `node-${Date.now()}`,
            type: 'processing',
            message: latestEvent.message || `Executing analysis step`,
            timestamp: latestEvent.timestamp
          };
          break;
        case 'search_progress':
          insight = {
            id: `search-${Date.now()}`, 
            type: 'research',
            message: latestEvent.message || `Researching competitor data`,
            timestamp: latestEvent.timestamp
          };
          break;
        case 'insight_discovered':
          insight = {
            id: `insight-${Date.now()}`,
            type: 'insight',
            message: latestEvent.message || 'Competitive insight discovered',
            timestamp: latestEvent.timestamp
          };
          break;
        case 'opportunity_generated':
          insight = {
            id: `opportunity-${Date.now()}`,
            type: 'opportunity',
            message: latestEvent.message || 'Strategic opportunity identified',
            timestamp: latestEvent.timestamp
          };
          break;
      }
      
      if (insight) {
        setLiveInsights(prev => {
          // Only add if not already present (avoid duplicates)
          const exists = prev.some(i => i.message === insight.message && i.type === insight.type);
          if (exists) return prev;
          return [...prev.slice(-9), insight]; // Keep last 10 insights
        });
      }
    }
  }, [events, hasStreamingCompleted]);

  // Toggle opportunity expansion
  const toggleOpportunityExpansion = (index: number) => {
    const newExpanded = new Set(expandedOpportunities);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedOpportunities(newExpanded);
  };

  // Get analysis result - fetch immediately if no streaming was initiated or when streaming completes
  const { 
    data: result, 
    isLoading: resultLoading,
    refetch: refetchResult,
    error: resultError
  } = useQuery<AnalysisResult>({
    queryKey: ['analysis-result', analysisId],
    queryFn: () => getAnalysisResult(analysisId!),
    // Enable fetching when:
    // 1. We have an analysis ID AND
    // 2. Either streaming has completed OR no streaming was initiated (direct navigation)
    enabled: !!analysisId && (hasStreamingCompleted || !analysisParams?.startAnalysis),
    retry: 3,
    // Remove refetchInterval to prevent unnecessary polling
    refetchInterval: false,
  });

  // Determine if we should show streaming view or results view
  const showStreamingView = !hasStreamingCompleted && 
    analysisParams?.startAnalysis && (
      streamingIsRunning || 
      streamingProgress < 100 || 
      !events.some(event => event.type === 'analysis_completed' || event.type === 'stream_completed')
    );

  // Add debug logging to understand the transition
  useEffect(() => {
    console.log('🔍 Results Page State:', {
      analysisId,
      hasAnalysisParams: !!analysisParams,
      startAnalysis: analysisParams?.startAnalysis,
      streamingIsRunning,
      streamingProgress,
      eventsCount: events.length,
      hasCompletionEvent: events.some(event => event.type === 'analysis_completed' || event.type === 'stream_completed'),
      hasStreamingCompleted,
      showStreamingView,
      hasResult: !!result,
      resultLoading,
      resultError: resultError?.message
    });
  }, [streamingIsRunning, streamingProgress, events, showStreamingView, result, resultLoading, analysisId, hasStreamingCompleted, analysisParams, resultError]);

  // Show streaming state while analysis is running
  if (showStreamingView) {
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
          {analysisParams?.competitors && (
            <p className="text-sm text-gray-500 mt-1">
              Analyzing: {analysisParams.competitors.join(', ')} in {analysisParams.focusArea}
            </p>
          )}
        </div>

        {/* Live Analysis Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <Brain className="w-5 h-5 mr-2 text-primary-600" />
              Live Analysis
            </h2>
            
            {/* Connection Status */}
            <div className={`flex items-center space-x-2 text-sm ${isConnected ? 'text-green-600' : streamingIsRunning ? 'text-yellow-600' : 'text-gray-500'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-600 animate-pulse' : streamingIsRunning ? 'bg-yellow-600 animate-pulse' : 'bg-gray-400'}`}></div>
              <span>{isConnected ? 'Connected' : streamingIsRunning ? 'Connecting...' : 'Offline'}</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                LangGraph Analysis Progress
              </span>
              <span className="text-sm text-gray-600">{Math.round(streamingProgress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="h-2 rounded-full transition-all duration-300 bg-blue-600"
                style={{ width: `${streamingProgress}%` }}
              />
            </div>
          </div>

          {/* Current Status Message */}
          <div className="flex items-center space-x-3 mb-4">
            <Activity className="w-5 h-5 text-blue-500 animate-pulse" />
            <p className="text-gray-700">
              {streamingMessage || 'Analyzing competitive intelligence...'}
            </p>
          </div>

          {/* Live Insights Stream */}
          {liveInsights.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Recent Insights:</h3>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {liveInsights.slice(-5).map((insight) => (
                  <div key={insight.id} className="flex items-center space-x-2 text-sm p-2 bg-gray-50 rounded">
                    {insight.type === 'processing' && <Zap className="w-4 h-4 text-purple-500" />}
                    {insight.type === 'research' && <Eye className="w-4 h-4 text-blue-500" />}
                    {insight.type === 'insight' && <TrendingUp className="w-4 h-4 text-green-500" />}
                    {insight.type === 'opportunity' && <CheckCircle className="w-4 h-4 text-yellow-500" />}
                    <span className="flex-1 text-gray-700">{insight.message}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(insight.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Streaming Error */}
          {streamingError && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-yellow-800 text-sm">
                <strong>Connection Issue:</strong> {streamingError}
              </p>
              <p className="text-yellow-700 text-xs mt-1">
                The analysis will continue in the background...
              </p>
            </div>
          )}

          {/* Debug Info - Temporary for troubleshooting */}
          <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Debug Info:</h4>
            <div className="text-xs text-gray-600 space-y-1">
              <div>Running: {streamingIsRunning ? 'Yes' : 'No'}</div>
              <div>Progress: {streamingProgress}%</div>
              <div>Events: {events.length}</div>
              <div>Streaming Completed: {hasStreamingCompleted ? 'Yes' : 'No'}</div>
              <div>Completion Events: {events.filter(e => e.type === 'analysis_completed' || e.type === 'stream_completed').length}</div>
              <div>Last Event: {events[events.length - 1]?.type || 'None'}</div>
            </div>
            <button
              onClick={() => {
                console.log('Manual completion trigger');
                setHasStreamingCompleted(true);
              }}
              className="mt-2 px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
            >
              Force Complete
            </button>
          </div>
        </div>

        {/* Processing Steps Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <Brain className="w-3 h-3 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-blue-900 mb-2">Real-time Competitive Intelligence</h3>
              <p className="text-sm text-blue-800">
                Our AI is analyzing competitive data using advanced LangGraph workflows. 
                This includes researching competitors, identifying gaps, analyzing market positions, and generating strategic opportunities.
              </p>
              <p className="text-xs text-blue-700 mt-2">
                ⚡ Live streaming enabled - You're seeing real-time updates as the analysis progresses.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show completed analysis results
  if (result) {
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
          <div className="mt-2 px-4 py-2 bg-green-100 text-green-800 rounded-lg inline-block">
            ✅ Analysis Complete
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('analysis')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'analysis'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>Analysis Results</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('gaps')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'gaps'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Target className="w-4 h-4" />
                  <span>Competitive Gaps</span>
                </div>
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'analysis' && (
              <div className="space-y-8">
                {/* Executive Summary */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                      <BarChart3 className="w-5 h-5 mr-2 text-green-600" />
                      Executive Summary
                    </h2>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Confidence Score</p>
                        <p className="text-2xl font-bold text-green-600">{result.confidence_score?.toFixed(1) || 'N/A'}/10</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-3 gap-4 mb-4">
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <p className="text-2xl font-bold text-blue-600">{result.top_opportunities?.length || 0}</p>
                      <p className="text-sm text-blue-800">Opportunities</p>
                    </div>
                    <div className="text-center p-3 bg-purple-50 rounded-lg">
                      <p className="text-2xl font-bold text-purple-600">{result.metadata?.total_sources || 0}</p>
                      <p className="text-sm text-purple-800">Sources</p>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <p className="text-2xl font-bold text-green-600">{result.metadata?.competitors_analyzed?.length || 0}</p>
                      <p className="text-sm text-green-800">Competitors</p>
                    </div>
                  </div>
                  
                  <div className="prose prose-gray max-w-none">
                    <p className="text-gray-700">
                      {result.executive_summary?.key_insight || 'Analysis completed successfully.'}
                    </p>
                  </div>
                </div>

                {/* Strategic Opportunities */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
                    Strategic Opportunities
                  </h2>
                  
                  {result.top_opportunities && result.top_opportunities.length > 0 ? (
                    <div className="space-y-4">
                      {result.top_opportunities.map((opportunity, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <h3 className="font-semibold text-gray-900">
                                  {opportunity.title || `Opportunity ${index + 1}`}
                                </h3>
                                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                  Score: {opportunity.opportunity_score?.toFixed(1) || 'N/A'}
                                </span>
                              </div>
                              
                              <p className="text-gray-700 mb-3">
                                {opportunity.description || 'Strategic opportunity identified.'}
                              </p>
                              
                              {expandedOpportunities.has(index) && (
                                <div className="space-y-3">
                                  {opportunity.evidence && (
                                    <div>
                                      <h4 className="font-medium text-gray-900 mb-1">Supporting Evidence:</h4>
                                      <p className="text-sm text-gray-600">{opportunity.evidence}</p>
                                    </div>
                                  )}
                                  
                                  {opportunity.next_steps && opportunity.next_steps.length > 0 && (
                                    <div>
                                      <h4 className="font-medium text-gray-900 mb-1">Recommended Next Steps:</h4>
                                      <ul className="list-disc list-inside space-y-1">
                                        {opportunity.next_steps.map((step, stepIndex) => (
                                          <li key={stepIndex} className="text-sm text-gray-600">{step}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  
                                  {opportunity.time_to_market && (
                                    <div>
                                      <h4 className="font-medium text-gray-900 mb-1">Time to Market:</h4>
                                      <p className="text-sm text-gray-600">{opportunity.time_to_market}</p>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                            
                            <button
                              onClick={() => toggleOpportunityExpansion(index)}
                              className="ml-4 p-1 text-gray-400 hover:text-gray-600"
                            >
                              {expandedOpportunities.has(index) ? (
                                <ChevronUp className="w-5 h-5" />
                              ) : (
                                <ChevronDown className="w-5 h-5" />
                              )}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-8">
                      No strategic opportunities identified in this analysis.
                    </p>
                  )}
                </div>

                {/* Analysis Details */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                    <BarChart3 className="w-5 h-5 mr-2 text-gray-600" />
                    Analysis Details
                  </h2>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">Analysis Metadata</h3>
                      <dl className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <dt className="text-gray-600">Total Sources:</dt>
                          <dd className="font-medium">{result.metadata?.total_sources || 0}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-gray-600">Competitors Analyzed:</dt>
                          <dd className="font-medium">{result.metadata?.competitors_analyzed?.length || 0}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-gray-600">Analysis Duration:</dt>
                          <dd className="font-medium">{result.metadata?.analysis_duration || 'Unknown'}</dd>
                        </div>
                      </dl>
                    </div>
                    
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">Strategic Recommendations</h3>
                      {result.executive_summary?.strategic_recommendations && result.executive_summary.strategic_recommendations.length > 0 ? (
                        <ul className="space-y-1 text-sm">
                          {result.executive_summary.strategic_recommendations.map((rec, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-700">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500 text-sm">No specific recommendations available.</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'gaps' && (
              <GapAnalysisTab analysisResult={result} />
            )}
          </div>
        </div>
      </div>
    );
  }

  // Show loading state if streaming completed but no result yet  
  if (hasStreamingCompleted && resultLoading) {
    return (
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analysis Results
          </h1>
          <p className="text-lg text-gray-600">
            Analysis ID: {analysisId}
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <RefreshCw className="w-6 h-6 text-blue-500 animate-spin" />
            <span className="text-lg text-gray-700">Loading analysis results...</span>
          </div>
          <p className="text-gray-500">
            The analysis has completed. Fetching your competitive intelligence report...
          </p>
        </div>
      </div>
    );
  }

  // Show loading state for direct navigation (no streaming initiated)
  if (!analysisParams?.startAnalysis && resultLoading) {
    return (
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analysis Results
          </h1>
          <p className="text-lg text-gray-600">
            Analysis ID: {analysisId}
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <RefreshCw className="w-6 h-6 text-blue-500 animate-spin" />
            <span className="text-lg text-gray-700">Fetching analysis results...</span>
          </div>
          <p className="text-gray-500">
            Looking up your existing analysis...
          </p>
        </div>
      </div>
    );
  }

  // Fallback: Show error state
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Analysis Results
        </h1>
        <p className="text-lg text-gray-600">
          Analysis ID: {analysisId}
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <AlertCircle className="w-6 h-6 text-yellow-500" />
          <span className="text-lg text-gray-700">Analysis Status Unknown</span>
        </div>
        <p className="text-gray-500 mb-4">
          Unable to determine analysis status. The analysis may still be running or may have encountered an issue.
        </p>

        {/* Debug Information */}
        <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg text-left">
          <h3 className="font-medium text-gray-900 mb-2">Debug Information:</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <div>Analysis ID: {analysisId || 'Missing'}</div>
            <div>Has Analysis Params: {analysisParams ? 'Yes' : 'No'}</div>
            <div>Start Analysis Flag: {analysisParams?.startAnalysis ? 'Yes' : 'No'}</div>
            <div>Streaming Completed: {hasStreamingCompleted ? 'Yes' : 'No'}</div>
            <div>Result Loading: {resultLoading ? 'Yes' : 'No'}</div>
            <div>Has Result: {result ? 'Yes' : 'No'}</div>
            <div>Result Error: {resultError?.message || 'None'}</div>
            <div>Events Count: {events.length}</div>
          </div>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => refetchResult()}
            className="btn-primary flex items-center space-x-2 mx-auto"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Fetch Results</span>
          </button>
          
          {resultError && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">
                <strong>API Error:</strong> {resultError.message}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage; 