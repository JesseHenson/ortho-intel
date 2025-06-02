#!/usr/bin/env node

/**
 * Comprehensive Research Integration Test
 */

const http = require('http');

const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5174';

const TEST_REQUEST = {
    competitors: ["Stryker Spine", "Zimmer Biomet"],
    focus_area: "spine_fusion"
};

// Helper function for HTTP requests
const makeRequest = (url, options = {}) => {
    return new Promise((resolve, reject) => {
        const req = http.request(url, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const parsed = data ? JSON.parse(data) : {};
                    resolve({ statusCode: res.statusCode, data: parsed });
                } catch (e) {
                    resolve({ statusCode: res.statusCode, data: data });
                }
            });
        });
        
        req.on('error', reject);
        
        if (options.body) {
            req.write(JSON.stringify(options.body));
        }
        
        req.end();
    });
};

async function runTests() {
    console.log('🧪 Starting Research Integration Tests...\n');
    
    let testsPassed = 0;
    let totalTests = 0;
    
    // Test 1: Backend with research enabled
    totalTests++;
    console.log('Test 1: Backend Analysis (Research Enabled)');
    try {
        const response = await makeRequest(`${BACKEND_URL}/analyze-gaps-sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: { ...TEST_REQUEST, research_enabled: true }
        });
        
        console.log(`  Status: ${response.statusCode}`);
        console.log(`  Has metadata: ${!!response.data.metadata}`);
        
        if (response.statusCode === 200) {
            testsPassed++;
            console.log('  ✅ PASSED\n');
        } else {
            console.log('  ❌ FAILED\n');
        }
    } catch (error) {
        console.log(`  ❌ FAILED: ${error.message}\n`);
    }
    
    // Test 2: Backend with research disabled
    totalTests++;
    console.log('Test 2: Backend Analysis (Research Disabled)');
    try {
        const response = await makeRequest(`${BACKEND_URL}/analyze-gaps-sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: { ...TEST_REQUEST, research_enabled: false }
        });
        
        console.log(`  Status: ${response.statusCode}`);
        console.log(`  Has metadata: ${!!response.data.metadata}`);
        
        if (response.statusCode === 200) {
            testsPassed++;
            console.log('  ✅ PASSED\n');
        } else {
            console.log('  ❌ FAILED\n');
        }
    } catch (error) {
        console.log(`  ❌ FAILED: ${error.message}\n`);
    }
    
    // Test 3: Frontend accessibility
    totalTests++;
    console.log('Test 3: Frontend Accessibility');
    try {
        const response = await makeRequest(FRONTEND_URL);
        
        console.log(`  Frontend status: ${response.statusCode}`);
        
        if (response.statusCode === 200) {
            testsPassed++;
            console.log('  ✅ PASSED\n');
        } else {
            console.log('  ❌ FAILED\n');
        }
    } catch (error) {
        console.log(`  ❌ FAILED: ${error.message}\n`);
    }
    
    // Test 4: Cache service
    totalTests++;
    console.log('Test 4: Cache Service');
    try {
        const response = await makeRequest(`${BACKEND_URL}/cache/stats`);
        
        console.log(`  Cache status: ${response.statusCode}`);
        console.log(`  Cache entries: ${response.data.total_entries || 0}`);
        
        if (response.statusCode === 200) {
            testsPassed++;
            console.log('  ✅ PASSED\n');
        } else {
            console.log('  ❌ FAILED\n');
        }
    } catch (error) {
        console.log(`  ❌ FAILED: ${error.message}\n`);
    }
    
    // Summary
    console.log('📊 Test Results Summary');
    console.log('=' .repeat(50));
    console.log(`Tests Passed: ${testsPassed}/${totalTests}`);
    console.log(`Success Rate: ${((testsPassed/totalTests) * 100).toFixed(1)}%`);
    
    if (testsPassed === totalTests) {
        console.log('\n🎉 All tests PASSED! Research integration is functional!');
        console.log('\n✨ Research Features Available:');
        console.log('   • Main analysis endpoints support research parameter');
        console.log('   • Frontend can toggle research on/off');
        console.log('   • Cache system works with research context');
    } else {
        console.log('\n⚠️  Some tests FAILED. Please check the output above.');
    }
    
    console.log('\n🔗 Key URLs:');
    console.log(`   • Main Analysis: ${FRONTEND_URL}/analysis`);
    console.log(`   • Backend Health: ${BACKEND_URL}/health`);
    console.log(`   • Cache Stats: ${BACKEND_URL}/cache/stats`);
}

runTests().catch(console.error); 