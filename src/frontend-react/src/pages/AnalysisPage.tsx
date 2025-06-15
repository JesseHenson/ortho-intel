import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { 
  Plus, 
  X, 
  Play, 
  Building2, 
  Target,
  Briefcase
} from 'lucide-react';

import { startAnalysis } from '../lib/api';
import type { CompetitorAnalysisRequest } from '../lib/api';
import LoadingSpinner from '../components/LoadingSpinner';

// Must match backend COMPETITOR_SEPARATOR and FA_SEPARATOR
const COMPETITOR_SEPARATOR = '|||';
const FA_SEPARATOR = '__FA__';

// Helper function to generate analysis ID
const generateAnalysisId = (competitors: string[], focusArea: string): string => {
  const competitorStr = competitors.map(c => c.replace(/\s+/g, '_')).join(COMPETITOR_SEPARATOR).toLowerCase();
  const focusStr = focusArea.toLowerCase().replace(/\s+/g, '-');
  const timestamp = Date.now().toString().slice(-6);
  return `${competitorStr}${FA_SEPARATOR}${focusStr}_${timestamp}`;
};

const AnalysisPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<CompetitorAnalysisRequest>({
    competitors: [],
    focus_area: '',
    analysis_type: 'comprehensive',
    client_name: '',
    research_enabled: true, // Default research to enabled
  });
  const [currentCompetitor, setCurrentCompetitor] = useState('');

  // Predefined options
  const focusAreas = [
    'Spine Fusion',
    'Hip Reconstruction', 
    'Knee Reconstruction',
    'Trauma Fixation',
    'Sports Medicine',
    'Orthobiologics',
    'Surgical Robotics',
    'Digital Surgery',
    'General Orthopedics'
  ];

  const suggestedCompetitors = [
    'Stryker Spine',
    'Medtronic Spine',
    'DePuy Synthes',
    'Zimmer Biomet',
    'Orthofix',
    'NuVasive',
    'SeaSpine',
    'Globus Medical',
    'K2M (Stryker)',
    'Bioventus'
  ];

  // Start analysis mutation
  const startAnalysisMutation = useMutation({
    mutationFn: startAnalysis,
    onSuccess: (data: { analysis_id: string }) => {
      navigate(`/results/${data.analysis_id}`);
    },
    onError: (error) => {
      console.error('Failed to start analysis:', error);
    },
  });

  const addCompetitor = (competitor: string) => {
    if (competitor && !formData.competitors.includes(competitor)) {
      setFormData((prev: CompetitorAnalysisRequest) => ({
        ...prev,
        competitors: [...prev.competitors, competitor]
      }));
      setCurrentCompetitor('');
    }
  };

  const removeCompetitor = (competitor: string) => {
    setFormData((prev: CompetitorAnalysisRequest) => ({
      ...prev,
      competitors: prev.competitors.filter((c: string) => c !== competitor)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.competitors.length > 0 && formData.focus_area) {
      // Generate analysis ID for streaming
      const analysisId = generateAnalysisId(formData.competitors, formData.focus_area);
      
      // Navigate to results page immediately with the analysis ID and research setting
      navigate(`/results/${analysisId}`, { 
        state: { 
          competitors: formData.competitors, 
          focusArea: formData.focus_area,
          researchEnabled: formData.research_enabled,  // Pass research setting
          startAnalysis: true
        }
      });
    }
  };

  const isValid = formData.competitors.length > 0 && formData.focus_area.length > 0;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          New Competitive Analysis
        </h1>
        <p className="text-lg text-gray-600">
          Configure your analysis parameters to identify strategic opportunities
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Competitors Section */}
        <div className="bg-white rounded-lg shadow-card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Building2 className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Select Competitors
            </h2>
          </div>
          
          <p className="text-gray-600 mb-6">
            Choose up to 5 competitors to analyze. You can select from suggestions or add custom competitors.
          </p>

          {/* Current Competitors */}
          {formData.competitors.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Selected Competitors:</h3>
              <div className="flex flex-wrap gap-2">
                {formData.competitors.map((competitor: string) => (
                  <div
                    key={competitor}
                    className="flex items-center space-x-2 bg-primary-100 text-primary-800 px-3 py-1 rounded-full"
                  >
                    <span className="text-sm font-medium">{competitor}</span>
                    <button
                      type="button"
                      onClick={() => removeCompetitor(competitor)}
                      className="p-1 hover:bg-primary-200 rounded-full transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Add Competitor */}
          <div className="space-y-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={currentCompetitor}
                onChange={(e) => setCurrentCompetitor(e.target.value)}
                placeholder="Enter competitor name..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCompetitor(currentCompetitor))}
              />
              <button
                type="button"
                onClick={() => addCompetitor(currentCompetitor)}
                disabled={!currentCompetitor || formData.competitors.length >= 5}
                className="btn-primary flex items-center space-x-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus className="w-4 h-4" />
                <span>Add</span>
              </button>
            </div>

            {/* Suggested Competitors */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Suggested Competitors:</h3>
              <div className="flex flex-wrap gap-2">
                {suggestedCompetitors
                  .filter(comp => !formData.competitors.includes(comp))
                  .slice(0, 8)
                  .map((competitor) => (
                    <button
                      key={competitor}
                      type="button"
                      onClick={() => addCompetitor(competitor)}
                      disabled={formData.competitors.length >= 5}
                      className="text-sm px-3 py-1 border border-gray-300 rounded-full hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {competitor}
                    </button>
                  ))}
              </div>
            </div>
          </div>

          {formData.competitors.length >= 5 && (
            <p className="text-sm text-strategic-600 mt-2">
              Maximum of 5 competitors allowed
            </p>
          )}
        </div>

        {/* Focus Area Section */}
        <div className="bg-white rounded-lg shadow-card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Target className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Focus Area
            </h2>
          </div>

          <p className="text-gray-600 mb-6">
            Select the market segment or product category for your analysis.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {focusAreas.map((area) => (
              <button
                key={area}
                type="button"
                onClick={() => setFormData((prev: CompetitorAnalysisRequest) => ({ ...prev, focus_area: area }))}
                className={`p-3 text-left border-2 rounded-lg transition-all ${
                  formData.focus_area === area
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <span className="font-medium">{area}</span>
              </button>
            ))}
          </div>

          {/* Custom Focus Area */}
          <div className="mt-4">
            <input
              type="text"
              placeholder="Or enter custom focus area..."
              value={!focusAreas.includes(formData.focus_area) ? formData.focus_area : ''}
              onChange={(e) => setFormData((prev: CompetitorAnalysisRequest) => ({ ...prev, focus_area: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        {/* Optional Settings */}
        <div className="bg-white rounded-lg shadow-card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Briefcase className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Optional Settings
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client Name (Optional)
              </label>
              <input
                type="text"
                value={formData.client_name}
                onChange={(e) => setFormData((prev: CompetitorAnalysisRequest) => ({ ...prev, client_name: e.target.value }))}
                placeholder="Enter client or project name..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Analysis Type
              </label>
              <select
                value={formData.analysis_type}
                onChange={(e) => setFormData((prev: CompetitorAnalysisRequest) => ({ ...prev, analysis_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="comprehensive">Comprehensive Analysis</option>
                <option value="quick">Quick Overview</option>
                <option value="deep-dive">Deep Dive</option>
              </select>
            </div>
          </div>

          {/* Research Toggle */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-blue-900">
                  🔬 Research Mode
                </h3>
                <p className="text-sm text-blue-700 mt-1">
                  {formData.research_enabled 
                    ? 'Enhanced analysis with research-backed insights (recommended)' 
                    : 'Basic analysis without external research - faster but less comprehensive'}
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`text-sm font-medium ${formData.research_enabled ? 'text-blue-600' : 'text-gray-500'}`}>
                  {formData.research_enabled ? 'ON' : 'OFF'}
                </span>
                <button
                  type="button"
                  onClick={() => setFormData((prev: CompetitorAnalysisRequest) => ({ 
                    ...prev, 
                    research_enabled: !prev.research_enabled 
                  }))}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    formData.research_enabled ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      formData.research_enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex items-center justify-between bg-white rounded-lg shadow-card p-6">
          <div>
            <h3 className="font-medium text-gray-900">Ready to Start Analysis</h3>
            <p className="text-sm text-gray-600">
              {formData.competitors.length > 0 
                ? `Analyzing ${formData.competitors.length} competitor(s) in ${formData.focus_area || 'selected focus area'}`
                : 'Please select competitors and focus area to continue'
              }
            </p>
          </div>

          <button
            type="submit"
            disabled={!isValid || startAnalysisMutation.isPending}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {startAnalysisMutation.isPending ? (
              <>
                <LoadingSpinner size="sm" />
                <span>Starting Analysis...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Start Analysis</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Error Display */}
      {startAnalysisMutation.error && (
        <div className="bg-risk-50 border border-risk-200 rounded-lg p-4">
          <p className="text-risk-800">
            Failed to start analysis: {startAnalysisMutation.error.message}
          </p>
        </div>
      )}
    </div>
  );
};

export default AnalysisPage; 