import React from 'react';
import { AlertTriangle, Clock, DollarSign, TrendingUp, Target, Zap } from 'lucide-react';
import type { CompetitiveGap } from '../lib/api';

interface GapMatrixProps {
  gaps: CompetitiveGap[];
  className?: string;
}

const GapMatrix: React.FC<GapMatrixProps> = ({ gaps, className = '' }) => {
  // Organize gaps by type and severity for matrix display
  const gapTypes = ['feature', 'pricing', 'market_position', 'clinical', 'technology'] as const;
  const severityLevels = ['critical', 'high', 'medium', 'low'] as const;

  const getGapIcon = (gapType: CompetitiveGap['gap_type']) => {
    switch (gapType) {
      case 'feature': return <Target className="w-4 h-4" />;
      case 'pricing': return <DollarSign className="w-4 h-4" />;
      case 'market_position': return <TrendingUp className="w-4 h-4" />;
      case 'clinical': return <AlertTriangle className="w-4 h-4" />;
      case 'technology': return <Zap className="w-4 h-4" />;
      default: return <Target className="w-4 h-4" />;
    }
  };

  const getSeverityColor = (severity: CompetitiveGap['severity']) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 border-red-300 text-red-800';
      case 'high': return 'bg-orange-100 border-orange-300 text-orange-800';
      case 'medium': return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      case 'low': return 'bg-green-100 border-green-300 text-green-800';
      default: return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  const getInvestmentBadge = (investment: CompetitiveGap['investment_required']) => {
    const colors = {
      low: 'bg-green-100 text-green-700',
      medium: 'bg-yellow-100 text-yellow-700',
      high: 'bg-red-100 text-red-700'
    };
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[investment]}`}>
        {investment.charAt(0).toUpperCase() + investment.slice(1)} Investment
      </span>
    );
  };

  // Group gaps by type for display
  const gapsByType = gapTypes.reduce((acc, type) => {
    acc[type] = gaps.filter(gap => gap.gap_type === type);
    return acc;
  }, {} as Record<string, CompetitiveGap[]>);

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Competitive Gap Matrix</h3>
            <p className="text-sm text-gray-600">
              Visual overview of competitive gaps by type and severity
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-gray-400" />
            <span className="text-sm text-gray-500">Updated {new Date().toLocaleDateString()}</span>
          </div>
        </div>

        {/* Matrix Grid */}
        <div className="space-y-6">
          {gapTypes.map(gapType => {
            const typeGaps = gapsByType[gapType] || [];
            const typeLabel = gapType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            return (
              <div key={gapType} className="border rounded-lg p-4 bg-gray-50">
                <div className="flex items-center mb-3">
                  {getGapIcon(gapType)}
                  <h4 className="ml-2 font-medium text-gray-900">{typeLabel}</h4>
                  <span className="ml-2 bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-xs">
                    {typeGaps.length} gap{typeGaps.length !== 1 ? 's' : ''}
                  </span>
                </div>

                {typeGaps.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Target className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>No {typeLabel.toLowerCase()} gaps identified</p>
                  </div>
                ) : (
                  <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                    {typeGaps.map(gap => (
                      <div
                        key={gap.id}
                        className={`p-3 rounded-lg border-2 ${getSeverityColor(gap.severity)}`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h5 className="font-medium text-sm leading-tight">{gap.title}</h5>
                          <span className="text-xs font-bold ml-2 flex-shrink-0">
                            {gap.opportunity_score}/10
                          </span>
                        </div>
                        
                        <p className="text-xs mb-3 line-clamp-2">{gap.description}</p>
                        
                        <div className="space-y-2">
                          {getInvestmentBadge(gap.investment_required)}
                          
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-600">Timeline:</span>
                            <span className="font-medium">{gap.time_to_close}</span>
                          </div>
                          
                          {gap.recommended_actions.length > 0 && (
                            <div className="text-xs">
                              <span className="text-gray-600">Next step:</span>
                              <span className="ml-1 font-medium">
                                {gap.recommended_actions[0]}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Summary Stats */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          {severityLevels.map(severity => {
            const count = gaps.filter(gap => gap.severity === severity).length;
            return (
              <div key={severity} className="text-center">
                <div className={`w-8 h-8 rounded-full mx-auto mb-1 flex items-center justify-center ${getSeverityColor(severity)}`}>
                  <span className="text-sm font-bold">{count}</span>
                </div>
                <p className="text-xs text-gray-600 capitalize">{severity}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default GapMatrix; 