import React, { useState, useEffect } from 'react';
import { 
  Search, 
  TrendingUp, 
  CheckCircle, 
  ExternalLink,
  Brain,
  Target,
  FileText,
  Lightbulb,
  AlertCircle,
  Zap,
  Activity
} from 'lucide-react';
import { useStreamingAnalysis } from '../hooks/useStreamingAnalysis';

export interface StreamingInsight {
  id: string;
  type: 'source_discovery' | 'market_insight' | 'competitive_gap' | 'opportunity_identified' | 'node_execution' | 'search_progress';
  title: string;
  content: string;
  source_url?: string;
  credibility_score?: number;
  timestamp: string;
  relevance_score?: number;
  confidence_score?: number;
}

export interface StreamingAnalyticsProps {
  analysisId: string;
  isRunning?: boolean;
  insights?: StreamingInsight[];
  onInsightClick?: (insight: StreamingInsight) => void;
}

const StreamingAnalytics: React.FC<StreamingAnalyticsProps> = ({
  analysisId,
  isRunning: propIsRunning,
  onInsightClick
}) => {
  const [displayedInsights, setDisplayedInsights] = useState<StreamingInsight[]>([]);
  const [animatingInsight, setAnimatingInsight] = useState<string | null>(null);

  // Use real streaming hook
  const {
    isConnected,
    isRunning: streamingIsRunning,
    events,
    latestEvent,
    progress,
    currentMessage,
    error
  } = useStreamingAnalysis(analysisId, true);

  // Use streaming state or prop fallback
  const isAnalysisRunning = streamingIsRunning || propIsRunning || false;

  // Convert streaming events to insights
  useEffect(() => {
    if (!latestEvent?.type) return;

    const event = latestEvent;
    let newInsight: StreamingInsight | null = null;

    switch (event.type) {
      case 'source_found':
        newInsight = {
          id: `source-${Date.now()}`,
          type: 'source_discovery',
          title: 'Key Source Discovered',
          content: event.message || 'Found relevant competitive intelligence source',
          timestamp: event.timestamp || new Date().toISOString(),
          credibility_score: 8.5,
          relevance_score: 8.5
        };
        break;

      case 'insight_discovered':
        newInsight = {
          id: `insight-${Date.now()}`,
          type: 'market_insight',
          title: 'Strategic Insight Discovered',
          content: event.message || 'New competitive insight identified',
          timestamp: event.timestamp || new Date().toISOString(),
          confidence_score: 8.0
        };
        break;

      case 'opportunity_generated':
        newInsight = {
          id: `opportunity-${Date.now()}`,
          type: 'opportunity_identified',
          title: 'Strategic Opportunity',
          content: event.message || 'Strategic opportunity identified',
          timestamp: event.timestamp || new Date().toISOString(),
          confidence_score: 8.0
        };
        break;

      case 'node_started':
      case 'node_completed':
      case 'node_execution':
        newInsight = {
          id: `node-${Date.now()}`,
          type: 'node_execution',
          title: 'Analysis Step',
          content: event.message || 'Executing analysis step',
          timestamp: event.timestamp || new Date().toISOString()
        };
        break;

      case 'search_started':
      case 'search_progress':
        newInsight = {
          id: `search-${Date.now()}`,
          type: 'search_progress',
          title: 'Researching Competitor',
          content: event.message || 'Analyzing competitive data',
          timestamp: event.timestamp || new Date().toISOString()
        };
        break;
    }

    if (newInsight) {
      setAnimatingInsight(newInsight.id);
      setDisplayedInsights(prev => [...prev, newInsight!]);
      
      // Remove animation after a short delay
      setTimeout(() => setAnimatingInsight(null), 500);
    }
  }, [latestEvent]);

  // Reset insights when analysis starts
  useEffect(() => {
    if (isAnalysisRunning && events.length === 0) {
      setDisplayedInsights([]);
    }
  }, [isAnalysisRunning, events.length]);

  const getInsightIcon = (type: StreamingInsight['type']) => {
    switch (type) {
      case 'source_discovery':
        return <FileText className="w-5 h-5 text-blue-600" />;
      case 'market_insight':
        return <TrendingUp className="w-5 h-5 text-green-600" />;
      case 'competitive_gap':
        return <Target className="w-5 h-5 text-red-600" />;
      case 'opportunity_identified':
        return <Lightbulb className="w-5 h-5 text-yellow-600" />;
      case 'node_execution':
        return <Zap className="w-5 h-5 text-purple-600" />;
      case 'search_progress':
        return <Search className="w-5 h-5 text-indigo-600" />;
      default:
        return <Brain className="w-5 h-5 text-gray-600" />;
    }
  };

  const getInsightColor = (type: StreamingInsight['type']) => {
    switch (type) {
      case 'source_discovery':
        return 'border-blue-200 bg-blue-50';
      case 'market_insight':
        return 'border-green-200 bg-green-50';
      case 'competitive_gap':
        return 'border-red-200 bg-red-50';
      case 'opportunity_identified':
        return 'border-yellow-200 bg-yellow-50';
      case 'node_execution':
        return 'border-purple-200 bg-purple-50';
      case 'search_progress':
        return 'border-indigo-200 bg-indigo-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  // Don't show if not running and no insights to display
  if (!isAnalysisRunning && displayedInsights.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Brain className="w-5 h-5 mr-2 text-primary-600" />
            {isAnalysisRunning ? 'Live Analysis Insights' : 'Recent Analysis Insights'}
          </h2>
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            {isAnalysisRunning && (
              <div className={`flex items-center space-x-2 text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-600 animate-pulse' : 'bg-red-600'}`}></div>
                <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>
            )}
            
            {/* Analysis Status */}
            {isAnalysisRunning ? (
              <div className="flex items-center space-x-2 text-sm text-blue-600">
                <Activity className="w-4 h-4" />
                <span>Analyzing in real-time</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-sm text-green-600">
                <CheckCircle className="w-4 h-4" />
                <span>Analysis insights</span>
              </div>
            )}
          </div>
        </div>
        
        {/* Progress Bar */}
        {isAnalysisRunning && progress > 0 && (
          <div className="mt-3">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>{currentMessage || 'Processing...'}</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-3 flex items-center space-x-2 text-sm text-red-600 bg-red-50 p-2 rounded">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}
      </div>
      
      <div className="p-6">
        {isAnalysisRunning && displayedInsights.length === 0 ? (
          <div className="text-center py-8">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4 animate-pulse" />
            <p className="text-gray-600 mb-2">
              {isConnected ? 'Initializing competitive intelligence scan...' : 'Connecting to analysis stream...'}
            </p>
            <p className="text-sm text-gray-500">
              <span className="inline-block animate-bounce">🔍</span> Scanning market data 
              <span className="inline-block animate-bounce" style={{animationDelay: '0.1s'}}> • </span>
              <span className="inline-block animate-bounce" style={{animationDelay: '0.2s'}}>📊</span> Analyzing competitors
              <span className="inline-block animate-bounce" style={{animationDelay: '0.3s'}}> • </span>
              <span className="inline-block animate-bounce" style={{animationDelay: '0.4s'}}>💡</span> Discovering insights
            </p>
          </div>
        ) : (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {displayedInsights.map((insight) => (
              <div
                key={insight.id}
                className={`
                  p-4 rounded-lg border transition-all duration-300 cursor-pointer
                  ${getInsightColor(insight.type)}
                  ${animatingInsight === insight.id ? 'scale-105 shadow-md' : 'hover:shadow-sm'}
                `}
                onClick={() => onInsightClick?.(insight)}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getInsightIcon(insight.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {insight.title}
                      </h4>
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        {insight.confidence_score && (
                          <span className="bg-gray-200 px-2 py-1 rounded">
                            {(insight.confidence_score * 10).toFixed(0)}% confidence
                          </span>
                        )}
                        <span>{new Date(insight.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                      {insight.content}
                    </p>
                    {insight.source_url && (
                      <div className="flex items-center mt-2 text-xs text-blue-600">
                        <ExternalLink className="w-3 h-3 mr-1" />
                        <span className="truncate">Source available</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StreamingAnalytics; 