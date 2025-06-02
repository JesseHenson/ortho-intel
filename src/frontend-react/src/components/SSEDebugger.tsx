import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, Bug, Copy, Download } from 'lucide-react';

interface SSEDebuggerProps {
  analysisId: string;
  isConnected: boolean;
  events: any[];
  error: string | null;
  baseUrl?: string;
}

const SSEDebugger: React.FC<SSEDebuggerProps> = ({
  analysisId,
  isConnected,
  events,
  error,
  baseUrl = 'http://localhost:8000'
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [networkInfo, setNetworkInfo] = useState<any>(null);

  // Network diagnostics
  useEffect(() => {
    const runDiagnostics = async () => {
      try {
        // Test basic connectivity
        const healthResponse = await fetch(`${baseUrl}/health`);
        const healthData = await healthResponse.json();
        
        setNetworkInfo({
          baseUrl,
          healthCheck: healthResponse.ok,
          healthData,
          timestamp: new Date().toISOString()
        });
      } catch (err) {
        setNetworkInfo({
          baseUrl,
          healthCheck: false,
          error: err instanceof Error ? err.message : 'Unknown error',
          timestamp: new Date().toISOString()
        });
      }
    };

    runDiagnostics();
  }, [baseUrl]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const exportDebugData = () => {
    const debugData = {
      analysisId,
      isConnected,
      error,
      events,
      networkInfo,
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(debugData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sse-debug-${analysisId}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!isExpanded) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsExpanded(true)}
          className={`p-3 rounded-full shadow-lg flex items-center space-x-2 text-white transition-all ${
            isConnected 
              ? error 
                ? 'bg-yellow-500 hover:bg-yellow-600' 
                : 'bg-green-500 hover:bg-green-600'
              : 'bg-red-500 hover:bg-red-600'
          }`}
        >
          <Bug className="w-5 h-5" />
          {isConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
          <span className="text-sm font-medium">{events.length}</span>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50 max-h-96 overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 px-4 py-2 border-b flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bug className="w-4 h-4 text-gray-600" />
          <span className="font-medium text-gray-800">SSE Debugger</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={exportDebugData}
            className="p-1 hover:bg-gray-200 rounded"
            title="Export debug data"
          >
            <Download className="w-4 h-4 text-gray-600" />
          </button>
          <button
            onClick={() => setIsExpanded(false)}
            className="p-1 hover:bg-gray-200 rounded"
          >
            ×
          </button>
        </div>
      </div>

      <div className="p-4 space-y-3 overflow-y-auto max-h-80">
        {/* Connection Status */}
        <div className="space-y-2">
          <h3 className="font-medium text-sm text-gray-700">Connection Status</h3>
          <div className={`flex items-center space-x-2 text-sm ${
            isConnected ? 'text-green-600' : 'text-red-600'
          }`}>
            {isConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded p-2">
              <p className="text-xs text-red-700">{error}</p>
            </div>
          )}
        </div>

        {/* Network Info */}
        {networkInfo && (
          <div className="space-y-2">
            <h3 className="font-medium text-sm text-gray-700">Network</h3>
            <div className="bg-gray-50 rounded p-2 space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span>Health Check:</span>
                <span className={networkInfo.healthCheck ? 'text-green-600' : 'text-red-600'}>
                  {networkInfo.healthCheck ? '✓' : '✗'}
                </span>
              </div>
              <div className="text-xs text-gray-600">
                URL: {baseUrl}
              </div>
              <button
                onClick={() => copyToClipboard(`${baseUrl}/stream/${analysisId}`)}
                className="flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-800"
              >
                <Copy className="w-3 h-3" />
                <span>Copy SSE URL</span>
              </button>
            </div>
          </div>
        )}

        {/* Events */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-sm text-gray-700">Events ({events.length})</h3>
            <button
              onClick={() => copyToClipboard(JSON.stringify(events, null, 2))}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Copy All
            </button>
          </div>
          
          {events.length === 0 ? (
            <p className="text-xs text-gray-500">No events received</p>
          ) : (
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {events.slice(-5).map((event, index) => (
                <div key={index} className="bg-gray-50 rounded p-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-gray-700">
                      {event.type || 'unknown'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  {event.message && (
                    <p className="text-xs text-gray-600 mt-1">{event.message}</p>
                  )}
                  {event.progress !== undefined && (
                    <div className="flex items-center space-x-2 mt-1">
                      <div className="flex-1 bg-gray-200 rounded-full h-1">
                        <div 
                          className="bg-blue-500 h-1 rounded-full transition-all"
                          style={{ width: `${event.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">{event.progress}%</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Debug Commands */}
        <div className="space-y-2">
          <h3 className="font-medium text-sm text-gray-700">Debug Commands</h3>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => console.log('SSE Debug Data:', {analysisId, isConnected, events, error})}
              className="text-xs bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded px-2 py-1"
            >
              Log to Console
            </button>
            <button
              onClick={() => window.open(`${baseUrl}/stream/${analysisId}`, '_blank')}
              className="text-xs bg-green-50 hover:bg-green-100 border border-green-200 rounded px-2 py-1"
            >
              Test in Browser
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SSEDebugger; 