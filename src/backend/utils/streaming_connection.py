#!/usr/bin/env python3
"""
Streaming Connection Management Utilities

Provides robust connection handling, error recovery, and graceful degradation
for real-time streaming analysis functionality.

Following backend organization guidelines in src/backend/utils/
"""

import asyncio
import logging
from typing import Dict, Set, Optional, Callable, Any, AsyncGenerator, List
from datetime import datetime, timedelta
import json
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..core.streaming_models import (
    StreamingEvent, StreamingResponse, StreamingSession, 
    StreamingMetrics, StreamingConfig, ErrorEvent, StreamingStatus
)

logger = logging.getLogger(__name__)

class ConnectionState(str, Enum):
    """WebSocket connection states"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RECONNECTING = "reconnecting"

class DisconnectionReason(str, Enum):
    """Reasons for connection disconnection"""
    CLIENT_DISCONNECT = "client_disconnect"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    NETWORK_ERROR = "network_error"
    GRACEFUL_SHUTDOWN = "graceful_shutdown"

@dataclass
class ConnectionMetrics:
    """Connection-specific metrics tracking"""
    session_id: str
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    messages_sent: int = 0
    messages_received: int = 0
    reconnection_attempts: int = 0
    total_disconnections: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def record_message_sent(self, message_size: int = 0):
        """Record a sent message"""
        self.messages_sent += 1
        self.bytes_sent += message_size
        self.update_activity()
    
    def record_message_received(self, message_size: int = 0):
        """Record a received message"""
        self.messages_received += 1
        self.bytes_received += message_size
        self.update_activity()

class ConnectionManager:
    """
    Manages WebSocket connections for real-time streaming.
    
    Provides connection pooling, error recovery, rate limiting,
    and graceful degradation capabilities.
    """
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metrics: Dict[str, ConnectionMetrics] = {}
        self.connection_states: Dict[str, ConnectionState] = {}
        self.sessions: Dict[str, StreamingSession] = {}
        
        # Rate limiting
        self.rate_limiters: Dict[str, asyncio.Semaphore] = {}
        
        # Connection monitoring
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
        self.cleanup_tasks: Set[asyncio.Task] = set()
        
        # Event handlers
        self.on_connect_handlers: List[Callable] = []
        self.on_disconnect_handlers: List[Callable] = []
        self.on_error_handlers: List[Callable] = []
    
    async def connect(self, websocket: WebSocket, session_id: str, client_info: Dict[str, Any] = None) -> bool:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            session_id: Unique session identifier
            client_info: Optional client information
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            await websocket.accept()
            
            # Register connection
            self.active_connections[session_id] = websocket
            self.connection_states[session_id] = ConnectionState.CONNECTED
            self.connection_metrics[session_id] = ConnectionMetrics(session_id=session_id)
            
            # Create session
            session = StreamingSession(
                session_id=session_id,
                client_info=client_info or {},
                analysis_config={}
            )
            self.sessions[session_id] = session
            
            # Set up rate limiting
            self.rate_limiters[session_id] = asyncio.Semaphore(self.config.max_events_per_second)
            
            # Start heartbeat monitoring
            if self.config.heartbeat_interval > 0:
                self.heartbeat_tasks[session_id] = asyncio.create_task(
                    self._heartbeat_monitor(session_id)
                )
            
            # Schedule session cleanup
            cleanup_task = asyncio.create_task(
                self._schedule_session_cleanup(session_id)
            )
            self.cleanup_tasks.add(cleanup_task)
            
            logger.info(f"WebSocket connection established for session {session_id}")
            
            # Call connect handlers
            for handler in self.on_connect_handlers:
                try:
                    await handler(session_id, websocket)
                except Exception as e:
                    logger.warning(f"Connect handler error: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket for session {session_id}: {e}")
            await self._handle_connection_error(session_id, str(e))
            return False
    
    async def disconnect(self, session_id: str, reason: DisconnectionReason = DisconnectionReason.GRACEFUL_SHUTDOWN):
        """
        Gracefully disconnect a WebSocket connection.
        
        Args:
            session_id: Session to disconnect
            reason: Reason for disconnection
        """
        if session_id not in self.active_connections:
            logger.warning(f"Attempted to disconnect non-existent session {session_id}")
            return
        
        try:
            self.connection_states[session_id] = ConnectionState.DISCONNECTING
            
            websocket = self.active_connections[session_id]
            
            # Send disconnect notification if possible
            if reason != DisconnectionReason.CLIENT_DISCONNECT:
                try:
                    disconnect_event = ErrorEvent(
                        message=f"Connection closing: {reason.value}",
                        error_type="ConnectionClosed",
                        error_details=f"Server initiated disconnect due to: {reason.value}",
                        is_recoverable=(reason in [DisconnectionReason.TIMEOUT, DisconnectionReason.NETWORK_ERROR])
                    )
                    
                    await self._send_event_to_connection(session_id, disconnect_event)
                    await asyncio.sleep(0.1)  # Brief delay for message delivery
                    
                except Exception as e:
                    logger.debug(f"Could not send disconnect notification to {session_id}: {e}")
            
            # Close WebSocket
            try:
                await websocket.close()
            except Exception as e:
                logger.debug(f"Error closing WebSocket for {session_id}: {e}")
            
            # Update metrics
            if session_id in self.connection_metrics:
                self.connection_metrics[session_id].total_disconnections += 1
            
            logger.info(f"WebSocket disconnected for session {session_id}, reason: {reason.value}")
            
            # Call disconnect handlers
            for handler in self.on_disconnect_handlers:
                try:
                    await handler(session_id, reason)
                except Exception as e:
                    logger.warning(f"Disconnect handler error: {e}")
                    
        except Exception as e:
            logger.error(f"Error during disconnect for session {session_id}: {e}")
        finally:
            await self._cleanup_session(session_id)
    
    async def send_event(self, session_id: str, event: StreamingEvent) -> bool:
        """
        Send a streaming event to a specific session with rate limiting.
        
        Args:
            session_id: Target session
            event: Event to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if session_id not in self.active_connections:
            logger.debug(f"Cannot send event to disconnected session {session_id}")
            return False
        
        # Apply rate limiting
        if session_id in self.rate_limiters:
            try:
                async with asyncio.timeout(1.0):  # 1 second timeout for rate limit
                    await self.rate_limiters[session_id].acquire()
            except asyncio.TimeoutError:
                logger.warning(f"Rate limit timeout for session {session_id}")
                return False
        
        return await self._send_event_to_connection(session_id, event)
    
    async def broadcast_event(self, event: StreamingEvent, exclude_sessions: Set[str] = None) -> int:
        """
        Broadcast an event to all active connections.
        
        Args:
            event: Event to broadcast
            exclude_sessions: Sessions to exclude from broadcast
            
        Returns:
            int: Number of successful sends
        """
        exclude_sessions = exclude_sessions or set()
        successful_sends = 0
        
        # Create broadcast tasks for all active sessions
        tasks = []
        for session_id in list(self.active_connections.keys()):
            if session_id not in exclude_sessions:
                task = asyncio.create_task(self.send_event(session_id, event))
                tasks.append((session_id, task))
        
        # Wait for all sends to complete
        for session_id, task in tasks:
            try:
                success = await task
                if success:
                    successful_sends += 1
                else:
                    logger.debug(f"Failed to broadcast to session {session_id}")
            except Exception as e:
                logger.warning(f"Broadcast error for session {session_id}: {e}")
        
        return successful_sends
    
    async def _send_event_to_connection(self, session_id: str, event: StreamingEvent) -> bool:
        """Send event to a specific connection"""
        try:
            websocket = self.active_connections[session_id]
            
            # Create response container
            sequence_number = self.sessions[session_id].events_sent + 1
            response = StreamingResponse(
                event=event,
                session_id=session_id,
                sequence_number=sequence_number
            )
            
            # Serialize and send
            message = response.model_dump_json()
            await websocket.send_text(message)
            
            # Update metrics
            self.connection_metrics[session_id].record_message_sent(len(message))
            self.sessions[session_id].events_sent = sequence_number
            self.sessions[session_id].last_activity = datetime.now()
            
            return True
            
        except WebSocketDisconnect:
            logger.info(f"Client disconnected during send: {session_id}")
            await self.disconnect(session_id, DisconnectionReason.CLIENT_DISCONNECT)
            return False
        except Exception as e:
            logger.error(f"Error sending event to {session_id}: {e}")
            await self._handle_connection_error(session_id, str(e))
            return False
    
    async def _heartbeat_monitor(self, session_id: str):
        """Monitor connection health with heartbeat"""
        try:
            while session_id in self.active_connections:
                await asyncio.sleep(self.config.heartbeat_interval)
                
                if session_id not in self.active_connections:
                    break
                
                # Check if connection is stale
                metrics = self.connection_metrics.get(session_id)
                if metrics:
                    time_since_activity = datetime.now() - metrics.last_activity
                    if time_since_activity > timedelta(seconds=self.config.heartbeat_interval * 3):
                        logger.info(f"Session {session_id} appears stale, disconnecting")
                        await self.disconnect(session_id, DisconnectionReason.TIMEOUT)
                        break
                
                # Send heartbeat (could be implemented as a ping/pong)
                try:
                    websocket = self.active_connections[session_id]
                    await websocket.ping()
                except Exception as e:
                    logger.info(f"Heartbeat failed for {session_id}: {e}")
                    await self.disconnect(session_id, DisconnectionReason.NETWORK_ERROR)
                    break
                    
        except asyncio.CancelledError:
            logger.debug(f"Heartbeat monitor cancelled for {session_id}")
        except Exception as e:
            logger.error(f"Heartbeat monitor error for {session_id}: {e}")
    
    async def _schedule_session_cleanup(self, session_id: str):
        """Schedule automatic session cleanup after max duration"""
        try:
            await asyncio.sleep(self.config.max_session_duration)
            
            if session_id in self.active_connections:
                logger.info(f"Session {session_id} exceeded max duration, disconnecting")
                await self.disconnect(session_id, DisconnectionReason.TIMEOUT)
                
        except asyncio.CancelledError:
            logger.debug(f"Session cleanup cancelled for {session_id}")
    
    async def _handle_connection_error(self, session_id: str, error_message: str):
        """Handle connection errors"""
        logger.error(f"Connection error for {session_id}: {error_message}")
        
        self.connection_states[session_id] = ConnectionState.ERROR
        
        # Call error handlers
        for handler in self.on_error_handlers:
            try:
                await handler(session_id, error_message)
            except Exception as e:
                logger.warning(f"Error handler failed: {e}")
        
        # Attempt graceful cleanup
        await self._cleanup_session(session_id)
    
    async def _cleanup_session(self, session_id: str):
        """Clean up session resources"""
        try:
            # Remove from active connections
            self.active_connections.pop(session_id, None)
            
            # Update connection state
            self.connection_states[session_id] = ConnectionState.DISCONNECTED
            
            # Cancel heartbeat monitoring
            if session_id in self.heartbeat_tasks:
                task = self.heartbeat_tasks.pop(session_id)
                if not task.done():
                    task.cancel()
            
            # Clean up rate limiter
            self.rate_limiters.pop(session_id, None)
            
            # Keep metrics and session data for potential reconnection
            # (They can be cleaned up later by a background task)
            
        except Exception as e:
            logger.error(f"Error during session cleanup for {session_id}: {e}")
    
    def get_connection_metrics(self, session_id: str) -> Optional[ConnectionMetrics]:
        """Get connection metrics for a session"""
        return self.connection_metrics.get(session_id)
    
    def get_all_metrics(self) -> Dict[str, ConnectionMetrics]:
        """Get all connection metrics"""
        return self.connection_metrics.copy()
    
    def get_active_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self.active_connections)
    
    def is_connected(self, session_id: str) -> bool:
        """Check if a session is currently connected"""
        return session_id in self.active_connections
    
    async def shutdown(self):
        """Gracefully shutdown all connections"""
        logger.info("Shutting down connection manager")
        
        # Disconnect all active connections
        disconnect_tasks = []
        for session_id in list(self.active_connections.keys()):
            task = asyncio.create_task(
                self.disconnect(session_id, DisconnectionReason.GRACEFUL_SHUTDOWN)
            )
            disconnect_tasks.append(task)
        
        # Wait for all disconnections
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        # Cancel any remaining cleanup tasks
        for task in self.cleanup_tasks:
            if not task.done():
                task.cancel()
        
        logger.info("Connection manager shutdown complete")

# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None

def get_connection_manager(config: StreamingConfig = None) -> ConnectionManager:
    """Get or create the global connection manager instance"""
    global _connection_manager
    
    if _connection_manager is None:
        if config is None:
            config = StreamingConfig()
        _connection_manager = ConnectionManager(config)
    
    return _connection_manager

@asynccontextmanager
async def managed_connection(websocket: WebSocket, session_id: str, client_info: Dict[str, Any] = None):
    """
    Context manager for WebSocket connections with automatic cleanup.
    
    Usage:
        async with managed_connection(websocket, session_id) as manager:
            # Connection is established
            await manager.send_event(session_id, some_event)
        # Connection is automatically cleaned up
    """
    manager = get_connection_manager()
    
    try:
        success = await manager.connect(websocket, session_id, client_info)
        if not success:
            raise ConnectionError(f"Failed to establish connection for session {session_id}")
        
        yield manager
        
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"Connection error for {session_id}: {e}")
        raise
    finally:
        await manager.disconnect(session_id, DisconnectionReason.GRACEFUL_SHUTDOWN) 