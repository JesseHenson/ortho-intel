#!/usr/bin/env python3
"""
Streaming Fallback and Graceful Degradation Utilities

Provides client-side fallback mechanisms when real-time streaming fails
or is unavailable, ensuring the application remains functional.

Following backend organization guidelines in src/backend/utils/
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any, Union, AsyncIterator
from datetime import datetime, timedelta
from enum import Enum
import json
from dataclasses import dataclass

from ..core.streaming_models import (
    StreamingEvent, StreamingConfig, StreamingEventType, 
    ProgressUpdateEvent, ErrorEvent, StreamingStatus
)
from ..core.data_models import GraphState

logger = logging.getLogger(__name__)

class FallbackMode(str, Enum):
    """Available fallback modes when streaming fails"""
    POLLING = "polling"          # Regular polling for updates
    BATCH_UPDATES = "batch"      # Batched progress updates  
    COMPLETION_ONLY = "completion"  # Only show final results
    OFFLINE = "offline"          # No real-time updates

class StreamingAvailability(str, Enum):
    """Streaming system availability states"""
    AVAILABLE = "available"      # Streaming fully functional
    DEGRADED = "degraded"        # Streaming working but limited
    UNAVAILABLE = "unavailable"  # Streaming completely unavailable
    UNKNOWN = "unknown"          # Availability status unknown

@dataclass
class FallbackConfig:
    """Configuration for fallback behavior"""
    
    # Primary fallback mode
    primary_mode: FallbackMode = FallbackMode.POLLING
    
    # Polling configuration
    polling_interval: float = 2.0  # seconds between polls
    max_polling_duration: float = 300.0  # max time to poll (5 minutes)
    
    # Batch update configuration  
    batch_size: int = 5  # events per batch
    batch_interval: float = 5.0  # seconds between batches
    
    # Retry configuration
    max_retry_attempts: int = 3
    retry_delay: float = 1.0  # initial retry delay
    retry_backoff: float = 2.0  # backoff multiplier
    
    # User feedback
    show_fallback_notice: bool = True
    fallback_message: str = "Real-time updates temporarily unavailable. Using fallback mode."
    
    # Performance thresholds
    connection_timeout: float = 10.0
    slow_connection_threshold: float = 5.0

class StreamingFallbackManager:
    """
    Manages fallback behavior when streaming is unavailable or degraded.
    
    Provides graceful degradation with multiple fallback strategies
    to ensure users can still access analysis results.
    """
    
    def __init__(self, config: FallbackConfig = None):
        self.config = config or FallbackConfig()
        self.availability_status = StreamingAvailability.UNKNOWN
        self.last_availability_check = datetime.now()
        self.active_fallback_mode: Optional[FallbackMode] = None
        
        # Event handlers
        self.on_fallback_activated: List[Callable] = []
        self.on_fallback_deactivated: List[Callable] = []
        self.on_availability_changed: List[Callable] = []
        
        # Polling state
        self.polling_task: Optional[asyncio.Task] = None
        self.is_polling = False
        
        # Metrics
        self.fallback_activations = 0
        self.total_polling_time = 0.0
        self.successful_reconnections = 0
    
    async def check_streaming_availability(self, websocket_url: str = None) -> StreamingAvailability:
        """
        Check if streaming is available and functional.
        
        Args:
            websocket_url: Optional WebSocket URL to test
            
        Returns:
            StreamingAvailability: Current availability status
        """
        try:
            # Simple connectivity check
            if websocket_url:
                # In a real implementation, you might do:
                # - Test WebSocket connection
                # - Check response times
                # - Verify server health endpoint
                logger.debug(f"Checking streaming availability at {websocket_url}")
            
            # For now, simulate availability check
            # In real implementation, this would test actual connectivity
            await asyncio.sleep(0.1)  # Simulate network check
            
            previous_status = self.availability_status
            self.availability_status = StreamingAvailability.AVAILABLE
            self.last_availability_check = datetime.now()
            
            # Notify if status changed
            if previous_status != self.availability_status:
                await self._notify_availability_changed(previous_status, self.availability_status)
            
            return self.availability_status
            
        except asyncio.TimeoutError:
            logger.warning("Streaming availability check timed out")
            self.availability_status = StreamingAvailability.UNAVAILABLE
            return self.availability_status
        except Exception as e:
            logger.error(f"Error checking streaming availability: {e}")
            self.availability_status = StreamingAvailability.UNKNOWN
            return self.availability_status
    
    async def activate_fallback(self, reason: str, mode: FallbackMode = None) -> bool:
        """
        Activate fallback mode due to streaming failure.
        
        Args:
            reason: Reason for activating fallback
            mode: Specific fallback mode to use (uses config default if None)
            
        Returns:
            bool: True if fallback was activated successfully
        """
        try:
            if self.active_fallback_mode is not None:
                logger.debug("Fallback mode already active")
                return True
            
            fallback_mode = mode or self.config.primary_mode
            self.active_fallback_mode = fallback_mode
            self.fallback_activations += 1
            
            logger.info(f"Activating fallback mode '{fallback_mode}' due to: {reason}")
            
            # Start appropriate fallback behavior
            if fallback_mode == FallbackMode.POLLING:
                await self._start_polling()
            elif fallback_mode == FallbackMode.BATCH_UPDATES:
                await self._start_batch_updates()
            # Other modes might not require background tasks
            
            # Notify handlers
            await self._notify_fallback_activated(reason, fallback_mode)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate fallback mode: {e}")
            return False
    
    async def deactivate_fallback(self, reason: str = "Streaming restored") -> bool:
        """
        Deactivate fallback mode when streaming is restored.
        
        Args:
            reason: Reason for deactivating fallback
            
        Returns:
            bool: True if fallback was deactivated successfully
        """
        try:
            if self.active_fallback_mode is None:
                logger.debug("No fallback mode is currently active")
                return True
            
            previous_mode = self.active_fallback_mode
            self.active_fallback_mode = None
            
            # Stop background tasks
            await self._stop_polling()
            
            logger.info(f"Deactivated fallback mode '{previous_mode}' - {reason}")
            
            # Notify handlers
            await self._notify_fallback_deactivated(reason, previous_mode)
            
            self.successful_reconnections += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate fallback mode: {e}")
            return False
    
    async def get_analysis_progress_fallback(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get analysis progress using fallback methods when streaming unavailable.
        
        Args:
            analysis_id: ID of the analysis to check
            
        Returns:
            Dict containing progress information
        """
        try:
            if self.active_fallback_mode == FallbackMode.COMPLETION_ONLY:
                # Only check if analysis is complete
                return await self._check_completion_status(analysis_id)
            
            elif self.active_fallback_mode == FallbackMode.POLLING:
                # Get detailed progress via polling
                return await self._poll_analysis_progress(analysis_id)
            
            elif self.active_fallback_mode == FallbackMode.BATCH_UPDATES:
                # Get batched progress updates
                return await self._get_batch_progress(analysis_id)
            
            else:
                # Default: basic status check
                return await self._check_completion_status(analysis_id)
                
        except Exception as e:
            logger.error(f"Error getting fallback progress for analysis {analysis_id}: {e}")
            return {
                "analysis_id": analysis_id,
                "status": "error",
                "error": str(e),
                "fallback_mode": self.active_fallback_mode.value if self.active_fallback_mode else None
            }
    
    async def simulate_streaming_events(self, analysis_data: Dict[str, Any]) -> AsyncIterator[StreamingEvent]:
        """
        Simulate streaming events for fallback mode based on analysis data.
        
        This creates synthetic streaming events when real-time streaming
        is unavailable but we still want to show progress.
        
        Args:
            analysis_data: Analysis data to create events from
            
        Yields:
            StreamingEvent: Simulated streaming events
        """
        try:
            # Extract relevant data
            competitors = analysis_data.get("competitors", [])
            opportunities = analysis_data.get("strategic_opportunities", [])
            
            # Simulate analysis start
            yield ProgressUpdateEvent(
                message="Analysis started (fallback mode)",
                current_step="Initializing analysis",
                completed_steps=[],
                remaining_steps=["Research", "Analysis", "Generation", "Completion"],
                progress_percentage=0.0
            )
            
            await asyncio.sleep(0.5)
            
            # Simulate competitor research
            for i, competitor in enumerate(competitors):
                progress = (i + 1) / len(competitors) * 25.0  # 25% for research phase
                
                yield ProgressUpdateEvent(
                    message=f"Researching {competitor}",
                    current_step=f"Analyzing competitor {i+1} of {len(competitors)}",
                    completed_steps=["Initializing analysis"],
                    remaining_steps=["Analysis", "Generation", "Completion"],
                    progress_percentage=progress
                )
                
                await asyncio.sleep(0.3)
            
            # Simulate analysis phase
            yield ProgressUpdateEvent(
                message="Analyzing competitive landscape",
                current_step="Processing research data",
                completed_steps=["Initializing analysis", "Research"],
                remaining_steps=["Generation", "Completion"],
                progress_percentage=50.0
            )
            
            await asyncio.sleep(0.5)
            
            # Simulate opportunity generation
            for i, opportunity in enumerate(opportunities):
                progress = 50.0 + (i + 1) / len(opportunities) * 40.0  # 40% for generation
                
                yield ProgressUpdateEvent(
                    message=f"Generated opportunity: {opportunity.get('title', 'Strategic Opportunity')}",
                    current_step=f"Generating opportunity {i+1} of {len(opportunities)}",
                    completed_steps=["Initializing analysis", "Research", "Analysis"],
                    remaining_steps=["Completion"],
                    progress_percentage=progress
                )
                
                await asyncio.sleep(0.2)
            
            # Simulate completion
            yield ProgressUpdateEvent(
                message="Analysis completed successfully",
                current_step="Finalizing results",
                completed_steps=["Initializing analysis", "Research", "Analysis", "Generation"],
                remaining_steps=[],
                progress_percentage=100.0
            )
            
        except Exception as e:
            logger.error(f"Error simulating streaming events: {e}")
            yield ErrorEvent(
                message="Error in fallback event simulation",
                error_type="FallbackError",
                error_details=str(e),
                is_recoverable=True
            )
    
    async def _start_polling(self):
        """Start polling for updates"""
        if self.is_polling:
            return
        
        self.is_polling = True
        self.polling_task = asyncio.create_task(self._polling_loop())
    
    async def _stop_polling(self):
        """Stop polling for updates"""
        self.is_polling = False
        
        if self.polling_task and not self.polling_task.done():
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        
        self.polling_task = None
    
    async def _polling_loop(self):
        """Main polling loop for fallback updates"""
        try:
            start_time = datetime.now()
            
            while self.is_polling:
                # Check if we've exceeded max polling duration
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > self.config.max_polling_duration:
                    logger.info("Max polling duration reached, stopping")
                    break
                
                # Perform polling check (implementation specific)
                await self._perform_polling_check()
                
                # Wait for next poll
                await asyncio.sleep(self.config.polling_interval)
                
        except asyncio.CancelledError:
            logger.debug("Polling loop cancelled")
        except Exception as e:
            logger.error(f"Error in polling loop: {e}")
        finally:
            self.is_polling = False
            self.total_polling_time += (datetime.now() - start_time).total_seconds()
    
    async def _perform_polling_check(self):
        """Perform a single polling check"""
        # This would be implemented based on specific requirements
        # For example, checking analysis status endpoint
        logger.debug("Performing polling check")
    
    async def _start_batch_updates(self):
        """Start batched update collection"""
        logger.debug("Starting batch updates mode")
        # Implementation would collect events in batches
    
    async def _check_completion_status(self, analysis_id: str) -> Dict[str, Any]:
        """Check if analysis is complete"""
        # This would query the analysis status endpoint
        return {
            "analysis_id": analysis_id,
            "status": "checking",
            "mode": "completion_only",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _poll_analysis_progress(self, analysis_id: str) -> Dict[str, Any]:
        """Poll for detailed analysis progress"""
        # This would query a progress endpoint
        return {
            "analysis_id": analysis_id,
            "status": "polling",
            "mode": "polling",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_batch_progress(self, analysis_id: str) -> Dict[str, Any]:
        """Get batched progress information"""
        return {
            "analysis_id": analysis_id,
            "status": "batching",
            "mode": "batch_updates",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _notify_fallback_activated(self, reason: str, mode: FallbackMode):
        """Notify handlers that fallback was activated"""
        for handler in self.on_fallback_activated:
            try:
                await handler(reason, mode)
            except Exception as e:
                logger.warning(f"Fallback activation handler error: {e}")
    
    async def _notify_fallback_deactivated(self, reason: str, mode: FallbackMode):
        """Notify handlers that fallback was deactivated"""
        for handler in self.on_fallback_deactivated:
            try:
                await handler(reason, mode)
            except Exception as e:
                logger.warning(f"Fallback deactivation handler error: {e}")
    
    async def _notify_availability_changed(self, old_status: StreamingAvailability, new_status: StreamingAvailability):
        """Notify handlers that availability status changed"""
        for handler in self.on_availability_changed:
            try:
                await handler(old_status, new_status)
            except Exception as e:
                logger.warning(f"Availability change handler error: {e}")
    
    def get_fallback_metrics(self) -> Dict[str, Any]:
        """Get metrics about fallback usage"""
        return {
            "fallback_activations": self.fallback_activations,
            "total_polling_time": self.total_polling_time,
            "successful_reconnections": self.successful_reconnections,
            "current_availability": self.availability_status.value,
            "active_fallback_mode": self.active_fallback_mode.value if self.active_fallback_mode else None,
            "last_availability_check": self.last_availability_check.isoformat(),
            "is_polling": self.is_polling
        }
    
    def is_fallback_active(self) -> bool:
        """Check if any fallback mode is currently active"""
        return self.active_fallback_mode is not None
    
    def get_user_feedback_message(self) -> Optional[str]:
        """Get user-friendly message about current fallback status"""
        if not self.is_fallback_active():
            return None
        
        if self.config.show_fallback_notice:
            mode_descriptions = {
                FallbackMode.POLLING: "Checking for updates regularly",
                FallbackMode.BATCH_UPDATES: "Updates will be shown in batches", 
                FallbackMode.COMPLETION_ONLY: "Results will be shown when complete",
                FallbackMode.OFFLINE: "Working offline - limited functionality"
            }
            
            mode_desc = mode_descriptions.get(self.active_fallback_mode, "Using alternative update method")
            return f"{self.config.fallback_message} {mode_desc}."
        
        return None

# Global fallback manager instance
_fallback_manager: Optional[StreamingFallbackManager] = None

def get_fallback_manager(config: FallbackConfig = None) -> StreamingFallbackManager:
    """Get or create the global fallback manager instance"""
    global _fallback_manager
    
    if _fallback_manager is None:
        _fallback_manager = StreamingFallbackManager(config)
    
    return _fallback_manager

# Utility functions for common fallback scenarios

async def handle_connection_failure(error_message: str, websocket_url: str = None) -> StreamingFallbackManager:
    """
    Handle a streaming connection failure by activating appropriate fallback.
    
    Args:
        error_message: Description of the connection failure
        websocket_url: Optional WebSocket URL for availability testing
        
    Returns:
        StreamingFallbackManager: Configured fallback manager
    """
    manager = get_fallback_manager()
    
    # Check current availability
    availability = await manager.check_streaming_availability(websocket_url)
    
    # Determine appropriate fallback mode based on availability
    if availability == StreamingAvailability.UNAVAILABLE:
        fallback_mode = FallbackMode.POLLING
    elif availability == StreamingAvailability.DEGRADED:
        fallback_mode = FallbackMode.BATCH_UPDATES
    else:
        fallback_mode = FallbackMode.COMPLETION_ONLY
    
    # Activate fallback
    await manager.activate_fallback(error_message, fallback_mode)
    
    return manager

async def attempt_graceful_reconnection(max_attempts: int = 3) -> bool:
    """
    Attempt to gracefully reconnect to streaming services.
    
    Args:
        max_attempts: Maximum number of reconnection attempts
        
    Returns:
        bool: True if reconnection was successful
    """
    manager = get_fallback_manager()
    
    for attempt in range(max_attempts):
        try:
            # Test availability
            availability = await manager.check_streaming_availability()
            
            if availability == StreamingAvailability.AVAILABLE:
                # Deactivate fallback if successful
                await manager.deactivate_fallback("Reconnection successful")
                return True
            
            # Wait before next attempt with exponential backoff
            if attempt < max_attempts - 1:
                delay = manager.config.retry_delay * (manager.config.retry_backoff ** attempt)
                logger.info(f"Reconnection attempt {attempt + 1} failed, retrying in {delay:.1f} seconds")
                await asyncio.sleep(delay)
                
        except Exception as e:
            logger.warning(f"Reconnection attempt {attempt + 1} failed: {e}")
    
    logger.error(f"Failed to reconnect after {max_attempts} attempts")
    return False 