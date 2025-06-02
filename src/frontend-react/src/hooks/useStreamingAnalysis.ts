import { useState, useEffect, useRef, useCallback } from 'react';

// Simplified event interface that matches backend exactly
export interface StreamingEvent {
  type: string;
  message?: string;
  progress?: number;
  timestamp: string;
  analysis_id?: string;
  event_id?: number;
  sequence?: number;
  // Additional fields from backend
  status?: string;
  error?: string;
  has_result?: boolean;
  // Cache-related fields
  cached?: boolean;
  cost_saved?: number;
  cache_hit?: boolean;
}

export interface StreamingAnalysisState {
  isConnected: boolean;
  isRunning: boolean;
  events: StreamingEvent[];
  latestEvent: StreamingEvent | null;
  progress: number;
  currentMessage: string;
  error: string | null;
  // Cache-related state
  isCached: boolean;
  costSaved: number;
  cacheMetadata: any;
  cacheStatus: string;
  // Research state
  researchEnabled: boolean;
}

export const useStreamingAnalysis = (analysisId: string | null, autoStart: boolean = false, defaultResearch: boolean = true) => {
  const [state, setState] = useState<StreamingAnalysisState>({
    isConnected: false,
    isRunning: false,
    events: [],
    latestEvent: null,
    progress: 0,
    currentMessage: '',
    error: null,
    isCached: false,
    costSaved: 0,
    cacheMetadata: null,
    cacheStatus: 'live',
    researchEnabled: defaultResearch
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const researchRef = useRef<boolean>(defaultResearch); // Track research state
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // Method: Check for cached analysis results
  const checkCachedAnalysis = useCallback(async (competitors: string[], focusArea: string) => {
    try {
      console.log('🔍 Checking for cached analysis...');
      
      const response = await fetch(`${baseUrl}/analyze-gaps-sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          competitors,
          focus_area: focusArea
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Check if this was a cache hit
        const isCacheHit = result.metadata?.cached === true || result.metadata?.cache_hit === true;
        
        if (isCacheHit) {
          console.log('✅ Cache HIT! Using cached results');
          
          // Update state with cache metadata
          setState(prev => ({
            ...prev,
            isCached: true,
            costSaved: result.metadata?.cost_saved || 0,
            cacheMetadata: result.metadata
          }));
          
          return {
            isCached: true,
            result,
            costSaved: result.metadata?.cost_saved || 0,
            processingTime: result.metadata?.processing_time || 0
          };
        } else {
          console.log('❌ Cache MISS - will need fresh analysis');
          return {
            isCached: false,
            result: null,
            costSaved: 0,
            processingTime: 0
          };
        }
      } else {
        console.error('Failed to check cache:', response.statusText);
        return { isCached: false, result: null, costSaved: 0, processingTime: 0 };
      }
    } catch (error) {
      console.error('Error checking cached analysis:', error);
      return { isCached: false, result: null, costSaved: 0, processingTime: 0 };
    }
  }, [baseUrl]);

  // Method: Connect to cached stream with simulated real-time experience
  const connectToCachedStream = useCallback((
    analysisId: string, 
    competitors: string[], 
    focusArea: string
  ) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setState(prev => ({
      ...prev,
      isConnected: false,
      isRunning: true,
      events: [],
      latestEvent: null,
      progress: 0,
      currentMessage: 'Connecting to cached analysis stream...',
      error: null,
      cacheStatus: 'checking'
    }));

    const competitorsParam = competitors.join(',');
    const url = `${baseUrl}/stream/cached/${analysisId}?competitors=${encodeURIComponent(competitorsParam)}&focus_area=${encodeURIComponent(focusArea)}`;
    
    console.log('🔄 Connecting to cached stream:', url);
    
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('✅ Cached stream connected');
      setState(prev => ({
        ...prev,
        isConnected: true,
        currentMessage: 'Connected to cached analysis stream'
      }));
    };

    eventSource.onmessage = (event) => {
      try {
        const data: StreamingEvent = JSON.parse(event.data);
        console.log('📨 Cached stream event:', data);

        setState(prev => {
          const newEvents = [...prev.events, data];
          
          // Update cache status based on event type
          let newCacheStatus = prev.cacheStatus;
          if (data.type === 'cache_hit') {
            newCacheStatus = 'hit';
          } else if (data.type === 'cache_miss' || data.type === 'cache_miss_redirect') {
            newCacheStatus = 'miss';
          }

          return {
            ...prev,
            events: newEvents,
            latestEvent: data,
            progress: data.progress || prev.progress,
            currentMessage: data.message || prev.currentMessage,
            cacheStatus: newCacheStatus,
            costSaved: data.cost_saved || prev.costSaved,
            isRunning: data.type !== 'streaming_complete' && data.type !== 'error' && data.type !== 'cache_miss_redirect'
          };
        });

        // Handle completion or redirection
        if (data.type === 'streaming_complete') {
          console.log('✅ Cached stream completed');
          eventSource.close();
        } else if (data.type === 'cache_miss_redirect') {
          console.log('🔄 Cache miss - redirecting to live analysis');
          eventSource.close();
          // Could automatically redirect to live streaming here
        }

      } catch (error) {
        console.error('❌ Error parsing cached stream event:', error);
        setState(prev => ({
          ...prev,
          error: `Failed to parse event: ${error}`,
          isRunning: false
        }));
      }
    };

    eventSource.onerror = (error) => {
      console.error('❌ Cached stream error:', error);
      setState(prev => ({
        ...prev,
        error: 'Cached stream connection failed',
        isConnected: false,
        isRunning: false
      }));
      eventSource.close();
    };
  }, [baseUrl]);

  // Method: Connect to LangGraph streaming (for live analysis with research support)
  const connectToLangGraphStream = useCallback((analysisId: string, researchEnabled?: boolean) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setState(prev => ({
      ...prev,
      isConnected: false,
      isRunning: true,
      events: [],
      latestEvent: null,
      progress: 0,
      currentMessage: 'Connecting to live analysis stream...',
      error: null,
      cacheStatus: 'live'
    }));

    // Use provided research flag or current ref value
    const useResearch = researchEnabled !== undefined ? researchEnabled : researchRef.current;
    const url = `${baseUrl}/stream/langgraph/${analysisId}${useResearch ? '?research=true' : ''}`;
    
    console.log('🔄 Connecting to LangGraph stream:', url);
    console.log('🔬 Research enabled:', useResearch);
    
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('✅ LangGraph stream connected');
      setState(prev => ({
        ...prev,
        isConnected: true,
        currentMessage: 'Connected to live analysis stream'
      }));
    };

    eventSource.onmessage = (event) => {
      try {
        const data: StreamingEvent = JSON.parse(event.data);
        console.log('📨 LangGraph stream event:', data);

        setState(prev => {
          const newEvents = [...prev.events, data];
          
          return {
            ...prev,
            events: newEvents,
            latestEvent: data,
            progress: data.progress || prev.progress,
            currentMessage: data.message || prev.currentMessage,
            isRunning: data.type !== 'stream_completed' && data.type !== 'error'
          };
        });

        // Handle completion
        if (data.type === 'stream_completed') {
          console.log('✅ LangGraph stream completed');
          eventSource.close();
        }

      } catch (error) {
        console.error('❌ Error parsing LangGraph stream event:', error);
        setState(prev => ({
          ...prev,
          error: `Failed to parse event: ${error}`,
          isRunning: false
        }));
      }
    };

    eventSource.onerror = (error) => {
      console.error('❌ LangGraph stream error:', error);
      setState(prev => ({
        ...prev,
        error: 'Live stream connection failed',
        isConnected: false,
        isRunning: false
      }));
      eventSource.close();
    };
  }, [baseUrl]);

  // Method: Smart analysis that checks cache first
  const startSmartAnalysis = useCallback(async (competitors: string[], focusArea: string) => {
    if (!analysisId) {
      console.error('No analysis ID provided');
      return;
    }

    try {
      console.log('🧠 Starting smart analysis (cache-aware)...');
      
      // Step 1: Check for cached results
      const cacheCheck = await checkCachedAnalysis(competitors, focusArea);
      
      if (cacheCheck.isCached && cacheCheck.result) {
        console.log('✅ Using cached results with simulated streaming');
        
        // Use cached streaming for better UX
        connectToCachedStream(analysisId, competitors, focusArea);
        
        return {
          fromCache: true,
          result: cacheCheck.result,
          costSaved: cacheCheck.costSaved,
          processingTime: cacheCheck.processingTime
        };
      } else {
        console.log('🔄 No cache available, running live analysis');
        
        // Use LangGraph streaming for fresh analysis
        connectToLangGraphStream(analysisId);
        
        return {
          fromCache: false,
          result: null,
          costSaved: 0,
          processingTime: 0
        };
      }
      
    } catch (error) {
      console.error('Error in smart analysis:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to start smart analysis'
      }));
      
      return {
        fromCache: false,
        result: null,
        costSaved: 0,
        processingTime: 0
      };
    }
  }, [analysisId, checkCachedAnalysis, connectToCachedStream, connectToLangGraphStream]);

  // Method: Disconnect
  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      console.log('🔌 Disconnecting stream');
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    setState(prev => ({
      ...prev,
      isConnected: false,
      isRunning: false,
      currentMessage: 'Disconnected'
    }));
  }, []);

  // Method: Start basic analysis (backward compatibility)
  const startAnalysis = useCallback((competitors: string[], focusArea: string) => {
    if (!analysisId) {
      console.error('No analysis ID provided');
      return;
    }

    console.log('🚀 Starting basic analysis...', { competitors, focusArea });
    connectToLangGraphStream(analysisId, researchRef.current);
  }, [analysisId, connectToLangGraphStream]);

  // Research control methods
  const setResearchEnabled = useCallback((enabled: boolean) => {
    researchRef.current = enabled;
    setState(prev => ({
      ...prev,
      researchEnabled: enabled
    }));
  }, []);

  const toggleResearch = useCallback(() => {
    const newValue = !researchRef.current;
    researchRef.current = newValue;
    setState(prev => ({
      ...prev,
      researchEnabled: newValue
    }));
  }, []);

  // Auto-start effect
  useEffect(() => {
    if (autoStart && analysisId) {
      console.log('🎬 Auto-starting streaming for:', analysisId);
      connectToLangGraphStream(analysisId, researchRef.current);
    }
    
    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [autoStart, analysisId, connectToLangGraphStream, disconnect]);

  return {
    ...state,
    connectToCachedStream,
    connectToLangGraphStream,
    disconnect,
    startAnalysis,
    startSmartAnalysis,
    checkCachedAnalysis,
    setResearchEnabled,
    toggleResearch
  };
}; 