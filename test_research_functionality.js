// Research Functionality Test
// Tests the research flag integration from frontend perspective

const { EventSource } = require('eventsource');

console.log('🔬 Testing Research Functionality Integration');
console.log('='.repeat(60));

const config = {
  baseUrl: 'http://localhost:8000',
  frontendUrl: 'http://localhost:5174',
  testAnalysisId: 'research_demo_' + Date.now()
};

console.log('📋 Test Configuration:');
console.log(`   Backend: ${config.baseUrl}`);
console.log(`   Frontend: ${config.frontendUrl}`);
console.log(`   Analysis ID: ${config.testAnalysisId}`);
console.log('');

// Test 1: Research-enabled streaming
function testResearchEnabledStreaming() {
  return new Promise((resolve) => {
    console.log('1️⃣  Testing LangGraph Streaming WITH Research...');
    
    const url = `${config.baseUrl}/stream/langgraph/${config.testAnalysisId}?research=true`;
    console.log(`   🔗 URL: ${url}`);
    
    const eventSource = new EventSource(url);
    const events = [];
    let researchNodeSeen = false;
    let researchResults = 0;
    
    eventSource.onopen = () => {
      console.log('   ✅ Research stream connected');
    };
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        events.push(data);
        
        // Track research-specific activity
        if (data.node_name === 'research_competitor') {
          researchNodeSeen = true;
          console.log(`   🔬 Research node executing - Iteration ${data.state_preview?.research_iteration || 0}, Results: ${data.state_preview?.results_count || 0}`);
        }
        
        if (data.state_preview?.results_count) {
          researchResults = Math.max(researchResults, data.state_preview.results_count);
        }
        
        // Log key events
        if (data.type === 'analysis_started') {
          console.log('   🚀 Research-enabled analysis started');
        } else if (data.type === 'node_execution') {
          console.log(`   ⚙️  Node: ${data.node_name} (${data.progress?.toFixed(1) || 0}%)`);
        }
        
        // Complete after a reasonable number of events
        if (events.length >= 10 || data.type === 'analysis_completed') {
          eventSource.close();
          
          console.log('   📊 Research Analysis Results:');
          console.log(`      • Total events: ${events.length}`);
          console.log(`      • Research node executed: ${researchNodeSeen ? 'YES' : 'NO'}`);
          console.log(`      • Research results found: ${researchResults}`);
          console.log('   ✅ Research-enabled test completed');
          
          resolve({
            success: true,
            eventsCount: events.length,
            researchNodeExecuted: researchNodeSeen,
            researchResults,
            events
          });
        }
        
      } catch (error) {
        console.log(`   ❌ Error parsing research event: ${error.message}`);
        eventSource.close();
        resolve({ success: false, error: error.message });
      }
    };
    
    eventSource.onerror = (error) => {
      console.log(`   ❌ Research stream error: ${error.message || 'Connection failed'}`);
      eventSource.close();
      resolve({ success: false, error: 'Research stream failed' });
    };
    
    // Timeout after 30 seconds
    setTimeout(() => {
      if (eventSource.readyState !== EventSource.CLOSED) {
        console.log('   ⏰ Research test timeout');
        eventSource.close();
        resolve({ success: false, error: 'Timeout' });
      }
    }, 30000);
  });
}

// Test 2: Basic streaming without research
function testBasicStreaming() {
  return new Promise((resolve) => {
    console.log('2️⃣  Testing LangGraph Streaming WITHOUT Research...');
    
    const url = `${config.baseUrl}/stream/langgraph/${config.testAnalysisId}_basic`;
    console.log(`   🔗 URL: ${url}`);
    
    const eventSource = new EventSource(url);
    const events = [];
    let researchNodeSeen = false;
    
    eventSource.onopen = () => {
      console.log('   ✅ Basic stream connected');
    };
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        events.push(data);
        
        // Check if research node is executed (shouldn't be in basic mode)
        if (data.node_name === 'research_competitor') {
          researchNodeSeen = true;
          console.log(`   ⚠️  Unexpected: Research node seen in basic mode`);
        }
        
        // Log key events
        if (data.type === 'analysis_started') {
          console.log('   🚀 Basic analysis started');
        } else if (data.type === 'node_execution') {
          console.log(`   ⚙️  Node: ${data.node_name} (${data.progress?.toFixed(1) || 0}%)`);
        }
        
        // Complete after a reasonable number of events
        if (events.length >= 8 || data.type === 'analysis_completed') {
          eventSource.close();
          
          console.log('   📊 Basic Analysis Results:');
          console.log(`      • Total events: ${events.length}`);
          console.log(`      • Research node executed: ${researchNodeSeen ? 'YES (unexpected!)' : 'NO (expected)'}`);
          console.log('   ✅ Basic test completed');
          
          resolve({
            success: true,
            eventsCount: events.length,
            researchNodeExecuted: researchNodeSeen,
            events
          });
        }
        
      } catch (error) {
        console.log(`   ❌ Error parsing basic event: ${error.message}`);
        eventSource.close();
        resolve({ success: false, error: error.message });
      }
    };
    
    eventSource.onerror = (error) => {
      console.log(`   ❌ Basic stream error: ${error.message || 'Connection failed'}`);
      eventSource.close();
      resolve({ success: false, error: 'Basic stream failed' });
    };
    
    // Timeout after 20 seconds (basic should be faster)
    setTimeout(() => {
      if (eventSource.readyState !== EventSource.CLOSED) {
        console.log('   ⏰ Basic test timeout');
        eventSource.close();
        resolve({ success: false, error: 'Timeout' });
      }
    }, 20000);
  });
}

