import React from 'react';
import { Check, X, AlertCircle, Star, TrendingUp } from 'lucide-react';
import type { FeatureComparison as FeatureComparisonType } from '../lib/api';

interface FeatureComparisonProps {
  comparisons: FeatureComparisonType[];
  className?: string;
}

const FeatureComparison: React.FC<FeatureComparisonProps> = ({ comparisons, className = '' }) => {
  const getCapabilityIcon = (capability: FeatureComparisonType['our_capability']) => {
    switch (capability) {
      case 'superior': return <Star className="w-4 h-4 text-yellow-500" />;
      case 'competitive': return <Check className="w-4 h-4 text-green-500" />;
      case 'basic': return <AlertCircle className="w-4 h-4 text-orange-500" />;
      case 'missing': return <X className="w-4 h-4 text-red-500" />;
      default: return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getCapabilityColor = (capability: FeatureComparisonType['our_capability']) => {
    switch (capability) {
      case 'superior': return 'bg-yellow-50 text-yellow-800';
      case 'competitive': return 'bg-green-50 text-green-800';
      case 'basic': return 'bg-orange-50 text-orange-800';
      case 'missing': return 'bg-red-50 text-red-800';
      default: return 'bg-gray-50 text-gray-800';
    }
  };

  const getGapSeverityColor = (severity: FeatureComparisonType['gap_severity']) => {
    switch (severity) {
      case 'major': return 'text-red-600 font-semibold';
      case 'moderate': return 'text-orange-600 font-medium';
      case 'minor': return 'text-yellow-600';
      case 'none': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getImportanceStars = (importance: number) => {
    return Array.from({ length: 10 }, (_, i) => (
      <Star
        key={i}
        className={`w-3 h-3 ${i < importance ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  // Get all competitors from the data
  const allCompetitors = [...new Set(
    comparisons.flatMap(comp => Object.keys(comp.competitor_capabilities))
  )];

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Feature Comparison Matrix</h3>
            <p className="text-sm text-gray-600">
              Detailed feature-by-feature competitive analysis
            </p>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-400" />
              <span>Market Importance (1-10)</span>
            </div>
          </div>
        </div>

        {comparisons.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">No Feature Comparisons Available</p>
            <p>Feature comparisons will appear here once analysis is complete.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Feature</th>
                  <th className="text-center py-3 px-4 font-medium text-gray-900">Our Capability</th>
                  {allCompetitors.map(competitor => (
                    <th key={competitor} className="text-center py-3 px-4 font-medium text-gray-900">
                      {competitor}
                    </th>
                  ))}
                  <th className="text-center py-3 px-4 font-medium text-gray-900">Market Importance</th>
                  <th className="text-center py-3 px-4 font-medium text-gray-900">Gap Severity</th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map((comparison, index) => (
                  <tr
                    key={index}
                    className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                  >
                    {/* Feature Name */}
                    <td className="py-4 px-4">
                      <div>
                        <h4 className="font-medium text-gray-900">{comparison.feature_name}</h4>
                        {comparison.improvement_opportunity && (
                          <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                            {comparison.improvement_opportunity}
                          </p>
                        )}
                      </div>
                    </td>

                    {/* Our Capability */}
                    <td className="py-4 px-4 text-center">
                      <div className="flex items-center justify-center space-x-2">
                        {getCapabilityIcon(comparison.our_capability)}
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCapabilityColor(comparison.our_capability)}`}>
                          {comparison.our_capability.charAt(0).toUpperCase() + comparison.our_capability.slice(1)}
                        </span>
                      </div>
                    </td>

                    {/* Competitor Capabilities */}
                    {allCompetitors.map(competitor => {
                      const capability = comparison.competitor_capabilities[competitor] || 'missing';
                      return (
                        <td key={competitor} className="py-4 px-4 text-center">
                          <div className="flex items-center justify-center space-x-2">
                            {getCapabilityIcon(capability)}
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCapabilityColor(capability)}`}>
                              {capability.charAt(0).toUpperCase() + capability.slice(1)}
                            </span>
                          </div>
                        </td>
                      );
                    })}

                    {/* Market Importance */}
                    <td className="py-4 px-4 text-center">
                      <div className="flex items-center justify-center space-x-1">
                        {getImportanceStars(comparison.market_importance)}
                      </div>
                      <span className="text-xs text-gray-600 mt-1">
                        {comparison.market_importance}/10
                      </span>
                    </td>

                    {/* Gap Severity */}
                    <td className="py-4 px-4 text-center">
                      <span className={`font-medium capitalize ${getGapSeverityColor(comparison.gap_severity)}`}>
                        {comparison.gap_severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Legend */}
        {comparisons.length > 0 && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Capability Legend</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="flex items-center space-x-2">
                <Star className="w-4 h-4 text-yellow-500" />
                <span>Superior</span>
              </div>
              <div className="flex items-center space-x-2">
                <Check className="w-4 h-4 text-green-500" />
                <span>Competitive</span>
              </div>
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-orange-500" />
                <span>Basic</span>
              </div>
              <div className="flex items-center space-x-2">
                <X className="w-4 h-4 text-red-500" />
                <span>Missing</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeatureComparison; 