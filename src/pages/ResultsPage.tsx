import React, { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
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
  FileText,
  Loader2
} from 'lucide-react';

import { getAnalysisStatus, getAnalysisResult, getComprehensiveAnalysisResult } from '../lib/api';
import type { AnalysisStatus, AnalysisResult } from '../lib/api';
import LoadingSpinner from '../components/LoadingSpinner';
import StreamingAnalytics, { type StreamingInsight } from '../components/StreamingAnalytics';
import { pdfExportService } from '../services/pdfExportService';
import { useStreamingAnalysis } from '../hooks/useStreamingAnalysis';
import GapAnalysisTab from '../components/GapAnalysisTab';
import ComprehensiveAnalysisView from '../components/ComprehensiveAnalysisView';

const ResultsPage = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const [expandedOpportunities, setExpandedOpportunities] = useState<Set<number>>(new Set());
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState<'comprehensive' | 'analysis' | 'gaps'>('comprehensive');

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

  // Fetch comprehensive data when status is completed
  const { data: comprehensiveData, error: comprehensiveError } = useQuery({
    queryKey: ['comprehensive-analysis', analysisId],
    queryFn: () => getComprehensiveAnalysisResult(analysisId!),
    enabled: !!analysisId && status === 'completed',
    retry: false,
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Analysis Results
        </h1>
        <p className="text-lg text-gray-600">
          Analysis ID: {analysisId}
        </p>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {status === 'completed' && result && comprehensiveData ? (
          <div className="space-y-6">
            {/* Tab Navigation */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                  <button
                    onClick={() => setActiveTab('comprehensive')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'comprehensive'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    📊 Complete Analysis
                  </button>
                  <button
                    onClick={() => setActiveTab('analysis')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'analysis'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    🎯 Strategic Summary
                  </button>
                  <button
                    onClick={() => setActiveTab('gaps')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'gaps'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    🔍 Gap Analysis
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {activeTab === 'comprehensive' && (
                  <ComprehensiveAnalysisView analysisResult={comprehensiveData} />
                )}
                {activeTab === 'analysis' && (
                  <div>
                    {/* Executive Summary */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <h2 className="text-2xl font-bold text-gray-900 mb-4">Executive Summary</h2>
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-blue-900 mb-2">Key Insight</h3>
                        <p className="text-blue-800 mb-4">{result.executive_summary.key_insight}</p>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          <div>
                            <h4 className="font-medium text-blue-900">Revenue Potential</h4>
                            <p className="text-blue-700">{result.executive_summary.revenue_potential}</p>
                          </div>
                          <div>
                            <h4 className="font-medium text-blue-900">Market Share Opportunity</h4>
                            <p className="text-blue-700">{result.executive_summary.market_share_opportunity}</p>
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-blue-900 mb-2">Strategic Recommendations</h4>
                          <ul className="space-y-1">
                            {result.executive_summary.strategic_recommendations.map((rec, index) => (
                              <li key={index} className="text-blue-700 flex items-start">
                                <span className="text-blue-500 mr-2">•</span>
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Strategic Opportunities */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <h2 className="text-2xl font-bold text-gray-900 mb-6">Strategic Opportunities</h2>
                      <div className="space-y-6">
                        {result.top_opportunities.map((opportunity, index) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start mb-4">
                              <div className="flex-1">
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">{opportunity.title}</h3>
                                <div className="flex items-center space-x-4 mb-3">
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    {opportunity.category}
                                  </span>
                                  <span className="text-sm text-gray-600">
                                    Score: <span className="font-semibold text-blue-600">{opportunity.opportunity_score.toFixed(1)}/10</span>
                                  </span>
                                  <span className="text-sm text-gray-600">
                                    Timeline: <span className="font-medium">{opportunity.time_to_market}</span>
                                  </span>
                                </div>
                              </div>
                            </div>
                            
                            <p className="text-gray-700 mb-4 leading-relaxed">{opportunity.description}</p>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                              <div>
                                <h4 className="font-medium text-gray-900 mb-2">Investment Level</h4>
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  opportunity.investment_level === 'Low' ? 'bg-green-100 text-green-800' :
                                  opportunity.investment_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {opportunity.investment_level}
                                </span>
                              </div>
                              <div>
                                <h4 className="font-medium text-gray-900 mb-2">Implementation Difficulty</h4>
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  opportunity.implementation_difficulty === 'Low' ? 'bg-green-100 text-green-800' :
                                  opportunity.implementation_difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {opportunity.implementation_difficulty}
                                </span>
                              </div>
                            </div>
                            
                            {opportunity.evidence && (
                              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                                <h4 className="font-medium text-gray-900 mb-2">Evidence</h4>
                                <p className="text-gray-700 text-sm leading-relaxed">{opportunity.evidence}</p>
                              </div>
                            )}
                            
                            <div className="bg-blue-50 rounded-lg p-4">
                              <h4 className="font-medium text-gray-900 mb-2">Next Steps</h4>
                              <ul className="space-y-1">
                                {opportunity.next_steps.map((step, stepIndex) => (
                                  <li key={stepIndex} className="text-gray-700 text-sm flex items-start">
                                    <span className="text-blue-500 mr-2">•</span>
                                    {step}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Analysis Metadata */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <h2 className="text-2xl font-bold text-gray-900 mb-4">Analysis Details</h2>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="text-2xl font-bold text-gray-900">{result.confidence_score.toFixed(1)}/10</div>
                          <div className="text-sm text-gray-600">Confidence Score</div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="text-2xl font-bold text-gray-900">{result.metadata.total_sources}</div>
                          <div className="text-sm text-gray-600">Sources Analyzed</div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="text-2xl font-bold text-gray-900">{result.metadata.competitors_analyzed.length}</div>
                          <div className="text-sm text-gray-600">Competitors</div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="text-lg font-bold text-gray-900">{result.metadata.analysis_duration}</div>
                          <div className="text-sm text-gray-600">Duration</div>
                        </div>
                      </div>
                      <div className="mt-4">
                        <h3 className="font-medium text-gray-900 mb-2">Competitors Analyzed</h3>
                        <div className="flex flex-wrap gap-2">
                          {result.metadata.competitors_analyzed.map((competitor, index) => (
                            <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-md">
                              {competitor}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                {activeTab === 'gaps' && result && (
                  <GapAnalysisTab analysisResult={result} />
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            <StreamingAnalytics 
              analysisId={analysisId!}
              onComplete={() => {
                refetch();
              }}
            />
          </div>
        )}
      </main>
    </div>
  );
};

export default ResultsPage; 