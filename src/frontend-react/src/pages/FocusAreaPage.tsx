import { useState } from 'react';
import { 
  Target, 
  TrendingUp, 
  DollarSign, 
  Users, 
  BarChart3,
  Calendar,
  AlertTriangle,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  Minus,
  Building2,
  Award,
  Lightbulb
} from 'lucide-react';

// Mock data for focus areas
const focusAreaData = {
  'Spine Fusion': {
    id: 'spine-fusion',
    icon: '🦴',
    marketSize: '$15.2B',
    growthRate: '+7.3%',
    marketSizeDetail: '$15.2B (2023)',
    projectedSize: '$21.8B by 2028',
    description: 'Spinal fusion involves permanently connecting two or more vertebrae in the spine, eliminating motion between them.',
    keyMetrics: {
      marketShare: '42%',
      averagePrice: '$45,000',
      procedureVolume: '450,000/year',
      approvalTime: '18-24 months'
    },
    marketTrends: [
      {
        trend: 'Minimally Invasive Techniques',
        impact: 'high',
        direction: 'up',
        description: 'Growing adoption of MIS-TLIF and lateral approaches reducing recovery time'
      },
      {
        trend: 'Biologics Integration',
        impact: 'high', 
        direction: 'up',
        description: 'Increased use of bone grafts and growth factors improving fusion rates'
      },
      {
        trend: 'Robotic Surgery Adoption',
        impact: 'medium',
        direction: 'up',
        description: 'Enhanced precision and reduced radiation exposure driving adoption'
      },
      {
        trend: 'Cost Pressure',
        impact: 'medium',
        direction: 'down',
        description: 'Healthcare cost reduction initiatives affecting pricing strategies'
      }
    ],
    keyPlayers: [
      { name: 'Medtronic', share: '22%', trend: 'stable' },
      { name: 'Stryker', share: '19%', trend: 'up' },
      { name: 'DePuy Synthes', share: '16%', trend: 'down' },
      { name: 'NuVasive', share: '8%', trend: 'up' },
      { name: 'Zimmer Biomet', share: '7%', trend: 'stable' }
    ],
    opportunities: [
      {
        title: 'Enhanced Biologics for Cervical Fusion',
        description: 'Development of safer biologics addressing rhBMP complications',
        marketPotential: '$2.1B',
        timeframe: '12-18 months',
        difficulty: 'Medium'
      },
      {
        title: 'AI-Powered Surgical Planning',
        description: 'Integration of machine learning for optimal implant selection',
        marketPotential: '$800M',
        timeframe: '18-24 months', 
        difficulty: 'High'
      },
      {
        title: 'Biodegradable Fusion Cages',
        description: 'Next-generation materials eliminating need for revision surgeries',
        marketPotential: '$1.5B',
        timeframe: '24-36 months',
        difficulty: 'High'
      }
    ],
    challenges: [
      'FDA regulatory complexity for biologics',
      'Surgeon training requirements for new technologies',
      'Hospital budget constraints and reimbursement pressures',
      'Competition from non-fusion alternatives'
    ],
    regulatoryLandscape: {
      recentApprovals: [
        'FDA approval for ViviGen bone graft (2023)',
        'CE mark for XLIF expandable cage (2023)'
      ],
      upcomingRegulations: [
        'Enhanced biologics safety requirements (2024)',
        'Digital surgery device guidelines (2024)'
      ]
    }
  },
  'Hip Reconstruction': {
    id: 'hip-reconstruction',
    icon: '🦵',
    marketSize: '$7.8B',
    growthRate: '+5.2%',
    marketSizeDetail: '$7.8B (2023)',
    projectedSize: '$10.1B by 2028',
    description: 'Hip reconstruction involves replacing damaged hip joints with artificial implants to restore mobility and reduce pain.',
    keyMetrics: {
      marketShare: '28%',
      averagePrice: '$15,000',
      procedureVolume: '520,000/year',
      approvalTime: '12-18 months'
    },
    marketTrends: [
      {
        trend: 'Robotic-Assisted Surgery',
        impact: 'high',
        direction: 'up',
        description: 'Growing adoption of Mako and ROSA systems improving precision'
      },
      {
        trend: 'Ceramic-on-Ceramic Bearings',
        impact: 'medium',
        direction: 'up',
        description: 'Enhanced durability and reduced wear rates extending implant life'
      },
      {
        trend: 'Outpatient Hip Replacement',
        impact: 'high',
        direction: 'up',
        description: 'Same-day discharge protocols reducing costs and improving satisfaction'
      },
      {
        trend: 'Revision Surgery Complexity',
        impact: 'medium',
        direction: 'down',
        description: 'Increasing complexity of revision cases requiring specialized solutions'
      }
    ],
    keyPlayers: [
      { name: 'Stryker', share: '32%', trend: 'up' },
      { name: 'Zimmer Biomet', share: '28%', trend: 'stable' },
      { name: 'DePuy Synthes', share: '22%', trend: 'down' },
      { name: 'Smith & Nephew', share: '10%', trend: 'up' },
      { name: 'MicroPort', share: '4%', trend: 'up' }
    ],
    opportunities: [
      {
        title: 'Smart Implants with Sensors',
        description: 'IoT-enabled implants providing real-time monitoring',
        marketPotential: '$1.2B',
        timeframe: '24-36 months',
        difficulty: 'High'
      },
      {
        title: 'Personalized 3D-Printed Implants',
        description: 'Patient-specific implants improving fit and outcomes',
        marketPotential: '$900M',
        timeframe: '18-24 months',
        difficulty: 'Medium'
      }
    ],
    challenges: [
      'Aging population increasing revision burden',
      'Younger patient expectations for longevity',
      'Cost pressures from value-based care',
      'Surgeon preference and training requirements'
    ],
    regulatoryLandscape: {
      recentApprovals: [
        'FDA clearance for MAKO Hip 2.0 (2023)',
        'CE mark for ceramic femoral heads (2023)'
      ],
      upcomingRegulations: [
        'Enhanced post-market surveillance (2024)',
        'Digital health device integration (2024)'
      ]
    }
  },
  'Knee Reconstruction': {
    id: 'knee-reconstruction', 
    icon: '🦴',
    marketSize: '$9.1B',
    growthRate: '+6.1%',
    marketSizeDetail: '$9.1B (2023)',
    projectedSize: '$12.4B by 2028',
    description: 'Knee reconstruction replaces damaged knee joints to restore function and alleviate pain from arthritis or injury.',
    keyMetrics: {
      marketShare: '32%',
      averagePrice: '$18,000',
      procedureVolume: '790,000/year',
      approvalTime: '15-20 months'
    },
    marketTrends: [
      {
        trend: 'Partial Knee Replacement Growth',
        impact: 'high',
        direction: 'up',
        description: 'Unicompartmental knees gaining acceptance for younger patients'
      },
      {
        trend: 'Robotic Surgery Adoption',
        impact: 'high',
        direction: 'up',
        description: 'Mako and NAVIO systems improving alignment and outcomes'
      },
      {
        trend: 'Enhanced Recovery Protocols',
        impact: 'medium',
        direction: 'up',
        description: 'Rapid recovery pathways reducing length of stay'
      }
    ],
    keyPlayers: [
      { name: 'Zimmer Biomet', share: '25%', trend: 'stable' },
      { name: 'Stryker', share: '23%', trend: 'up' },
      { name: 'DePuy Synthes', share: '20%', trend: 'down' },
      { name: 'Smith & Nephew', share: '15%', trend: 'up' },
      { name: 'MicroPort', share: '8%', trend: 'up' }
    ],
    opportunities: [
      {
        title: 'Kinematic Alignment Technology',
        description: 'Advanced alignment techniques preserving natural knee kinematics',
        marketPotential: '$1.8B',
        timeframe: '12-18 months',
        difficulty: 'Medium'
      }
    ],
    challenges: [
      'Balancing cost and innovation',
      'Surgeon training for new techniques',
      'Patient satisfaction metrics pressure'
    ],
    regulatoryLandscape: {
      recentApprovals: [
        'FDA clearance for ROSA Knee 3.0 (2023)'
      ],
      upcomingRegulations: [
        'Patient-specific implant guidelines (2024)'
      ]
    }
  }
};

