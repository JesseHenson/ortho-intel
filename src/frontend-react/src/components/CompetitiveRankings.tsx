import React from 'react';
import { Trophy, Medal, Award, TrendingUp, BarChart3 } from 'lucide-react';
import type { CompetitiveRanking } from '../lib/api';

interface CompetitiveRankingsProps {
  rankings: CompetitiveRanking[];
  className?: string;
}

const CompetitiveRankings: React.FC<CompetitiveRankingsProps> = ({ rankings, className = '' }) => {
  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return <Trophy className="w-5 h-5 text-yellow-500" />;
      case 2: return <Medal className="w-5 h-5 text-gray-400" />;
      case 3: return <Award className="w-5 h-5 text-orange-500" />;
      default: return <div className="w-5 h-5 flex items-center justify-center bg-gray-200 rounded-full text-xs font-bold text-gray-600">{rank}</div>;
    }
  };

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1: return 'bg-yellow-50 border-yellow-200';
      case 2: return 'bg-gray-50 border-gray-200';
      case 3: return 'bg-orange-50 border-orange-200';
      default: return 'bg-white border-gray-200';
    }
  };

  const getScoreBarWidth = (score: number, maxScore: number) => {
    return Math.round((score / maxScore) * 100);
  };

  const getScoreColor = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    if (percentage >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Competitive Rankings</h3>
            <p className="text-sm text-gray-600">
              Performance rankings across key competitive dimensions
            </p>
          </div>
          <BarChart3 className="w-6 h-6 text-gray-400" />
        </div>

        {rankings.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">No Rankings Available</p>
            <p>Competitive rankings will appear here once analysis is complete.</p>
          </div>
        ) : (
          <div className="space-y-8">
            {rankings.map((ranking, categoryIndex) => {
              const maxScore = Math.max(...ranking.rankings.map(r => r.score));
              
              return (
                <div key={categoryIndex} className="border rounded-lg p-4">
                  <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2 text-blue-500" />
                    {ranking.category}
                  </h4>
                  
                  <div className="space-y-3">
                    {ranking.rankings
                      .sort((a, b) => a.rank - b.rank)
                      .map((competitor, index) => (
                        <div
                          key={index}
                          className={`flex items-center p-3 rounded-lg border ${getRankColor(competitor.rank)} transition-all hover:shadow-md`}
                        >
                          {/* Rank Icon */}
                          <div className="flex-shrink-0 mr-4">
                            {getRankIcon(competitor.rank)}
                          </div>

                          {/* Competitor Info */}
                          <div className="flex-grow min-w-0">
                            <div className="flex items-center justify-between mb-2">
                              <h5 className="font-medium text-gray-900 truncate">
                                {competitor.competitor_name}
                              </h5>
                              <div className="flex items-center space-x-2">
                                <span className="text-sm font-bold text-gray-900">
                                  {competitor.score}/{maxScore}
                                </span>
                                <span className="text-xs text-gray-500">
                                  #{competitor.rank}
                                </span>
                              </div>
                            </div>

                            {/* Score Bar */}
                            <div className="mb-2">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full transition-all duration-500 ${getScoreColor(competitor.score, maxScore)}`}
                                  style={{ width: `${getScoreBarWidth(competitor.score, maxScore)}%` }}
                                />
                              </div>
                            </div>

                            {/* Key Factors */}
                            {competitor.key_factors && competitor.key_factors.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {competitor.key_factors.slice(0, 3).map((factor, factorIndex) => (
                                  <span
                                    key={factorIndex}
                                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                                  >
                                    {factor}
                                  </span>
                                ))}
                                {competitor.key_factors.length > 3 && (
                                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                    +{competitor.key_factors.length - 3} more
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                  </div>

                  {/* Category Summary */}
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                      <div>
                        <p className="text-xs text-gray-600">Competitors</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {ranking.rankings.length}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Avg Score</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {(ranking.rankings.reduce((sum, r) => sum + r.score, 0) / ranking.rankings.length).toFixed(1)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Top Score</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {maxScore}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Leader</p>
                        <p className="text-lg font-semibold text-gray-900 truncate">
                          {ranking.rankings.find(r => r.rank === 1)?.competitor_name || 'N/A'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Overall Summary */}
        {rankings.length > 0 && (
          <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
            <h4 className="text-md font-medium text-gray-900 mb-3 flex items-center">
              <Trophy className="w-4 h-4 mr-2 text-blue-600" />
              Overall Performance Summary
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <p className="text-gray-600">Total Categories</p>
                <p className="text-xl font-bold text-blue-600">{rankings.length}</p>
              </div>
              <div className="text-center">
                <p className="text-gray-600">Competitors Analyzed</p>
                <p className="text-xl font-bold text-blue-600">
                  {[...new Set(rankings.flatMap(r => r.rankings.map(c => c.competitor_name)))].length}
                </p>
              </div>
              <div className="text-center">
                <p className="text-gray-600">Key Factors</p>
                <p className="text-xl font-bold text-blue-600">
                  {[...new Set(rankings.flatMap(r => r.rankings.flatMap(c => c.key_factors)))].length}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompetitiveRankings; 