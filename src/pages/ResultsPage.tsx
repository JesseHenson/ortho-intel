import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { 
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Search,
  BookOpen,
  Download,
  FileText
} from 'lucide-react';

import { getAnalysisStatus, getAnalysisResult } from '../lib/api';
import type { AnalysisStatus, AnalysisResult } from '../lib/api';
import LoadingSpinner from '../components/LoadingSpinner';
import StreamingAnalytics, { type StreamingInsight } from '../components/StreamingAnalytics';
import { pdfExportService } from '../services/pdfExportService';

const ResultsPage = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const [expandedOpportunities, setExpandedOpportunities] = useState<Set<number>>(new Set());
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());

  const toggleOpportunityExpansion = (index: number) => {
    setExpandedOpportunities(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const toggleSourceExpansion = (sourceKey: string) => {
    setExpandedSources(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sourceKey)) {
        newSet.delete(sourceKey);
      } else {
        newSet.add(sourceKey);
      }
      return newSet;
    });
  };

  const handleExportFullReport = async () => {
    if (!result) return;
    
    try {
      await pdfExportService.exportAnalysisReport(result, {
        clientName: 'Marketing Client',
        analystName: 'Orthopedic Intelligence Team',
        includeWatermark: false,
        customBranding: {
          companyName: 'Orthopedic Intelligence',
          primaryColor: '#2563eb'
        }
      });
    } catch (error) {
      console.error('Error exporting PDF:', error);
    }
  };

  const handleExportOpportunity = async (opportunityIndex: number) => {
    if (!result || !result.top_opportunities[opportunityIndex]) return;
    
    try {
      await pdfExportService.exportOpportunitySnapshot(
        result.top_opportunities[opportunityIndex],
        {
          clientName: 'Marketing Client',
          customBranding: {
            companyName: 'Orthopedic Intelligence',
            primaryColor: '#2563eb'
          }
        }
      );
    } catch (error) {
      console.error('Error exporting opportunity:', error);
    }
  };

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

  // Show loading state
  if (statusLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <h2 className="mt-4 text-lg font-medium text-gray-900">Loading Analysis...</h2>
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

      {/* Live Streaming Analytics */}
      <StreamingAnalytics
        analysisId={analysisId || ''}
        isRunning={status.status === 'running'}
        onInsightClick={(insight: StreamingInsight) => {
          console.log('Insight clicked:', insight);
          // TODO: Implement insight detail modal or navigation
        }}
      />

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

              {/* Export Options */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                    <FileText className="w-5 h-5 mr-2 text-primary-600" />
                    Export Options
                  </h2>
                </div>
                <div className="p-6">
                  <div className="flex flex-wrap gap-4">
                    <button
                      onClick={handleExportFullReport}
                      className="btn-primary flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download Full Report (PDF)</span>
                    </button>
                    
                    <button
                      onClick={() => {
                        // Export executive summary only
                        if (result) {
                          pdfExportService.exportAnalysisReport(result, {
                            clientName: 'Marketing Client',
                            sections: {
                              executiveSummary: true,
                              opportunities: false,
                              sourceEvidence: false,
                              marketAnalysis: true
                            }
                          });
                        }
                      }}
                      className="btn-secondary flex items-center space-x-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors"
                    >
                      <FileText className="w-4 h-4" />
                      <span>Executive Summary (PDF)</span>
                    </button>

                    <div className="text-sm text-gray-600 mt-2">
                      <p>• Full Report includes all opportunities, evidence, and analysis</p>
                      <p>• Individual opportunity exports available from each opportunity card</p>
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
                      {result.top_opportunities.map((opportunity, index) => {
                        const isExpanded = expandedOpportunities.has(index);
                        const maxDescriptionLength = 300;
                        const needsExpansion = opportunity.description.length > maxDescriptionLength;
                        const displayDescription = isExpanded || !needsExpansion 
                          ? opportunity.description 
                          : opportunity.description.substring(0, maxDescriptionLength) + '...';

                        return (
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
                                  <span className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                                    {opportunity.category}
                                  </span>
                                </div>
                              </div>
                              <div className="flex items-start space-x-2">
                                <button
                                  onClick={() => toggleOpportunityExpansion(index)}
                                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                                  title={expandedOpportunities.has(index) ? "Collapse details" : "Expand details"}
                                >
                                  {expandedOpportunities.has(index) ? (
                                    <ChevronUp className="w-5 h-5" />
                                  ) : (
                                    <ChevronDown className="w-5 h-5" />
                                  )}
                                </button>
                                
                                <button
                                  onClick={() => handleExportOpportunity(index)}
                                  className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                                  title="Export opportunity as PDF"
                                >
                                  <Download className="w-5 h-5" />
                                </button>
                              </div>
                            </div>
                            
                            <div className="mb-6">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium text-gray-900">Opportunity Description</h4>
                                {needsExpansion && (
                                  <button
                                    onClick={() => toggleOpportunityExpansion(index)}
                                    className="flex items-center text-sm text-primary-600 hover:text-primary-700 transition-colors"
                                  >
                                    {isExpanded ? (
                                      <>
                                        <ChevronUp className="w-4 h-4 mr-1" />
                                        Show Less
                                      </>
                                    ) : (
                                      <>
                                        <ChevronDown className="w-4 h-4 mr-1" />
                                        Show More
                                      </>
                                    )}
                                  </button>
                                )}
                              </div>
                              <p className="text-gray-700 leading-relaxed">
                                {displayDescription}
                              </p>
                            </div>

                            {/* Source Evidence Analysis */}
                            <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
                              <h4 className="font-medium text-amber-900 mb-3 flex items-center">
                                <Search className="w-4 h-4 mr-2" />
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
                                  <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                                    <BookOpen className="w-4 h-4 mr-2" />
                                    Supporting Evidence
                                  </h4>
                                  <div className="space-y-3">
                                    {opportunity.sources.slice(0, 2).map((source, sourceIndex) => {
                                      const sourceKey = `${index}-${sourceIndex}`;
                                      const isSourceExpanded = expandedSources.has(sourceKey);
                                      
                                      return (
                                        <div key={sourceIndex} className="border border-gray-200 rounded-lg p-3 bg-gray-50 hover:bg-gray-100 transition-colors">
                                          <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center space-x-2">
                                              <span className="text-sm font-medium text-gray-900">
                                                {source.title}
                                              </span>
                                              {source.url && (
                                                <a
                                                  href={source.url}
                                                  target="_blank"
                                                  rel="noopener noreferrer"
                                                  className="text-primary-600 hover:text-primary-700 transition-colors"
                                                  title="Open source"
                                                >
                                                  <ExternalLink className="w-4 h-4" />
                                                </a>
                                              )}
                                            </div>
                                            <div className="flex items-center space-x-2">
                                              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                                Credibility: {source.credibility_score}/10
                                              </span>
                                              <button
                                                onClick={() => toggleSourceExpansion(sourceKey)}
                                                className="text-xs text-primary-600 hover:text-primary-700 transition-colors"
                                              >
                                                {isSourceExpanded ? (
                                                  <ChevronUp className="w-3 h-3" />
                                                ) : (
                                                  <ChevronDown className="w-3 h-3" />
                                                )}
                                              </button>
                                            </div>
                                          </div>
                                          <p className={`text-xs text-gray-600 leading-relaxed ${isSourceExpanded ? '' : 'line-clamp-2'}`}>
                                            {source.content_snippet}
                                          </p>
                                          {isSourceExpanded && (
                                            <div className="mt-2 pt-2 border-t border-gray-200">
                                              <p className="text-xs text-gray-500">
                                                Relevance Score: {source.relevance_score}/10 | Retrieved: {new Date(source.retrieved_at).toLocaleDateString()}
                                              </p>
                                            </div>
                                          )}
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
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