const FocusAreaPage = () => {
  const [selectedFocusArea, setSelectedFocusArea] = useState<string>('Spine Fusion');
  
  const focusAreas = Object.keys(focusAreaData);
  const currentData = focusAreaData[selectedFocusArea as keyof typeof focusAreaData];

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'up': return <ArrowUp className="w-4 h-4 text-green-600" />;
      case 'down': return <ArrowDown className="w-4 h-4 text-red-600" />;
      default: return <Minus className="w-4 h-4 text-gray-600" />;
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'up': return 'text-green-700 bg-green-100';
      case 'down': return 'text-red-700 bg-red-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-green-100 text-green-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎯 Focus Area Industry Analysis
        </h1>
        <p className="text-lg text-gray-600">
          Deep market intelligence and competitive landscape analysis by therapeutic area
        </p>
      </div>

      {/* Focus Area Selector */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Target className="w-5 h-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">Select Focus Area</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {focusAreas.map((area) => (
            <button
              key={area}
              onClick={() => setSelectedFocusArea(area)}
              className={`p-4 text-left border-2 rounded-lg transition-all hover:shadow-md ${
                selectedFocusArea === area
                  ? 'border-primary-500 bg-primary-50 shadow-md'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-3xl">{focusAreaData[area as keyof typeof focusAreaData].icon}</span>
                <div>
                  <h3 className="font-semibold text-gray-900">{area}</h3>
                  <p className="text-sm text-gray-600">
                    {focusAreaData[area as keyof typeof focusAreaData].marketSize} • {focusAreaData[area as keyof typeof focusAreaData].growthRate}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Focus Area Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content - Left Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Market Overview */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
                  <span className="text-3xl">{currentData.icon}</span>
                  <span>{selectedFocusArea}</span>
                </h2>
                <p className="text-gray-600 mt-2">{currentData.description}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                <DollarSign className="w-6 h-6 text-blue-600 mb-2" />
                <div className="text-2xl font-bold text-blue-900">{currentData.marketSize}</div>
                <div className="text-sm text-blue-600">Market Size</div>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                <TrendingUp className="w-6 h-6 text-green-600 mb-2" />
                <div className="text-2xl font-bold text-green-900">{currentData.growthRate}</div>
                <div className="text-sm text-green-600">Growth Rate</div>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                <Users className="w-6 h-6 text-purple-600 mb-2" />
                <div className="text-2xl font-bold text-purple-900">{currentData.keyMetrics.procedureVolume}</div>
                <div className="text-sm text-purple-600">Annual Procedures</div>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
                <Calendar className="w-6 h-6 text-orange-600 mb-2" />
                <div className="text-2xl font-bold text-orange-900">{currentData.keyMetrics.approvalTime}</div>
                <div className="text-sm text-orange-600">Avg. Approval Time</div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">Market Projection</h3>
              <p className="text-gray-700">
                Current market size of <strong>{currentData.marketSizeDetail}</strong> projected to reach{' '}
                <strong>{currentData.projectedSize}</strong> with a compound annual growth rate of{' '}
                <strong>{currentData.growthRate}</strong>.
              </p>
            </div>
          </div>

          {/* Market Trends */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2 text-primary-600" />
              Market Trends & Drivers
            </h3>
            
            <div className="space-y-4">
              {currentData.marketTrends.map((trend, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-medium text-gray-900">{trend.trend}</h4>
                        <div className="flex items-center space-x-2">
                          {getTrendIcon(trend.direction)}
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(trend.impact)}`}>
                            {trend.impact} impact
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600">{trend.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Strategic Opportunities */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
              Strategic Opportunities
            </h3>
            
            <div className="grid grid-cols-1 gap-4">
              {currentData.opportunities.map((opportunity, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow bg-gradient-to-r from-yellow-50 to-amber-50">
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="font-semibold text-gray-900 text-lg">{opportunity.title}</h4>
                    <span className="text-lg font-bold text-green-600">{opportunity.marketPotential}</span>
                  </div>
                  <p className="text-gray-700 mb-4">{opportunity.description}</p>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="flex items-center space-x-1">
                      <Calendar className="w-4 h-4 text-blue-600" />
                      <span className="text-gray-600">Timeline: {opportunity.timeframe}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Target className="w-4 h-4 text-purple-600" />
                      <span className="text-gray-600">Difficulty: {opportunity.difficulty}</span>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Challenges & Risks */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-red-600" />
              Market Challenges & Risks
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {currentData.challenges.map((challenge, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-red-800">{challenge}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Market Leaders */}
          <div className="bg-white rounded-lg shadow-card p-6 sticky top-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Building2 className="w-5 h-5 mr-2 text-gray-600" />
              Market Leaders
            </h3>
            
            <div className="space-y-3">
              {currentData.keyPlayers.map((player, index) => (
                <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </span>
                    <div>
                      <div className="font-medium text-gray-900">{player.name}</div>
                      <div className="text-sm text-gray-600">{player.share} market share</div>
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${getTrendColor(player.trend)}`}>
                    {getTrendIcon(player.trend)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Regulatory Landscape */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Award className="w-5 h-5 mr-2 text-green-600" />
              Regulatory Landscape
            </h3>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  Recent Approvals
                </h4>
                <ul className="space-y-1">
                  {currentData.regulatoryLandscape.recentApprovals.map((approval, index) => (
                    <li key={index} className="text-sm text-gray-600 bg-green-50 p-2 rounded">
                      {approval}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <Calendar className="w-4 h-4 mr-2 text-blue-600" />
                  Upcoming Regulations
                </h4>
                <ul className="space-y-1">
                  {currentData.regulatoryLandscape.upcomingRegulations.map((regulation, index) => (
                    <li key={index} className="text-sm text-gray-600 bg-blue-50 p-2 rounded">
                      {regulation}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full btn-primary text-sm">
                📊 Generate Market Report
              </button>
              <button className="w-full btn-outline text-sm">
                🔍 Competitive Analysis
              </button>
              <button className="w-full btn-outline text-sm">
                📈 Track Market Trends
              </button>
              <button className="w-full btn-outline text-sm">
                📧 Subscribe to Updates
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FocusAreaPage; 