import asyncio
import logging
import os
from typing import Optional
from datetime import datetime

from src.adapters.database.connection import async_engine
from src.services.appointment_service import AppointmentBusinessService
from src.utils.timezone_utils import get_utc_now

logger = logging.getLogger(__name__)


class BackgroundTaskService:
    """Service for managing background tasks."""
    
    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.check_interval = int(os.getenv("BACKGROUND_TASK_INTERVAL", "300"))  # Default: 5 minutes in seconds
    
    async def start(self):
        """Start the background task service."""
        if self.running:
            logger.warning("Background task service is already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_periodic_tasks())
        logger.info(f"Background task service started (checking every {self.check_interval} seconds)")
    
    async def stop(self):
        """Stop the background task service."""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Background task service stopped")
    
    async def _run_periodic_tasks(self):
        """Main loop for periodic tasks."""
        while self.running:
            try:
                await self._check_overdue_appointments()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                logger.info("Background task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in background task: {e}", exc_info=True)
                # Continue running even if there's an error
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _check_overdue_appointments(self):
        """Check for and mark overdue appointments as missed."""
        try:
            current_time = get_utc_now()
            logger.debug(f"Checking for overdue appointments at {current_time}")
            
            # Create database connection for background task
            async with async_engine.begin() as connection:
                service = AppointmentBusinessService(connection)
                
                # Mark overdue appointments as missed
                missed_appointments = await service.mark_overdue_appointments_as_missed(current_time)
                
                if missed_appointments:
                    logger.info(f"Marked {len(missed_appointments)} overdue appointments as missed")
                    for apt in missed_appointments:
                        logger.info(f"  - Appointment {apt.id} (patient: {apt.patient}) marked as missed")
                else:
                    logger.debug("No overdue appointments found")
                    
        except Exception as e:
            logger.error(f"Failed to check overdue appointments: {e}", exc_info=True)
            raise


background_service = BackgroundTaskService()
