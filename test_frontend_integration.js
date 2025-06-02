// Frontend Integration Test
// Tests the complete cached streaming flow as the React frontend would experience it

const { EventSource } = require('eventsource');

console.log('🧪 Testing Frontend Integration with Cached Streaming');
console.log('='.repeat(60));

// Test configuration matching what frontend sends
const config = {
  baseUrl: 'http://localhost:8000',
  analysisId: 'frontend_integration_test_' + Date.now(),
  competitors: ['Stryker Spine', 'Zimmer Biomet'],
  focusArea: 'spine_fusion'
};

console.log('📋 Test Configuration:');
console.log(`   Base URL: ${config.baseUrl}`);
console.log(`   Analysis ID: ${config.analysisId}`);
console.log(`   Competitors: ${config.competitors.join(', ')}`);
console.log(`   Focus Area: ${config.focusArea}`);
console.log('');

// Step 1: Test cache status API (what frontend calls to check cache stats)
async function testCacheStatus() {
  console.log('1️⃣  Testing Cache Status API...');
  
  try {
    const response = await fetch(`${config.baseUrl}/cache/stats`);
    const stats = await response.json();
    
    console.log(`   ✅ Cache Stats: ${stats.total_cache_entries} entries, ${stats.hit_rate}% hit rate`);
    console.log(`   💰 Estimated Savings: $${stats.estimated_cost_saved}`);
    return true;
  } catch (error) {
    console.log(`   ❌ Cache Status Failed: ${error.message}`);
    return false;
  }
}

// Step 2: Test cached streaming (main frontend functionality)
function testCachedStreaming() {
  return new Promise((resolve) => {
    console.log('2️⃣  Testing Cached Streaming...');
    
    const competitorsParam = encodeURIComponent(config.competitors.join(','));
    const focusAreaParam = encodeURIComponent(config.focusArea);
    const streamUrl = `${config.baseUrl}/stream/cached/${config.analysisId}?competitors=${competitorsParam}&focus_area=${focusAreaParam}`;
    
    console.log(`   🔗 Connecting to: ${streamUrl}`);
    
    const eventSource = new EventSource(streamUrl);
    const events = [];
    let cacheHit = false;
    let costSaved = 0;
    
    eventSource.onopen = () => {
      console.log('   ✅ SSE Connection opened');
    };
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        events.push(data);
        
        console.log(`   📨 Event: ${data.type} - ${data.message || 'No message'} (${data.progress || 0}%)`);
        
        // Track cache-specific events
        if (data.type === 'cache_hit') {
          cacheHit = true;
          costSaved = data.cost_saved || 0;
          console.log(`   💰 Cache HIT! Saved $${costSaved}`);
        }
        
        // Check for completion
        if (data.type === 'streaming_complete' || data.type === 'analysis_completed') {
          eventSource.close();
          
          console.log('   🏁 Streaming completed');
          console.log(`   📊 Total events received: ${events.length}`);
          console.log(`   🎯 Cache hit: ${cacheHit ? 'YES' : 'NO'}`);
          if (cacheHit) console.log(`   💵 Cost saved: $${costSaved}`);
          
          resolve({
            success: true,
            eventsCount: events.length,
            cacheHit,
            costSaved,
            events
          });
        }
        
      } catch (error) {
        console.log(`   ❌ Failed to parse event: ${error.message}`);
        eventSource.close();
        resolve({ success: false, error: error.message });
      }
    };
    
    eventSource.onerror = (error) => {
      console.log(`   ❌ SSE Error: ${error.message || 'Connection error'}`);
      eventSource.close();
      resolve({ success: false, error: 'SSE connection failed' });
    };
    
    // Timeout after 30 seconds
    setTimeout(() => {
      if (eventSource.readyState !== EventSource.CLOSED) {
        console.log('   ⏰ Test timeout - closing connection');
        eventSource.close();
        resolve({ success: false, error: 'Timeout' });
      }
    }, 30000);
  });
}

// Step 3: Test sync analysis API (for full analysis data)
async function testSyncAnalysis() {
  console.log('3️⃣  Testing Sync Analysis API...');
  
  try {
    const response = await fetch(`${config.baseUrl}/analyze-gaps-sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        competitors: config.competitors,
        focus_area: config.focusArea
      })
    });
    
    const result = await response.json();
    
    console.log(`   ✅ Analysis completed: ${result.metadata?.cached ? 'CACHED' : 'FRESH'}`);
    console.log(`   📈 Opportunities: ${result.top_opportunities?.length || 0}`);
    console.log(`   🔍 Clinical Gaps: ${result.clinical_gaps?.length || 0}`);
    console.log(`   📊 Final Report: ${result.final_report ? 'YES' : 'NO'}`);
    console.log(`   ⏱️  Processing Time: ${result.metadata?.processing_time?.toFixed(3)}s`);
    if (result.metadata?.cost_saved) {
      console.log(`   💰 Cost Saved: $${result.metadata.cost_saved}`);
    }
    
    return {
      success: true,
      cached: result.metadata?.cached || false,
      opportunitiesCount: result.top_opportunities?.length || 0,
      gapsCount: result.clinical_gaps?.length || 0,
      hasFinalReport: !!result.final_report,
      processingTime: result.metadata?.processing_time || 0,
      costSaved: result.metadata?.cost_saved || 0
    };
    
  } catch (error) {
    console.log(`   ❌ Sync Analysis Failed: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// Run all tests
async function runIntegrationTests() {
  console.log('🚀 Starting Frontend Integration Tests...');
  console.log('');
  
  const results = {
    cacheStatus: await testCacheStatus(),
    streaming: null,
    syncAnalysis: null
  };
  
  console.log('');
  
  if (results.cacheStatus) {
    results.streaming = await testCachedStreaming();
    console.log('');
    results.syncAnalysis = await testSyncAnalysis();
  }
  
  console.log('');
  console.log('📋 Test Results Summary:');
  console.log('='.repeat(60));
  console.log(`Cache Status API: ${results.cacheStatus ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Cached Streaming: ${results.streaming?.success ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Sync Analysis API: ${results.syncAnalysis?.success ? '✅ PASS' : '❌ FAIL'}`);
  
  if (results.streaming?.success) {
    console.log(`Streaming Events: ${results.streaming.eventsCount} events received`);
    console.log(`Cache Performance: ${results.streaming.cacheHit ? `HIT ($${results.streaming.costSaved} saved)` : 'MISS'}`);
  }
  
  if (results.syncAnalysis?.success) {
    console.log(`Analysis Data: ${results.syncAnalysis.opportunitiesCount} opportunities, ${results.syncAnalysis.gapsCount} gaps`);
    console.log(`Data Source: ${results.syncAnalysis.cached ? 'CACHED' : 'FRESH'}`);
  }
  
  const allPassed = results.cacheStatus && results.streaming?.success && results.syncAnalysis?.success;
  console.log('');
  console.log(`🎯 Overall Result: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
  
  if (allPassed) {
    console.log('🎉 Frontend integration is working perfectly!');
    console.log('   - Cache system operational');
    console.log('   - Streaming events working');
    console.log('   - Full analysis data available');
    console.log('   - Cost savings tracked');
  }
}

// Check if we're running this directly
if (require.main === module) {
  runIntegrationTests().catch(console.error);
}

module.exports = { runIntegrationTests, testCacheStatus, testCachedStreaming, testSyncAnalysis }; 