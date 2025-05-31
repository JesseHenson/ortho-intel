#!/usr/bin/env python3
"""
Test suite for streaming models.

Tests all streaming event models, validation, and serialization
to ensure robust real-time communication.

Following backend organization guidelines in src/backend/tests/
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add project root to path for proper imports
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)

from src.backend.core.streaming_models import (
    StreamingEventType,
    StreamingStatus,
    BaseStreamingEvent,
    AnalysisStartedEvent,
    NodeExecutionEvent,
    SearchProgressEvent,
    SourceDiscoveryEvent,
    InsightDiscoveryEvent,
    OpportunityGeneratedEvent,
    ProgressUpdateEvent,
    AnalysisCompletedEvent,
    ErrorEvent,
    StreamingResponse,
    StreamingSession,
    StreamingMetrics,
    StreamingConfig
)

class TestStreamingModels(unittest.TestCase):
    """Test streaming models validation and functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_timestamp = datetime.now()
        self.test_session_id = "test_session_123"
    
    def test_base_streaming_event_creation(self):
        """Test base streaming event model creation"""
        print("🧪 Testing BaseStreamingEvent creation...")
        
        event = BaseStreamingEvent(
            message="Test progress update",
            progress_percentage=50.0
        )
        
        self.assertEqual(event.message, "Test progress update")
        self.assertEqual(event.progress_percentage, 50.0)
        self.assertEqual(event.status, StreamingStatus.INFO)  # Default
        self.assertIsInstance(event.timestamp, datetime)
    
    def test_analysis_started_event(self):
        """Test analysis started event model"""
        print("🧪 Testing AnalysisStartedEvent...")
        
        event = AnalysisStartedEvent(
            message="Analysis started for spine devices",
            competitors=["Stryker Spine", "Zimmer Biomet"],
            focus_area="spine_fusion",
            device_category="spinal_devices",
            estimated_duration=120
        )
        
        self.assertEqual(event.event_type, StreamingEventType.ANALYSIS_STARTED)
        self.assertEqual(len(event.competitors), 2)
        self.assertEqual(event.focus_area, "spine_fusion")
        self.assertEqual(event.estimated_duration, 120)
    
    def test_node_execution_event(self):
        """Test LangGraph node execution event"""
        print("🧪 Testing NodeExecutionEvent...")
        
        event = NodeExecutionEvent(
            message="Starting competitor research",
            node_name="research_competitor",
            node_description="Research competitor information and strategies",
            execution_order=1,
            input_summary="Processing Stryker Spine analysis"
        )
        
        self.assertEqual(event.event_type, StreamingEventType.NODE_STARTED)
        self.assertEqual(event.node_name, "research_competitor")
        self.assertEqual(event.execution_order, 1)
        self.assertIsNotNone(event.input_summary)
    
    def test_source_discovery_event(self):
        """Test source discovery event model"""
        print("🧪 Testing SourceDiscoveryEvent...")
        
        event = SourceDiscoveryEvent(
            message="Found relevant medical device source",
            source_url="https://example.com/stryker-spine-report",
            source_title="Stryker Spine Market Analysis 2024",
            source_domain="example.com",
            credibility_score=8.5,
            relevance_score=9.2,
            content_snippet="Stryker's spine division shows strong growth..."
        )
        
        self.assertEqual(event.event_type, StreamingEventType.SOURCE_FOUND)
        self.assertEqual(event.credibility_score, 8.5)
        self.assertEqual(event.relevance_score, 9.2)
        self.assertTrue(event.content_snippet.startswith("Stryker's"))
    
    def test_opportunity_generated_event(self):
        """Test opportunity generation event"""
        print("🧪 Testing OpportunityGeneratedEvent...")
        
        event = OpportunityGeneratedEvent(
            message="Strategic opportunity identified",
            opportunity_title="Market Expansion in Minimally Invasive Surgery",
            opportunity_category="Market Expansion",
            opportunity_score=8.7,
            implementation_difficulty="Medium",
            time_to_market="6-12 months"
        )
        
        self.assertEqual(event.event_type, StreamingEventType.OPPORTUNITY_GENERATED)
        self.assertEqual(event.opportunity_score, 8.7)
        self.assertEqual(event.implementation_difficulty, "Medium")
    
    def test_error_event_handling(self):
        """Test error event model"""
        print("🧪 Testing ErrorEvent handling...")
        
        event = ErrorEvent(
            message="API rate limit exceeded",
            error_type="RateLimitError",
            error_details="Tavily API returned 429 status",
            recovery_suggestion="Wait 60 seconds before retrying",
            is_recoverable=True
        )
        
        self.assertEqual(event.event_type, StreamingEventType.ANALYSIS_ERROR)
        self.assertEqual(event.status, StreamingStatus.ERROR)
        self.assertTrue(event.is_recoverable)
        self.assertIsNotNone(event.recovery_suggestion)
    
    def test_streaming_response_container(self):
        """Test streaming response container"""
        print("🧪 Testing StreamingResponse container...")
        
        # Use a concrete event type instead of BaseStreamingEvent
        progress_event = ProgressUpdateEvent(
            message="Test message",
            current_step="Testing streaming response",
            completed_steps=["Step 1", "Step 2"],
            remaining_steps=["Step 3", "Step 4"],
            progress_percentage=50.0
        )
        
        response = StreamingResponse(
            event=progress_event,
            session_id=self.test_session_id,
            sequence_number=42
        )
        
        self.assertEqual(response.session_id, self.test_session_id)
        self.assertEqual(response.sequence_number, 42)
        self.assertEqual(response.event.message, "Test message")
        self.assertEqual(response.event.event_type, StreamingEventType.PROGRESS_UPDATE)
    
    def test_streaming_session_management(self):
        """Test streaming session model"""
        print("🧪 Testing StreamingSession management...")
        
        session = StreamingSession(
            session_id=self.test_session_id,
            client_info={"user_agent": "test_client", "ip": "127.0.0.1"},
            analysis_config={"competitors": ["Stryker"], "focus": "spine"}
        )
        
        self.assertEqual(session.session_id, self.test_session_id)
        self.assertTrue(session.is_active)
        self.assertEqual(session.events_sent, 0)
        self.assertIsInstance(session.started_at, datetime)
    
    def test_streaming_metrics(self):
        """Test streaming metrics model"""
        print("🧪 Testing StreamingMetrics...")
        
        metrics = StreamingMetrics(
            session_id=self.test_session_id,
            events_sent=150,
            events_per_second=2.5,
            connection_duration=60.0,
            bytes_sent=8192,
            client_disconnections=1,
            errors_encountered=0
        )
        
        self.assertEqual(metrics.events_sent, 150)
        self.assertEqual(metrics.events_per_second, 2.5)
        self.assertEqual(metrics.client_disconnections, 1)
    
    def test_streaming_config_defaults(self):
        """Test streaming configuration with defaults"""
        print("🧪 Testing StreamingConfig defaults...")
        
        config = StreamingConfig()
        
        self.assertEqual(config.max_events_per_second, 10)
        self.assertEqual(config.batch_size, 5)
        self.assertEqual(config.heartbeat_interval, 30)
        self.assertEqual(config.max_session_duration, 3600)
        self.assertFalse(config.batch_events)
    
    def test_event_type_enumeration(self):
        """Test streaming event type enum"""
        print("🧪 Testing StreamingEventType enumeration...")
        
        # Test all event types are accessible
        self.assertEqual(StreamingEventType.ANALYSIS_STARTED, "analysis_started")
        self.assertEqual(StreamingEventType.SOURCE_FOUND, "source_found")
        self.assertEqual(StreamingEventType.OPPORTUNITY_GENERATED, "opportunity_generated")
        self.assertEqual(StreamingEventType.ANALYSIS_COMPLETED, "analysis_completed")
        
        # Test all event types exist
        expected_types = [
            "analysis_started", "analysis_completed", "analysis_error",
            "node_started", "node_completed", "node_error",
            "search_started", "source_found", "source_analyzed", "search_completed",
            "gap_identified", "opportunity_generated", "insight_discovered",
            "progress_update", "status_update"
        ]
        
        actual_types = [event_type.value for event_type in StreamingEventType]
        for expected_type in expected_types:
            self.assertIn(expected_type, actual_types)
    
    def test_event_serialization(self):
        """Test event model serialization/deserialization"""
        print("🧪 Testing event serialization...")
        
        # Create a complex event
        event = AnalysisStartedEvent(
            message="Starting comprehensive analysis",
            competitors=["Stryker Spine", "Zimmer Biomet", "Orthofix"],
            focus_area="cervical_spine",
            device_category="spinal_devices",
            estimated_duration=180,
            progress_percentage=0.0
        )
        
        # Test serialization
        event_dict = event.model_dump()
        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict["event_type"], "analysis_started")
        self.assertEqual(len(event_dict["competitors"]), 3)
        
        # Test deserialization
        recreated_event = AnalysisStartedEvent(**event_dict)
        self.assertEqual(recreated_event.message, event.message)
        self.assertEqual(recreated_event.competitors, event.competitors)
    
    def test_progress_percentage_validation(self):
        """Test progress percentage validation"""
        print("🧪 Testing progress percentage validation...")
        
        # Valid progress percentages
        valid_event = BaseStreamingEvent(
            message="Test",
            progress_percentage=50.0
        )
        self.assertEqual(valid_event.progress_percentage, 50.0)
        
        # None should be allowed
        none_event = BaseStreamingEvent(
            message="Test",
            progress_percentage=None
        )
        self.assertIsNone(none_event.progress_percentage)
        
        # Edge cases (0 and 100)
        zero_event = BaseStreamingEvent(
            message="Starting",
            progress_percentage=0.0
        )
        self.assertEqual(zero_event.progress_percentage, 0.0)
        
        complete_event = BaseStreamingEvent(
            message="Complete",
            progress_percentage=100.0
        )
        self.assertEqual(complete_event.progress_percentage, 100.0)

if __name__ == "__main__":
    unittest.main() 