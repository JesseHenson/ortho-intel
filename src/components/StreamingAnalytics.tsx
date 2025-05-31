import React, { useState, useEffect } from 'react';
import { 
  Search, 
  TrendingUp, 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  ExternalLink,
  Brain,
  Target,
  FileText,
  Lightbulb
} from 'lucide-react';

export interface StreamingInsight {
  id: string;
  type: 'source_discovery' | 'market_insight' | 'competitive_gap' | 'opportunity_identified';
  title: string;
  content: string;
  source_url?: string;
  credibility_score?: number;
  timestamp: string;
  relevance_score?: number;
}

export interface StreamingAnalyticsProps {
  analysisId: string;
  isRunning: boolean;
  insights?: StreamingInsight[];
  onInsightClick?: (insight: StreamingInsight) => void;
}

const StreamingAnalytics: React.FC<StreamingAnalyticsProps> = ({
  analysisId,
  isRunning,
  insights = [],
  onInsightClick
}) => {
  const [displayedInsights, setDisplayedInsights] = useState<StreamingInsight[]>([]);
  const [animatingInsight, setAnimatingInsight] = useState<string | null>(null);

  // Simulate real-time streaming for demonstration
  useEffect(() => {
    if (!isRunning) return;

    // Mock streaming insights for demonstration
    const mockInsights: StreamingInsight[] = [
      {
        id: '1',
        type: 'source_discovery',
        title: 'Key Source Discovered',
        content: 'Found comprehensive market analysis on knee replacement trends from leading orthopedic journal',
        source_url: 'https://example.com/orthopedic-research',
        credibility_score: 9.2,
        timestamp: new Date().toISOString(),
        relevance_score: 8.8
      },
      {
        id: '2',
        type: 'competitive_gap',
        title: 'Competitive Gap Identified',
        content: 'Zimmer Biomet lacks advanced robotics integration compared to Stryker in minimally invasive procedures',
        timestamp: new Date(Date.now() + 5000).toISOString(),
        relevance_score: 9.1
      },
      {
        id: '3',
        type: 'market_insight',
        title: 'Market Trend Analysis',
        content: 'Growing demand for personalized knee implants with 3D printing technology driving 15% market growth',
        timestamp: new Date(Date.now() + 10000).toISOString(),
        relevance_score: 8.7
      },
      {
        id: '4',
        type: 'opportunity_identified',
        title: 'Strategic Opportunity',
        content: 'Untapped market in ambulatory surgery centers for simplified knee replacement procedures',
        timestamp: new Date(Date.now() + 15000).toISOString(),
        relevance_score: 9.3
      }
    ];

    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < mockInsights.length) {
        const newInsight = mockInsights[currentIndex];
        setAnimatingInsight(newInsight.id);
        
        setDisplayedInsights(prev => [...prev, newInsight]);
        
        // Remove animation after a short delay
        setTimeout(() => setAnimatingInsight(null), 500);
        
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [isRunning]);

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
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  if (!isRunning && displayedInsights.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Brain className="w-5 h-5 mr-2 text-primary-600" />
            Live Analysis Insights
          </h2>
          {isRunning && (
            <div className="flex items-center space-x-2 text-sm text-blue-600">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
              <span>Analyzing in real-time</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="p-6">
        {isRunning && displayedInsights.length === 0 ? (
          <div className="text-center py-8">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4 animate-pulse" />
            <p className="text-gray-600">Analyzing sources and discovering insights...</p>
          </div>
        ) : (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {displayedInsights.map((insight) => (
              <div
                key={insight.id}
                className={`
                  border rounded-lg p-4 transition-all duration-500 cursor-pointer hover:shadow-md
                  ${getInsightColor(insight.type)}
                  ${animatingInsight === insight.id ? 'scale-105 shadow-lg' : ''}
                `}
                onClick={() => onInsightClick?.(insight)}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    {getInsightIcon(insight.type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {insight.title}
                      </h4>
                      <div className="flex items-center space-x-2 flex-shrink-0 ml-2">
                        {insight.relevance_score && (
                          <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                            {insight.relevance_score}/10
                          </span>
                        )}
                        {insight.source_url && (
                          <a
                            href={insight.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-500 hover:text-gray-700 transition-colors"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {insight.content}
                    </p>
                    
                    <div className="flex items-center justify-between mt-3">
                      <span className="text-xs text-gray-500">
                        {new Date(insight.timestamp).toLocaleTimeString()}
                      </span>
                      
                      {insight.credibility_score && (
                        <div className="flex items-center space-x-1">
                          <CheckCircle className="w-3 h-3 text-green-500" />
                          <span className="text-xs text-green-700">
                            Credibility: {insight.credibility_score}/10
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {!isRunning && displayedInsights.length > 0 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              Analysis complete • {displayedInsights.length} insights discovered
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StreamingAnalytics; 