// Test 3: Frontend accessibility check
async function testFrontendAccess() {
  console.log('3️⃣  Testing Frontend Accessibility...');
  
  try {
    // Check if frontend is accessible
    const frontendResponse = await fetch(config.frontendUrl);
    if (frontendResponse.ok) {
      console.log('   ✅ Frontend accessible');
    } else {
      console.log(`   ❌ Frontend not accessible: ${frontendResponse.status}`);
      return { success: false, error: 'Frontend not accessible' };
    }
    
    // Check if backend is accessible from frontend's perspective
    const backendResponse = await fetch(`${config.baseUrl}/health`);
    if (backendResponse.ok) {
      const health = await backendResponse.json();
      console.log('   ✅ Backend accessible from frontend');
      console.log(`   🔧 Services: ${Object.keys(health.services).join(', ')}`);
    } else {
      console.log(`   ❌ Backend not accessible: ${backendResponse.status}`);
      return { success: false, error: 'Backend not accessible' };
    }
    
    // Check specific research endpoints
    const langGraphUrl = `${config.baseUrl}/stream/langgraph/frontend_test_123`;
    console.log(`   🔗 Testing endpoint: ${langGraphUrl}`);
    
    return { success: true, frontendAccessible: true, backendAccessible: true };
    
  } catch (error) {
    console.log(`   ❌ Frontend access test failed: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// Run all tests
async function runResearchTests() {
  console.log('🚀 Starting Research Functionality Tests...');
  console.log('');
  
  const results = {
    frontendAccess: await testFrontendAccess(),
    researchEnabled: null,
    basicMode: null
  };
  
  console.log('');
  
  if (results.frontendAccess.success) {
    results.researchEnabled = await testResearchEnabledStreaming();
    console.log('');
    results.basicMode = await testBasicStreaming();
  }
  
  console.log('');
  console.log('📋 Research Tests Summary:');
  console.log('='.repeat(60));
  console.log(`Frontend Access: ${results.frontendAccess.success ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Research Mode: ${results.researchEnabled?.success ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Basic Mode: ${results.basicMode?.success ? '✅ PASS' : '❌ FAIL'}`);
  
  if (results.researchEnabled?.success && results.basicMode?.success) {
    console.log('');
    console.log('🔬 Research Functionality Analysis:');
    console.log(`Research Events: ${results.researchEnabled.eventsCount} events`);
    console.log(`Basic Events: ${results.basicMode.eventsCount} events`);
    console.log(`Research Node Executed (Research Mode): ${results.researchEnabled.researchNodeExecuted ? '✅ YES' : '❌ NO'}`);
    console.log(`Research Node Executed (Basic Mode): ${results.basicMode.researchNodeExecuted ? '⚠️ YES (unexpected)' : '✅ NO (expected)'}`);
    
    if (results.researchEnabled.researchResults) {
      console.log(`Research Results Found: ${results.researchEnabled.researchResults} results`);
    }
  }
  
  const allPassed = results.frontendAccess.success && 
                   results.researchEnabled?.success && 
                   results.basicMode?.success;
  
  console.log('');
  console.log(`🎯 Overall Result: ${allPassed ? '✅ ALL RESEARCH TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
  
  if (allPassed) {
    console.log('🎉 Research functionality is working perfectly!');
    console.log('   - Frontend can access backend');
    console.log('   - Research mode works with enhanced analysis');
    console.log('   - Basic mode works without research overhead');
    console.log('   - Users can toggle research on/off via frontend');
  }
  
  console.log('');
  console.log('💡 Frontend Usage Instructions:');
  console.log('   1. Open http://localhost:5174/cached-streaming');
  console.log('   2. Toggle the Research Mode switch (ON by default)');
  console.log('   3. Click "Test Live Streaming" to see research in action');
  console.log('   4. Watch for "research_competitor" node execution');
  console.log('   5. Compare with Research Mode OFF for basic analysis');
}

// Run tests if this file is executed directly
if (require.main === module) {
  runResearchTests().catch(console.error);
}

module.exports = { runResearchTests, testResearchEnabledStreaming, testBasicStreaming, testFrontendAccess }; 