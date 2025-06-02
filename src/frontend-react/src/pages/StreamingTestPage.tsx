import React, { useState, useRef, useEffect } from 'react';
import { Play, Square, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import SSEDebugger from '../components/SSEDebugger';

interface StreamingEvent {
  type: string;
  message: string;
  progress?: number;
  timestamp: string;
  analysis_id?: string;
}

const StreamingTestPage: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState<StreamingEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [analysisId, setAnalysisId] = useState('test-streaming-frontend');
  const [researchEnabled, setResearchEnabled] = useState(true);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connectStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setError(null);
    setEvents([]);
    setIsRunning(true);

    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    // Use LangGraph endpoint with research parameter
    const researchParam = researchEnabled ? '?research=true' : '';
    const eventSource = new EventSource(`${baseUrl}/stream/langgraph/${analysisId}${researchParam}`);
    eventSourceRef.current = eventSource;

    console.log('🔗 Connecting to:', `${baseUrl}/stream/langgraph/${analysisId}${researchParam}`);
    console.log('🔬 Research enabled:', researchEnabled);

    eventSource.onopen = () => {
      console.log('✅ Streaming connection opened');
      setIsConnected(true);
    };

    eventSource.onmessage = (event) => {
      console.log('📨 Received event:', event.data);
      try {
        const data = JSON.parse(event.data);
        setEvents(prev => [...prev, data]);
        
        // Check if stream is complete
        if (data.type === 'stream_complete' || data.type === 'analysis_completed') {
          setTimeout(() => {
            setIsRunning(false);
          }, 1000);
        }
      } catch (e) {
        console.error('❌ Failed to parse event data:', e);
        setError(`Failed to parse event: ${e}`);
      }
    };

    eventSource.onerror = (event) => {
      console.group('❌ SSE Error in StreamingTestPage');
      console.error('Error event:', event);
      console.error('EventSource readyState:', eventSource.readyState);
      
      // ReadyState: 0=CONNECTING, 1=OPEN, 2=CLOSED
      const stateMap: Record<number, string> = {0: 'CONNECTING', 1: 'OPEN', 2: 'CLOSED'};
      console.error('Connection state:', stateMap[eventSource.readyState] || 'UNKNOWN');
      
      // Only treat as error if connection is actually closed or failed
      if (eventSource.readyState === EventSource.CLOSED) {
        console.error('Connection was closed');
        setError('Connection closed unexpectedly');
        setIsConnected(false);
        setIsRunning(false);
      } else if (eventSource.readyState === EventSource.CONNECTING) {
        // This is normal - just connecting/reconnecting
        console.log('EventSource is connecting/reconnecting...');
        setError(null); // Clear any previous errors during reconnection
      } else {
        // readyState === 1 (OPEN) but we got an error - this shouldn't happen
        console.warn('Got error event but connection is still open');
      }
      
      console.groupEnd();
    };
  };

  const disconnectStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsConnected(false);
    setIsRunning(false);
  };

  useEffect(() => {
    return () => {
      disconnectStream();
    };
  }, []);

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'analysis_started':
        return <Play className="w-4 h-4 text-blue-500" />;
      case 'analysis_completed':
      case 'stream_complete':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <RefreshCw className="w-4 h-4 text-gray-500" />;
    }
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case 'connected':
        return 'border-l-green-500 bg-green-50';
      case 'analysis_started':
        return 'border-l-blue-500 bg-blue-50';
      case 'analysis_completed':
      case 'stream_complete':
        return 'border-l-green-500 bg-green-50';
      case 'error':
        return 'border-l-red-500 bg-red-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  const toggleResearch = () => {
    setResearchEnabled(!researchEnabled);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Streaming Test Page
        </h1>
        <p className="text-gray-600">
          Test Server-Sent Events (SSE) streaming functionality
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="space-y-4">
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
          
          {/* Research Toggle */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-blue-900">
                  🔬 Research Mode
                </h3>
                <p className="text-sm text-blue-700 mt-1">
                  {researchEnabled 
                    ? 'Enhanced analysis with research-backed insights' 
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
          
          <div className="flex space-x-4">
            <button
              onClick={connectStream}
              disabled={isRunning}
              className="btn-primary flex items-center space-x-2"
            >
              <Play className="w-4 h-4" />
              <span>Start Streaming</span>
            </button>
            
            <button
              onClick={disconnectStream}
              disabled={!isRunning}
              className="btn-secondary flex items-center space-x-2"
            >
              <Square className="w-4 h-4" />
              <span>Stop Streaming</span>
            </button>
          </div>
          
          {/* Status */}
          <div className="flex items-center space-x-4 text-sm">
            <div className={`flex items-center space-x-2 ${
              isConnected ? 'text-green-600' : 'text-gray-500'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-gray-400'
              }`}></div>
              <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
            
            <div className={`flex items-center space-x-2 ${
              isRunning ? 'text-blue-600' : 'text-gray-500'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                isRunning ? 'bg-blue-500 animate-pulse' : 'bg-gray-400'
              }`}></div>
              <span>{isRunning ? 'Streaming' : 'Idle'}</span>
            </div>
            
            <div className="text-gray-600">
              Events: {events.length}
            </div>
          </div>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                <span className="text-red-700">{error}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Events */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Streaming Events
        </h2>
        
        {events.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No events yet. Click "Start Streaming" to begin.
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {events.map((event, index) => (
              <div
                key={index}
                className={`border-l-4 p-4 rounded-r-lg ${
                  getEventColor(event.type)
                }`}
              >
                <div className="flex items-start space-x-3">
                  {getEventIcon(event.type)}
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
                    </div>
                    
                    {event.message && (
                      <p className="text-gray-700 mt-1">
                        {event.message}
                      </p>
                    )}
                    
                    <div className="text-xs text-gray-500 mt-2">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* SSE Debugger */}
      <SSEDebugger 
        analysisId={analysisId}
        isConnected={isConnected}
        events={events}
        error={error}
        baseUrl={import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
      />
    </div>
  );
};

export default StreamingTestPage; 