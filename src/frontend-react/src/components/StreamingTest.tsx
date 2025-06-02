import React, { useState } from 'react';
import { useStreamingAnalysis } from '../hooks/useStreamingAnalysis';

const StreamingTest: React.FC = () => {
  const [analysisId, setAnalysisId] = useState('test-improved-streaming');
  const { 
    isConnected, 
    isRunning, 
    events, 
    progress, 
    currentMessage, 
    error, 
    connectToLangGraphStream,
    disconnect
  } = useStreamingAnalysis(null);

  const handleConnect = () => {
    // For testing, use LangGraph stream with sample data
    connectToLangGraphStream(analysisId);
  };

  const handleConnectLangGraph = () => {
    connectToLangGraphStream(analysisId);
  };

  const handleDisconnect = () => {
    disconnect();
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Improved Streaming Test</h2>
      
      {/* Controls */}
      <div className="mb-6 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Analysis ID:</label>
          <input
            type="text"
            value={analysisId}
            onChange={(e) => setAnalysisId(e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
            disabled={isRunning}
          />
        </div>
        
        <div className="flex space-x-4">
          <button
            onClick={handleConnect}
            disabled={isRunning}
            className="px-4 py-2 bg-blue-500 text-white rounded-md disabled:bg-gray-400"
          >
            {isRunning ? 'Streaming...' : 'Simple Stream'}
          </button>
          
          <button
            onClick={handleConnectLangGraph}
            disabled={isRunning}
            className="px-4 py-2 bg-green-500 text-white rounded-md disabled:bg-gray-400"
          >
            {isRunning ? 'Streaming...' : 'LangGraph Stream'}
          </button>
          
          <button
            onClick={handleDisconnect}
            disabled={!isRunning}
            className="px-4 py-2 bg-red-500 text-white rounded-md disabled:bg-gray-400"
          >
            Stop Stream
          </button>
        </div>
      </div>

      {/* Status */}
      <div className="mb-6 p-4 bg-gray-50 rounded-md">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Connected:</span> 
            <span className={isConnected ? 'text-green-600' : 'text-red-600'}>
              {isConnected ? 'Yes' : 'No'}
            </span>
          </div>
          <div>
            <span className="font-medium">Running:</span> 
            <span className={isRunning ? 'text-blue-600' : 'text-gray-600'}>
              {isRunning ? 'Yes' : 'No'}
            </span>
          </div>
          <div>
            <span className="font-medium">Progress:</span> {progress}%
          </div>
          <div>
            <span className="font-medium">Events:</span> {events.length}
          </div>
        </div>
        
        {currentMessage && (
          <div className="mt-2">
            <span className="font-medium">Current:</span> {currentMessage}
          </div>
        )}
        
        {error && (
          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-700">
            <span className="font-medium">Error:</span> {error}
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {progress > 0 && (
        <div className="mb-6">
          <div className="flex justify-between text-sm mb-1">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Events */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Events ({events.length})</h3>
        
        {events.length === 0 ? (
          <p className="text-gray-500">No events yet. Click "Simple Stream" or "LangGraph Stream" to begin.</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {events.map((event, index) => (
              <div key={index} className="p-3 bg-white border rounded-md">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="font-medium text-blue-600">{event.type}</span>
                    {event.progress !== undefined && (
                      <span className="ml-2 text-sm text-gray-600">({event.progress}%)</span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                
                {event.message && (
                  <p className="text-gray-700 mt-1">{event.message}</p>
                )}
                
                {event.sequence && (
                  <span className="text-xs text-gray-500">Sequence: {event.sequence}</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StreamingTest; 