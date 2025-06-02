import { useState } from 'react';
import { 
  Search, 
  Building2, 
  MapPin, 
  TrendingUp, 
  Calendar,
  ExternalLink,
  Target,
  ChevronRight,
  Filter
} from 'lucide-react';

// Mock data for competitor profiles
const competitorProfiles = [
  {
    id: 1,
    name: "Stryker Spine",
    category: "Major Player",
    headquarters: "Kalamazoo, MI, USA",
    employees: "46,000+",
    revenue: "$17.1B (2023)",
    founded: "1941",
    logo: "🏥",
    description: "Leading medical technology company specializing in orthopedics, medical and surgical, and neurotechnology and spine products.",
    strengths: [
      "Strong R&D pipeline",
      "Global market presence", 
      "Innovative surgical robotics",
      "Comprehensive spine portfolio"
    ],
    weaknesses: [
      "Premium pricing strategy",
      "Complex product integration",
      "Regulatory compliance challenges"
    ],
    marketShare: "18.5%",
    recentDevelopments: [
      "Launched new minimally invasive spine system",
      "Acquired robotics company for $2.1B",
      "FDA approval for new cervical fusion device"
    ],
    competitiveAdvantages: [
      "Advanced surgical robotics",
      "Strong surgeon relationships",
      "Extensive clinical data"
    ],
    threats: [
      "Increasing price pressure",
      "New market entrants",
      "Regulatory changes"
    ],
    focusAreas: ["Spine Fusion", "Surgical Robotics", "Orthobiologics"],
    rating: 4.8
  },
  {
    id: 2,
    name: "Medtronic Spine",
    category: "Major Player",
    headquarters: "Dublin, Ireland",
    employees: "95,000+",
    revenue: "$31.7B (2023)",
    founded: "1949",
    logo: "🔬",
    description: "Global healthcare technology leader providing medical device solutions across multiple therapeutic areas including spine and biologics.",
    strengths: [
      "Largest medical device company",
      "Strong clinical evidence",
      "Global distribution network",
      "Comprehensive spine ecosystem"
    ],
    weaknesses: [
      "Slower innovation cycles",
      "Complex organizational structure",
      "Integration challenges"
    ],
    marketShare: "22.1%",
    recentDevelopments: [
      "Expanded AI-powered surgical planning",
      "New biologics manufacturing facility",
      "Partnership with leading spine surgeons"
    ],
    competitiveAdvantages: [
      "Market leadership position",
      "Comprehensive product portfolio",
      "Strong regulatory expertise"
    ],
    threats: [
      "Commoditization pressure",
      "Emerging competitors",
      "Healthcare cost reduction"
    ],
    focusAreas: ["Spine Fusion", "Orthobiologics", "Digital Surgery"],
    rating: 4.6
  },
  {
    id: 3,
    name: "NuVasive",
    category: "Specialist",
    headquarters: "San Diego, CA, USA",
    employees: "2,700+",
    revenue: "$1.14B (2023)", 
    founded: "1997",
    logo: "⚡",
    description: "Spine technology company focused on transforming spine surgery through innovative, procedurally-integrated solutions.",
    strengths: [
      "Minimally invasive focus",
      "Strong surgeon advocacy",
      "Innovation in lateral access",
      "Integrated technology platform"
    ],
    weaknesses: [
      "Limited product diversification",
      "Smaller scale than major players",
      "Dependence on spine market"
    ],
    marketShare: "8.3%",
    recentDevelopments: [
      "Launched new AI-powered surgical platform",
      "Expanded international presence",
      "New minimally invasive solutions"
    ],
    competitiveAdvantages: [
      "Minimally invasive expertise",
      "Strong surgeon relationships",
      "Technology integration"
    ],
    threats: [
      "Major player competition",
      "Market consolidation",
      "Reimbursement pressures"
    ],
    focusAreas: ["Spine Fusion", "Minimally Invasive Surgery"],
    rating: 4.4
  },
  {
    id: 4,
    name: "Zimmer Biomet",
    category: "Major Player", 
    headquarters: "Warsaw, IN, USA",
    employees: "27,000+",
    revenue: "$7.0B (2023)",
    founded: "1927",
    logo: "🦴",
    description: "Global leader in musculoskeletal healthcare with a comprehensive portfolio of solutions for spine, hip, knee, and trauma.",
    strengths: [
      "Comprehensive musculoskeletal portfolio",
      "Strong brand recognition",
      "Global manufacturing footprint",
      "Digital health initiatives"
    ],
    weaknesses: [
      "Integration challenges from mergers", 
      "Quality control issues",
      "Slower growth in spine"
    ],
    marketShare: "12.7%",
    recentDevelopments: [
      "Digital health platform expansion",
      "New spine biologics portfolio",
      "Robotic surgery partnerships"
    ],
    competitiveAdvantages: [
      "Broad product portfolio",
      "Established market presence",
      "Strong distribution network"
    ],
    threats: [
      "Commodity pricing pressure",
      "Regulatory scrutiny",
      "Competition from specialists"
    ],
    focusAreas: ["Spine Fusion", "Hip Reconstruction", "Knee Reconstruction"],
    rating: 4.2
  }
];

const CompetitorFinderPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedFocusArea, setSelectedFocusArea] = useState('All');
  const [selectedCompetitor, setSelectedCompetitor] = useState<any>(null);

  const categories = ['All', 'Major Player', 'Specialist', 'Emerging', 'Regional'];
  const focusAreas = ['All', 'Spine Fusion', 'Hip Reconstruction', 'Knee Reconstruction', 'Surgical Robotics', 'Orthobiologics'];

  // Filter competitors based on search and filters
  const filteredCompetitors = competitorProfiles.filter(competitor => {
    const matchesSearch = competitor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         competitor.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || competitor.category === selectedCategory;
    const matchesFocusArea = selectedFocusArea === 'All' || 
                           competitor.focusAreas.some(area => area === selectedFocusArea);
    
    return matchesSearch && matchesCategory && matchesFocusArea;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🏢 Competitor Intelligence Center
        </h1>
        <p className="text-lg text-gray-600">
          Discover, analyze, and track competitors in the orthopedic device market
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Panel - Search and Filters + Competitor List */}
        <div className="lg:col-span-2 space-y-6">
          {/* Search and Filters */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Search className="w-5 h-5 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">
                Find Competitors
              </h2>
            </div>

            <div className="space-y-4">
              {/* Search Bar */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search competitors by name, technology, or focus area..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              {/* Filters */}
              <div className="flex flex-wrap gap-4">
                <div className="flex items-center space-x-2">
                  <Filter className="w-4 h-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">Filters:</span>
                </div>
                
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>

                <select
                  value={selectedFocusArea}
                  onChange={(e) => setSelectedFocusArea(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
                >
                  {focusAreas.map(area => (
                    <option key={area} value={area}>{area}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Competitor Grid */}
          <div className="space-y-4">
            {filteredCompetitors.map((competitor) => (
              <div
                key={competitor.id}
                className={`bg-white rounded-lg border-2 transition-all cursor-pointer hover:shadow-md ${
                  selectedCompetitor?.id === competitor.id 
                    ? 'border-primary-500 shadow-lg' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedCompetitor(competitor)}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="text-3xl">{competitor.logo}</div>
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
                          <span>{competitor.name}</span>
                          <span className="text-yellow-500">
                            {'★'.repeat(Math.floor(competitor.rating))}
                          </span>
                        </h3>
                        <div className="flex items-center space-x-3 text-sm text-gray-600">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            competitor.category === 'Major Player' ? 'bg-blue-100 text-blue-800' :
                            competitor.category === 'Specialist' ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {competitor.category}
                          </span>
                          <span className="flex items-center space-x-1">
                            <MapPin className="w-3 h-3" />
                            <span>{competitor.headquarters}</span>
                          </span>
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </div>

                  <p className="text-gray-700 mb-4 line-clamp-2">
                    {competitor.description}
                  </p>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <span className="text-xs text-gray-600">Revenue</span>
                      <p className="font-semibold">{competitor.revenue}</p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-600">Market Share</span>
                      <p className="font-semibold">{competitor.marketShare}</p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-600">Employees</span>
                      <p className="font-semibold">{competitor.employees}</p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-600">Founded</span>
                      <p className="font-semibold">{competitor.founded}</p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {competitor.focusAreas.slice(0, 3).map((area, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-amber-100 text-amber-800 text-xs rounded-full"
                      >
                        {area}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel - Detailed Profile */}
        <div className="lg:col-span-1">
          {selectedCompetitor ? (
            <div className="bg-white rounded-lg shadow-card p-6 sticky top-8">
              <div className="text-center mb-6">
                <div className="text-4xl mb-2">{selectedCompetitor.logo}</div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedCompetitor.name}</h2>
                <p className="text-gray-600">{selectedCompetitor.category}</p>
              </div>

              <div className="space-y-6">
                {/* Company Overview */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <Building2 className="w-4 h-4 mr-2" />
                    Company Overview
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Headquarters:</span>
                      <span className="font-medium">{selectedCompetitor.headquarters}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Founded:</span>
                      <span className="font-medium">{selectedCompetitor.founded}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Employees:</span>
                      <span className="font-medium">{selectedCompetitor.employees}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Revenue:</span>
                      <span className="font-medium">{selectedCompetitor.revenue}</span>
                    </div>
                  </div>
                </div>

                {/* Strengths */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-2 text-green-600" />
                    Key Strengths
                  </h3>
                  <ul className="space-y-1">
                    {selectedCompetitor.strengths.map((strength: string, index: number) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="text-green-500 mr-2">•</span>
                        {strength}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Weaknesses */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <Target className="w-4 h-4 mr-2 text-red-600" />
                    Potential Weaknesses
                  </h3>
                  <ul className="space-y-1">
                    {selectedCompetitor.weaknesses.map((weakness: string, index: number) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="text-red-500 mr-2">•</span>
                        {weakness}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Recent Developments */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <Calendar className="w-4 h-4 mr-2 text-blue-600" />
                    Recent Developments
                  </h3>
                  <ul className="space-y-2">
                    {selectedCompetitor.recentDevelopments.map((development: string, index: number) => (
                      <li key={index} className="text-sm text-gray-700 p-2 bg-blue-50 rounded">
                        {development}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Focus Areas */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Focus Areas</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedCompetitor.focusAreas.map((area: string, index: number) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full"
                      >
                        {area}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="space-y-2 pt-4 border-t">
                  <button className="w-full btn-primary text-sm">
                    📊 Start Competitive Analysis
                  </button>
                  <button className="w-full btn-outline text-sm">
                    📋 View Full Report
                  </button>
                  <button className="w-full btn-outline text-sm flex items-center justify-center space-x-1">
                    <ExternalLink className="w-3 h-3" />
                    <span>Visit Website</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-card p-6 text-center">
              <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Select a Competitor
              </h3>
              <p className="text-gray-600">
                Click on any competitor from the list to view detailed intelligence and analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompetitorFinderPage; 