#!/usr/bin/env python3
"""
Test suite for streaming connection management.

Tests WebSocket connection handling, error recovery, rate limiting,
and graceful degradation functionality.

Following backend organization guidelines in src/backend/tests/
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Add project root to path for proper imports
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)

from src.backend.utils.streaming_connection import (
    ConnectionManager, ConnectionState, DisconnectionReason,
    ConnectionMetrics, get_connection_manager, managed_connection
)
from src.backend.core.streaming_models import (
    StreamingConfig, ProgressUpdateEvent, ErrorEvent, StreamingStatus
)


class TestConnectionMetrics:
    """Test connection metrics tracking"""
    
    def test_metrics_initialization(self):
        """Test metrics initialization with defaults"""
        metrics = ConnectionMetrics(session_id="test_session")
        
        assert metrics.session_id == "test_session"
        assert metrics.messages_sent == 0
        assert metrics.messages_received == 0
        assert metrics.reconnection_attempts == 0
        assert metrics.total_disconnections == 0
        assert metrics.bytes_sent == 0
        assert metrics.bytes_received == 0
        assert isinstance(metrics.connected_at, datetime)
        assert isinstance(metrics.last_activity, datetime)
    
    def test_message_tracking(self):
        """Test message sent/received tracking"""
        metrics = ConnectionMetrics(session_id="test_session")
        
        # Test message sent
        initial_activity = metrics.last_activity
        metrics.record_message_sent(100)
        
        assert metrics.messages_sent == 1
        assert metrics.bytes_sent == 100
        assert metrics.last_activity > initial_activity
        
        # Test message received
        metrics.record_message_received(150)
        
        assert metrics.messages_received == 1
        assert metrics.bytes_received == 150


class TestConnectionManager:
    """Test ConnectionManager functionality"""
    
    @pytest.fixture
    def config(self):
        """Create test streaming config"""
        return StreamingConfig(
            max_events_per_second=5,
            heartbeat_interval=1,
            max_session_duration=10,
            buffer_size=50
        )
    
    @pytest.fixture
    def manager(self, config):
        """Create ConnectionManager instance"""
        return ConnectionManager(config)
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket"""
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        websocket.close = AsyncMock()
        websocket.ping = AsyncMock()
        return websocket
    
    @pytest.mark.asyncio
    async def test_connection_establishment(self, manager, mock_websocket):
        """Test successful WebSocket connection establishment"""
        session_id = "test_session_001"
        client_info = {"user_agent": "test_client", "ip": "127.0.0.1"}
        
        # Test connection
        success = await manager.connect(mock_websocket, session_id, client_info)
        
        assert success is True
        assert session_id in manager.active_connections
        assert session_id in manager.connection_metrics
        assert session_id in manager.sessions
        assert manager.connection_states[session_id] == ConnectionState.CONNECTED
        
        # Verify WebSocket accept was called
        mock_websocket.accept.assert_called_once()
        
        # Verify session creation
        session = manager.sessions[session_id]
        assert session.session_id == session_id
        assert session.client_info == client_info
        assert session.is_active is True
        
        # Cleanup
        await manager.disconnect(session_id)
    
    @pytest.mark.asyncio
    async def test_connection_failure(self, manager):
        """Test WebSocket connection failure handling"""
        session_id = "test_session_002"
        
        # Create mock WebSocket that fails to accept
        mock_websocket = AsyncMock()
        mock_websocket.accept.side_effect = Exception("Connection failed")
        
        success = await manager.connect(mock_websocket, session_id)
        
        assert success is False
        assert session_id not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_graceful_disconnection(self, manager, mock_websocket):
        """Test graceful WebSocket disconnection"""
        session_id = "test_session_003"
        
        # Establish connection
        await manager.connect(mock_websocket, session_id)
        
        # Test disconnect
        await manager.disconnect(session_id, DisconnectionReason.GRACEFUL_SHUTDOWN)
        
        assert session_id not in manager.active_connections
        assert manager.connection_states[session_id] == ConnectionState.DISCONNECTED
        
        # Verify WebSocket close was called
        mock_websocket.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_event_sending(self, manager, mock_websocket):
        """Test sending events to connected sessions"""
        session_id = "test_session_004"
        
        # Establish connection
        await manager.connect(mock_websocket, session_id)
        
        # Create test event
        event = ProgressUpdateEvent(
            message="Test progress update",
            current_step="Testing",
            completed_steps=["Setup"],
            remaining_steps=["Verification", "Cleanup"],
            progress_percentage=50.0
        )
        
        # Send event
        success = await manager.send_event(session_id, event)
        
        assert success is True
        
        # Verify WebSocket send was called
        mock_websocket.send_text.assert_called_once()
        
        # Verify metrics were updated
        metrics = manager.get_connection_metrics(session_id)
        assert metrics.messages_sent == 1
        assert metrics.bytes_sent > 0
        
        # Cleanup
        await manager.disconnect(session_id)
    
    @pytest.mark.asyncio
    async def test_event_sending_to_disconnected_session(self, manager):
        """Test sending events to disconnected sessions"""
        session_id = "nonexistent_session"
        
        event = ProgressUpdateEvent(
            message="Test message",
            current_step="Testing",
            completed_steps=[],
            remaining_steps=[]
        )
        
        success = await manager.send_event(session_id, event)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_broadcast_event(self, manager, mock_websocket):
        """Test broadcasting events to multiple sessions"""
        session_ids = ["session_1", "session_2", "session_3"]
        mock_websockets = []
        
        # Establish multiple connections
        for session_id in session_ids:
            websocket = AsyncMock()
            websocket.accept = AsyncMock()
            websocket.send_text = AsyncMock()
            websocket.close = AsyncMock()
            mock_websockets.append(websocket)
            
            await manager.connect(websocket, session_id)
        
        # Create test event
        event = ProgressUpdateEvent(
            message="Broadcast test",
            current_step="Broadcasting",
            completed_steps=[],
            remaining_steps=[]
        )
        
        # Broadcast event
        successful_sends = await manager.broadcast_event(event)
        
        assert successful_sends == 3
        
        # Verify all WebSockets received the message
        for websocket in mock_websockets:
            websocket.send_text.assert_called_once()
        
        # Cleanup
        for session_id in session_ids:
            await manager.disconnect(session_id)
    
    @pytest.mark.asyncio
    async def test_broadcast_with_exclusions(self, manager):
        """Test broadcasting with session exclusions"""
        session_ids = ["session_1", "session_2", "session_3"]
        mock_websockets = []
        
        # Establish multiple connections
        for session_id in session_ids:
            websocket = AsyncMock()
            websocket.accept = AsyncMock()
            websocket.send_text = AsyncMock()
            websocket.close = AsyncMock()
            mock_websockets.append(websocket)
            
            await manager.connect(websocket, session_id)
        
        # Create test event
        event = ProgressUpdateEvent(
            message="Selective broadcast",
            current_step="Testing exclusions",
            completed_steps=[],
            remaining_steps=[]
        )
        
        # Broadcast event excluding session_2
        successful_sends = await manager.broadcast_event(
            event, 
            exclude_sessions={"session_2"}
        )
        
        assert successful_sends == 2
        
        # Verify only non-excluded sessions received the message
        mock_websockets[0].send_text.assert_called_once()  # session_1
        mock_websockets[1].send_text.assert_not_called()   # session_2 (excluded)
        mock_websockets[2].send_text.assert_called_once()  # session_3
        
        # Cleanup
        for session_id in session_ids:
            await manager.disconnect(session_id)
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, manager, mock_websocket):
        """Test rate limiting functionality"""
        session_id = "test_session_rate_limit"
        
        # Use a config with very low rate limit for testing
        test_config = StreamingConfig(max_events_per_second=2)
        manager.config = test_config
        
        # Establish connection
        await manager.connect(mock_websocket, session_id)
        
        # Reset rate limiter with low limit
        manager.rate_limiters[session_id] = asyncio.Semaphore(1)
        
        # Create test event
        event = ProgressUpdateEvent(
            message="Rate limit test",
            current_step="Testing limits",
            completed_steps=[],
            remaining_steps=[]
        )
        
        # Send first event (should succeed)
        success1 = await manager.send_event(session_id, event)
        assert success1 is True
        
        # Send second event immediately (should be rate limited)
        # Mock the rate limiter to timeout
        manager.rate_limiters[session_id] = AsyncMock()
        manager.rate_limiters[session_id].acquire.side_effect = asyncio.TimeoutError()
        
        success2 = await manager.send_event(session_id, event)
        assert success2 is False
        
        # Cleanup
        await manager.disconnect(session_id)
    
    @pytest.mark.asyncio
    async def test_connection_state_tracking(self, manager, mock_websocket):
        """Test connection state changes"""
        session_id = "test_session_states"
        
        # Initial state should not exist
        assert session_id not in manager.connection_states
        
        # Connect
        await manager.connect(mock_websocket, session_id)
        assert manager.connection_states[session_id] == ConnectionState.CONNECTED
        
        # Disconnect
        await manager.disconnect(session_id)
        assert manager.connection_states[session_id] == ConnectionState.DISCONNECTED
    
    @pytest.mark.asyncio 
    async def test_connection_metrics_tracking(self, manager, mock_websocket):
        """Test connection metrics are properly tracked"""
        session_id = "test_session_metrics"
        
        # Establish connection
        await manager.connect(mock_websocket, session_id)
        
        # Get initial metrics
        metrics = manager.get_connection_metrics(session_id)
        assert metrics is not None
        assert metrics.session_id == session_id
        assert metrics.messages_sent == 0
        
        # Send an event and verify metrics update
        event = ProgressUpdateEvent(
            message="Metrics test",
            current_step="Testing metrics",
            completed_steps=[],
            remaining_steps=[]
        )
        
        await manager.send_event(session_id, event)
        
        # Check updated metrics
        updated_metrics = manager.get_connection_metrics(session_id)
        assert updated_metrics.messages_sent == 1
        assert updated_metrics.bytes_sent > 0
        
        # Cleanup
        await manager.disconnect(session_id)
    
    @pytest.mark.asyncio
    async def test_session_management(self, manager, mock_websocket):
        """Test session creation and management"""
        session_id = "test_session_management"
        client_info = {"browser": "test", "version": "1.0"}
        
        # Establish connection
        await manager.connect(mock_websocket, session_id, client_info)
        
        # Verify session creation
        session = manager.sessions[session_id]
        assert session.session_id == session_id
        assert session.client_info == client_info
        assert session.is_active is True
        assert session.events_sent == 0
        
        # Send event and verify session update
        event = ProgressUpdateEvent(
            message="Session test",
            current_step="Testing sessions",
            completed_steps=[],
            remaining_steps=[]
        )
        
        await manager.send_event(session_id, event)
        
        # Verify session events counter updated
        assert manager.sessions[session_id].events_sent == 1
        
        # Cleanup
        await manager.disconnect(session_id)
    
    @pytest.mark.asyncio
    async def test_manager_shutdown(self, manager):
        """Test graceful manager shutdown"""
        session_ids = ["shutdown_test_1", "shutdown_test_2"]
        
        # Establish multiple connections
        for session_id in session_ids:
            websocket = AsyncMock()
            websocket.accept = AsyncMock()
            websocket.close = AsyncMock()
            await manager.connect(websocket, session_id)
        
        # Verify connections are active
        assert len(manager.active_connections) == 2
        
        # Shutdown manager
        await manager.shutdown()
        
        # Verify all connections were closed
        assert len(manager.active_connections) == 0
        
        # Verify all connection states are disconnected
        for session_id in session_ids:
            assert manager.connection_states[session_id] == ConnectionState.DISCONNECTED


