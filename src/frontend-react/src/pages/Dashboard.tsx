import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  PlusCircle, 
  BarChart3, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  TrendingUp,
  Target,
  Users
} from 'lucide-react';

import { listAnalyses, healthCheck } from '../lib/api';
import type { AnalysisListItem } from '../lib/api';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const [systemStatus, setSystemStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Check system health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await healthCheck();
        setSystemStatus('online');
      } catch (error) {
        setSystemStatus('offline');
      }
    };
    checkHealth();
  }, []);

  // Fetch recent analyses
  const { data: analyses = [], isLoading, error } = useQuery<AnalysisListItem[]>({
    queryKey: ['analyses'],
    queryFn: listAnalyses,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Ensure analyses is always an array to prevent slice errors
  const analysesArray = Array.isArray(analyses) ? analyses : [];

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gradient-primary mb-4">
          🎯 Orthopedic Intelligence Dashboard
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Competitive Intelligence Platform for Medical Device Manufacturing
        </p>
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus === 'online' ? 'bg-opportunity-500' :
              systemStatus === 'offline' ? 'bg-risk-500' : 'bg-gray-400'
            }`}></div>
            <span className="font-medium text-gray-900">
              System Status: {systemStatus === 'online' ? 'Online' : 
                            systemStatus === 'offline' ? 'Offline' : 'Checking...'}
            </span>
          </div>
          
          {systemStatus === 'online' && (
            <div className="text-sm text-gray-600">
              All services operational
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/analysis"
          className="bg-white rounded-lg shadow-card p-6 hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 group"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 gradient-primary rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <PlusCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">New Analysis</h3>
              <p className="text-sm text-gray-600">Start competitive analysis</p>
            </div>
          </div>
        </Link>

        <Link
          to="/focus-areas"
          className="bg-white rounded-lg shadow-card p-6 hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 group"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 gradient-opportunity rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Focus Areas</h3>
              <p className="text-sm text-gray-600">Spine, Hip, Knee, Trauma</p>
            </div>
          </div>
        </Link>

        <Link
          to="/competitors"
          className="bg-white rounded-lg shadow-card p-6 hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 group"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 gradient-strategic rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Competitors</h3>
              <p className="text-sm text-gray-600">Track market leaders</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent Analyses */}
      <div className="bg-white rounded-lg shadow-card">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>Recent Analyses</span>
            </h2>
            
            {analysesArray.length > 0 && (
              <span className="text-sm text-gray-600">
                {analysesArray.length} total analyses
              </span>
            )}
          </div>
        </div>

        <div className="p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner />
              <span className="ml-3 text-gray-600">Loading analyses...</span>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-risk-500 mx-auto mb-3" />
              <p className="text-gray-600">Failed to load analyses</p>
              <p className="text-sm text-gray-500 mt-2">
                {error.message || 'Unknown error occurred'}
              </p>
            </div>
          ) : analysesArray.length === 0 ? (
            <div className="text-center py-12">
              <TrendingUp className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No analyses yet
              </h3>
              <p className="text-gray-600 mb-6">
                Start your first competitive analysis to see results here
              </p>
              <Link to="/analysis" className="btn-primary">
                Start Analysis
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {analysesArray.slice(0, 5).map((analysis: AnalysisListItem) => (
                <div key={analysis.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className={`w-3 h-3 rounded-full ${
                      analysis.status === 'completed' ? 'bg-opportunity-500' :
                      analysis.status === 'running' ? 'bg-strategic-500' :
                      analysis.status === 'failed' ? 'bg-risk-500' : 'bg-gray-400'
                    }`}></div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {analysis.competitors?.join(', ') || 'Competitive Analysis'}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {analysis.focus_area || 'Market Analysis'} • {analysis.created_at || 'Recently'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    {analysis.status === 'completed' ? (
                      <CheckCircle className="w-5 h-5 text-opportunity-500" />
                    ) : analysis.status === 'running' ? (
                      <Clock className="w-5 h-5 text-strategic-500" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-risk-500" />
                    )}
                    
                    {analysis.status === 'completed' && (
                      <Link
                        to={`/results/${analysis.id}`}
                        className="btn-outline text-sm"
                      >
                        View Results
                      </Link>
                    )}
                  </div>
                </div>
              ))}
              
              {analysesArray.length > 5 && (
                <div className="text-center pt-4">
                  <button className="btn-secondary">
                    View All Analyses ({analysesArray.length})
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 