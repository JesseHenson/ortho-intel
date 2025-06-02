// Debug helper functions - available in browser console as window.debug

export const debugHelpers = {
  // Test SSE connection manually
  testSSE: (url: string) => {
    console.log(`🧪 Testing SSE connection to: ${url}`);
    const eventSource = new EventSource(url);
    
    eventSource.onopen = () => console.log('✅ SSE connection opened');
    eventSource.onmessage = (event) => console.log('📨 SSE message:', JSON.parse(event.data));
    eventSource.onerror = (error) => console.error('❌ SSE error:', error);
    
    return eventSource;
  },

  // Check all active SSE connections
  getActiveConnections: (): any[] => {
    const connections: any[] = [];
    // Note: No direct way to enumerate EventSource connections
    console.log('Active EventSource connections require manual tracking');
    return connections;
  },

  // Network diagnostics
  networkDiagnostics: async (baseUrl: string) => {
    const results = {
      ping: false,
      health: false,
      cors: false,
      streaming: false
    };

    try {
      // Test basic connectivity
      const response = await fetch(`${baseUrl}/health`);
      results.health = response.ok;
      results.ping = true;
      results.cors = !response.headers.get('access-control-allow-origin')?.includes('*');
      
      console.log('🔍 Network Diagnostics:', results);
    } catch (error) {
      console.error('❌ Network diagnostic failed:', error);
    }

    return results;
  },

  // React component finder
  findReactComponent: (element: Element) => {
    const key = Object.keys(element).find(key => 
      key.startsWith('__reactInternalInstance') || key.startsWith('__reactFiber')
    );
    return key ? (element as any)[key] : null;
  },

  // Memory usage
  getMemoryUsage: () => {
    if ('memory' in performance) {
      return {
        used: Math.round((performance.memory as any).usedJSHeapSize / 1048576),
        total: Math.round((performance.memory as any).totalJSHeapSize / 1048576),
        limit: Math.round((performance.memory as any).jsHeapSizeLimit / 1048576)
      };
    }
    return 'Memory API not available';
  },

  // Export current state for AI analysis
  exportStateForAI: () => {
    const state = {
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      localStorage: { ...localStorage },
      sessionStorage: { ...sessionStorage },
      environmentVariables: {
        // Extract Vite env vars
        ...(Object.keys(import.meta.env).reduce((acc, key) => {
          if (key.startsWith('VITE_')) {
            acc[key] = import.meta.env[key];
          }
          return acc;
        }, {} as Record<string, any>))
      },
      networkStatus: navigator.onLine,
      memory: debugHelpers.getMemoryUsage()
    };

    const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `debug-state-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    console.log('📊 Debug state exported for AI analysis');
    return state;
  }
};

// Make available globally
if (typeof window !== 'undefined') {
  (window as any).debug = debugHelpers;
  console.log('🛠️ Debug helpers loaded. Use window.debug in console.');
} 