class TestManagedConnection:
    """Test managed connection context manager"""
    
    @pytest.mark.asyncio
    async def test_managed_connection_success(self):
        """Test successful managed connection lifecycle"""
        session_id = "managed_test_001"
        
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        # Test context manager
        async with managed_connection(mock_websocket, session_id) as manager:
            assert isinstance(manager, ConnectionManager)
            assert manager.is_connected(session_id)
        
        # Connection should be cleaned up after context
        # Note: We can't easily test this with the global manager
        # In a real scenario, we'd need dependency injection
    
    @pytest.mark.asyncio
    async def test_managed_connection_failure(self):
        """Test managed connection with connection failure"""
        session_id = "managed_test_002"
        
        mock_websocket = AsyncMock()
        mock_websocket.accept.side_effect = Exception("Connection failed")
        
        # Test that context manager raises appropriate error
        with pytest.raises(ConnectionError):
            async with managed_connection(mock_websocket, session_id) as manager:
                pass


class TestConnectionManagerIntegration:
    """Integration tests for connection manager"""
    
    @pytest.mark.asyncio
    async def test_full_connection_lifecycle(self):
        """Test complete connection lifecycle with real events"""
        config = StreamingConfig(
            max_events_per_second=10,
            heartbeat_interval=5,
            max_session_duration=30
        )
        manager = ConnectionManager(config)
        
        session_id = "integration_test_001"
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        try:
            # 1. Connect
            success = await manager.connect(mock_websocket, session_id)
            assert success is True
            
            # 2. Send multiple events
            events = [
                ProgressUpdateEvent(
                    message=f"Step {i}",
                    current_step=f"Processing step {i}",
                    completed_steps=[f"Step {j}" for j in range(i)],
                    remaining_steps=[f"Step {j}" for j in range(i+1, 5)],
                    progress_percentage=i * 20.0
                ) for i in range(1, 5)
            ]
            
            for event in events:
                success = await manager.send_event(session_id, event)
                assert success is True
            
            # 3. Verify metrics
            metrics = manager.get_connection_metrics(session_id)
            assert metrics.messages_sent == 4
            assert metrics.bytes_sent > 0
            
            # 4. Test error event
            error_event = ErrorEvent(
                message="Test error",
                error_type="TestError",
                error_details="This is a test error",
                is_recoverable=True
            )
            
            success = await manager.send_event(session_id, error_event)
            assert success is True
            
            # 5. Verify final metrics
            final_metrics = manager.get_connection_metrics(session_id)
            assert final_metrics.messages_sent == 5
            
        finally:
            # 6. Cleanup
            await manager.disconnect(session_id)
            assert session_id not in manager.active_connections


if __name__ == "__main__":
    # Run with pytest for proper async support
    pytest.main([__file__, "-v"]) 