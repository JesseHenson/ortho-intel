import React, { useState } from 'react';
import { useStreamingAnalysis } from '../hooks/useStreamingAnalysis';

const CachedStreamingTest: React.FC = () => {
  const [analysisId, setAnalysisId] = useState('cached_test_' + Date.now());
  const [competitors, setCompetitors] = useState(['Stryker Spine', 'Zimmer Biomet']);
  const [focusArea, setFocusArea] = useState('spine_fusion');
  
  const {
    isConnected,
    isRunning,
    events,
    progress,
    currentMessage,
    error,
    cacheStatus,
    costSaved,
    researchEnabled,
    connectToCachedStream,
    connectToLangGraphStream,
    toggleResearch,
    disconnect
  } = useStreamingAnalysis(analysisId, false, true); // Default research to true

  const handleCachedStreamTest = () => {
    console.log('🧪 Starting cached stream test with research:', researchEnabled);
    connectToCachedStream(analysisId, competitors, focusArea);
  };

  const handleLiveStreamTest = () => {
    console.log('🔄 Starting live stream test with research:', researchEnabled);
    connectToLangGraphStream(analysisId, researchEnabled);
  };

  const handleStop = () => {
    disconnect();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'hit': return 'text-green-600';
      case 'miss': return 'text-orange-600';
      case 'live': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getEventTypeColor = (eventType: string) => {
    switch (eventType) {
      case 'connected': return 'border-l-green-500 bg-green-50';
      case 'cache_hit': return 'border-l-green-500 bg-green-50';
      case 'cache_miss': 
      case 'cache_miss_redirect': return 'border-l-orange-500 bg-orange-50';
      case 'analysis_started': return 'border-l-blue-500 bg-blue-50';
      case 'analysis_completed':
      case 'streaming_complete': return 'border-l-green-500 bg-green-50';
      case 'error': return 'border-l-red-500 bg-red-50';
      default: return 'border-l-gray-500 bg-gray-50';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎯 Cached Streaming Test with Research Controls
        </h1>
        <p className="text-gray-600">
          Test cached streaming functionality with research toggle
        </p>
      </div>

      {/* Configuration Panel */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Configuration</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Analysis ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Analysis ID
            </label>
            <input
              type="text"
              value={analysisId}
              onChange={(e) => setAnalysisId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isRunning}
            />
          </div>

          {/* Focus Area */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Focus Area
            </label>
            <input
              type="text"
              value={focusArea}
              onChange={(e) => setFocusArea(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isRunning}
            />
          </div>
        </div>

        {/* Competitors */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Competitors (comma-separated)
          </label>
          <input
            type="text"
            value={competitors.join(', ')}
            onChange={(e) => setCompetitors(e.target.value.split(',').map(c => c.trim()))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isRunning}
          />
        </div>

        {/* Research Toggle */}
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-blue-900">
                🔬 Research Mode
              </h3>
              <p className="text-sm text-blue-700 mt-1">
                {researchEnabled 
                  ? 'Enhanced analysis with research-backed insights (recommended)' 
                  : 'Basic analysis without external research'}
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`text-sm font-medium ${researchEnabled ? 'text-blue-600' : 'text-gray-500'}`}>
                {researchEnabled ? 'ON' : 'OFF'}
              </span>
              <button
                onClick={toggleResearch}
                disabled={isRunning}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  researchEnabled ? 'bg-blue-600' : 'bg-gray-200'
                } ${isRunning ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    researchEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Controls</h2>
        
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleCachedStreamTest}
            disabled={isRunning}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🎯 Test Cached Streaming
          </button>
          
          <button
            onClick={handleLiveStreamTest}
            disabled={isRunning}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🔄 Test Live Streaming
          </button>
          
          <button
            onClick={handleStop}
            disabled={!isRunning}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ⏹️ Stop
          </button>
        </div>
      </div>

      {/* Status */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Status</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className={`w-3 h-3 rounded-full mx-auto mb-1 ${
              isConnected ? 'bg-green-500' : 'bg-gray-400'
            }`}></div>
            <div className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
          
          <div className="text-center">
            <div className={`w-3 h-3 rounded-full mx-auto mb-1 ${
              isRunning ? 'bg-blue-500 animate-pulse' : 'bg-gray-400'
            }`}></div>
            <div className="text-sm text-gray-600">
              {isRunning ? 'Running' : 'Idle'}
            </div>
          </div>
          
          <div className="text-center">
            <div className={`text-lg font-semibold ${getStatusColor(cacheStatus)}`}>
              {cacheStatus.toUpperCase()}
            </div>
            <div className="text-sm text-gray-600">Cache Status</div>
          </div>
          
          <div className="text-center">
            <div className="text-lg font-semibold text-green-600">
              ${costSaved.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">Cost Saved</div>
          </div>
        </div>

        {progress > 0 && (
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {currentMessage && (
          <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
            <div className="text-sm text-blue-700">{currentMessage}</div>
          </div>
        )}

        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
            <div className="text-sm text-red-700">{error}</div>
          </div>
        )}
      </div>

      {/* Events */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Streaming Events ({events.length})
        </h2>
        
        {events.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No events yet. Click a test button to begin.
          </div>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {events.map((event, index) => (
              <div
                key={index}
                className={`border-l-4 p-3 rounded-r-lg ${getEventTypeColor(event.type)}`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">
                        {event.type}
                      </span>
                      {event.progress !== undefined && (
                        <span className="text-sm text-gray-600">
                          {event.progress}%
                        </span>
                      )}
                      {event.cost_saved && (
                        <span className="text-sm text-green-600 font-medium">
                          💰 ${event.cost_saved}
                        </span>
                      )}
                    </div>
                    
                    {event.message && (
                      <p className="text-gray-700 mt-1 text-sm">
                        {event.message}
                      </p>
                    )}
                    
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(event.timestamp).toLocaleTimeString()}
                      {event.event_id && ` • Event #${event.event_id}`}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CachedStreamingTest; 