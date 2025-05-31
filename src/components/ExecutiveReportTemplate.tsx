import React from 'react';
import { 
  TrendingUp, 
  Target, 
  AlertTriangle, 
  CheckCircle, 
  Calendar,
  Building,
  Users,
  DollarSign,
  BarChart3,
  FileText,
  Award,
  Lightbulb
} from 'lucide-react';
import type { AnalysisResult, StrategicOpportunity } from '../lib/api';

export interface ExecutiveReportProps {
  analysisResult: AnalysisResult;
  clientName?: string;
  reportDate?: Date;
  analystName?: string;
  companyLogo?: string;
  customBranding?: {
    primaryColor?: string;
    secondaryColor?: string;
    logoUrl?: string;
  };
}

export interface ReportSection {
  id: string;
  title: string;
  content: React.ReactNode;
  priority: 'high' | 'medium' | 'low';
}

const ExecutiveReportTemplate: React.FC<ExecutiveReportProps> = ({
  analysisResult,
  clientName = "Client Organization",
  reportDate = new Date(),
  analystName = "Orthopedic Intelligence Team",
  customBranding
}) => {
  const primaryColor = customBranding?.primaryColor || '#2563eb';
  const secondaryColor = customBranding?.secondaryColor || '#64748b';

  // Calculate key metrics
  const totalOpportunities = analysisResult.top_opportunities.length;
  const highValueOpportunities = analysisResult.top_opportunities.filter(
    opp => opp.opportunity_score >= 8.5
  ).length;
  const averageScore = analysisResult.top_opportunities.reduce(
    (sum, opp) => sum + opp.opportunity_score, 0
  ) / totalOpportunities || 0;

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getOpportunityIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'market_expansion':
        return <TrendingUp className="w-5 h-5" />;
      case 'product_development':
        return <Lightbulb className="w-5 h-5" />;
      case 'competitive_advantage':
        return <Award className="w-5 h-5" />;
      case 'strategic_partnership':
        return <Users className="w-5 h-5" />;
      default:
        return <Target className="w-5 h-5" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 9) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 7) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getInvestmentColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return 'text-green-600 bg-green-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'high':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white">
      {/* Report Header */}
      <div className="border-b-4 border-gray-900 pb-8 mb-8">
        <div className="flex items-center justify-between mb-6">
          {customBranding?.logoUrl ? (
            <img 
              src={customBranding.logoUrl} 
              alt="Company Logo" 
              className="h-12 w-auto"
            />
          ) : (
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Orthopedic Intelligence</h1>
                <p className="text-sm text-gray-600">Competitive Analysis Report</p>
              </div>
            </div>
          )}
          
          <div className="text-right">
            <p className="text-sm text-gray-600">Report Date</p>
            <p className="font-semibold text-gray-900">{formatDate(reportDate)}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-gray-600 mb-1">Prepared For</p>
            <p className="font-semibold text-gray-900 flex items-center">
              <Building className="w-4 h-4 mr-2" />
              {clientName}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Analysis ID</p>
            <p className="font-mono text-sm text-gray-700">{analysisResult.analysis_id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Analyst</p>
            <p className="font-semibold text-gray-900">{analystName}</p>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <FileText className="w-6 h-6 mr-3" style={{ color: primaryColor }} />
          Executive Summary
        </h2>
        
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Insight</h3>
          <p className="text-gray-700 leading-relaxed">
            {analysisResult.executive_summary.key_insight}
          </p>
        </div>

        {/* Key Metrics Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <Target className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{totalOpportunities}</p>
            <p className="text-sm text-gray-600">Total Opportunities</p>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <Award className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{highValueOpportunities}</p>
            <p className="text-sm text-gray-600">High-Value Opportunities</p>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <BarChart3 className="w-8 h-8 text-purple-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{averageScore.toFixed(1)}</p>
            <p className="text-sm text-gray-600">Average Score</p>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{analysisResult.confidence_score}%</p>
            <p className="text-sm text-gray-600">Confidence Score</p>
          </div>
        </div>

        {/* Strategic Recommendations */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center">
            <Lightbulb className="w-5 h-5 mr-2" />
            Strategic Recommendations
          </h3>
          <ul className="space-y-2">
            {analysisResult.executive_summary.strategic_recommendations.map((rec, index) => (
              <li key={index} className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <span className="text-blue-800">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Strategic Opportunities Analysis */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <TrendingUp className="w-6 h-6 mr-3" style={{ color: primaryColor }} />
          Strategic Opportunities Analysis
        </h2>

        <div className="space-y-6">
          {analysisResult.top_opportunities.map((opportunity, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1" style={{ color: primaryColor }}>
                    {getOpportunityIcon(opportunity.category)}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {opportunity.title}
                    </h3>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      {opportunity.description}
                    </p>
                  </div>
                </div>
                
                <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getScoreColor(opportunity.opportunity_score)}`}>
                  {opportunity.opportunity_score.toFixed(1)}/10
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Time to Market</p>
                  <p className="text-gray-900">{opportunity.time_to_market}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Investment Level</p>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getInvestmentColor(opportunity.investment_level)}`}>
                    {opportunity.investment_level}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Implementation</p>
                  <p className="text-gray-900">{opportunity.implementation_difficulty}</p>
                </div>
              </div>

              {opportunity.next_steps && opportunity.next_steps.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Recommended Next Steps</h4>
                  <ul className="space-y-1">
                    {opportunity.next_steps.map((step, stepIndex) => (
                      <li key={stepIndex} className="flex items-start space-x-2 text-sm">
                        <span className="w-5 h-5 bg-gray-200 text-gray-700 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">
                          {stepIndex + 1}
                        </span>
                        <span className="text-gray-700">{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Market Analysis Summary */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <BarChart3 className="w-6 h-6 mr-3" style={{ color: primaryColor }} />
          Market Analysis Summary
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Revenue Potential</h3>
            <p className="text-gray-700">{analysisResult.executive_summary.revenue_potential}</p>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Market Share Opportunity</h3>
            <p className="text-gray-700">{analysisResult.executive_summary.market_share_opportunity}</p>
          </div>
        </div>
      </section>

      {/* Report Footer */}
      <footer className="border-t border-gray-200 pt-8 mt-12">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            <p>© 2024 Orthopedic Intelligence Platform</p>
            <p>Confidential and Proprietary</p>
          </div>
          <div className="text-right">
            <p>Generated on {formatDate(new Date())}</p>
            <p>Report ID: {analysisResult.analysis_id}</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ExecutiveReportTemplate; 