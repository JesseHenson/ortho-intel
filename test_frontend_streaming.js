#!/usr/bin/env node

/**
 * Test script to verify frontend streaming integration
 * Simulates what the React frontend should be doing
 */

const { EventSource } = require('eventsource');

const BACKEND_URL = 'http://localhost:8000';
const ANALYSIS_ID = 'test-frontend-integration';

console.log('🧪 Testing Frontend Streaming Integration');
console.log(`📡 Connecting to: ${BACKEND_URL}/stream/simple/${ANALYSIS_ID}`);

const eventSource = new EventSource(`${BACKEND_URL}/stream/simple/${ANALYSIS_ID}`);

let eventCount = 0;
const startTime = Date.now();

eventSource.onopen = () => {
  console.log('✅ Connection opened successfully');
};

eventSource.onmessage = (event) => {
  eventCount++;
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  
  console.log(`📨 [${elapsed}s] Event #${eventCount}:`);
  
  try {
    const data = JSON.parse(event.data);
    console.log(`   Type: ${data.type}`);
    console.log(`   Message: ${data.message || 'N/A'}`);
    console.log(`   Progress: ${data.progress || 'N/A'}%`);
    console.log(`   Timestamp: ${data.timestamp || 'N/A'}`);
    
    // Check for completion
    if (data.type === 'stream_completed' || data.type === 'analysis_completed') {
      console.log('🏁 Stream completed successfully!');
      console.log(`📊 Total events received: ${eventCount}`);
      console.log(`⏱️  Total time: ${elapsed}s`);
      eventSource.close();
      process.exit(0);
    }
  } catch (error) {
    console.error(`❌ Failed to parse event data: ${error.message}`);
    console.error(`   Raw data: ${event.data}`);
  }
  
  console.log('');
};

eventSource.onerror = (error) => {
  console.error('❌ SSE Error:', error);
  console.error('   ReadyState:', eventSource.readyState);
  
  // ReadyState: 0=CONNECTING, 1=OPEN, 2=CLOSED
  const stateMap = {0: 'CONNECTING', 1: 'OPEN', 2: 'CLOSED'};
  console.error('   State:', stateMap[eventSource.readyState] || 'UNKNOWN');
  
  if (eventSource.readyState === 2) { // CLOSED
    console.error('🔌 Connection closed');
    process.exit(1);
  }
};

// Timeout after 15 seconds
setTimeout(() => {
  console.log('⏰ Test timeout - closing connection');
  console.log(`📊 Events received before timeout: ${eventCount}`);
  eventSource.close();
  process.exit(eventCount > 0 ? 0 : 1);
}, 15000);

console.log('⏳ Waiting for events...\n'); 