from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncConnection

from src.models.appointment import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentStatus
from src.adapters.database.appointment_adapter import AppointmentDatabaseAdapter
from src.utils.appointment_utils import is_appointment_overdue
from src.utils.timezone_utils import get_utc_now


class AppointmentBusinessService:
    """
    Business service for appointments with business rule enforcement.
    """
    
    def __init__(self, connection: AsyncConnection):
        self.adapter = AppointmentDatabaseAdapter(connection)
    
    async def create_appointment(self, appointment_data: AppointmentCreate) -> Appointment:
        """
        Create a new appointment.
        
        """
        return await self.adapter.create_appointment(appointment_data)
    
    async def get_appointment_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """
        Get appointment by ID.
        
        """
        return await self.adapter.get_appointment_by_id(appointment_id)
    
    async def update_appointment_status(self, appointment_id: str, new_status: AppointmentStatus) -> Optional[Appointment]:
        """
        Update appointment status 
        Cancelled appointments cannot be reinstated
        Returns:
            Updated appointment or None if not found
            
        Raises:
            ValueError: If business rules are violated.Cancelled appointments cannot be reinstated
        """
        
        current_appointment = await self.adapter.get_appointment_by_id(appointment_id)
        if current_appointment is None:
            return None
        
        # Business Rule: Cancelled appointments cannot be reinstated
        if current_appointment.status == AppointmentStatus.CANCELLED and new_status != AppointmentStatus.CANCELLED:
            raise ValueError("Cancelled appointments cannot be reinstated")
        
        return await self.adapter.update_appointment_status(appointment_id, new_status)
    
    async def update_appointment(self, appointment_id: str, appointment_data: AppointmentUpdate) -> Optional[Appointment]:
        """
        Update appointment

        Returns:
            Updated appointment or None if not found
            
        Raises:
            ValueError: If business rules are violated. Cancelled appointments cannot be reinstated
        """
        # Get current appointment for validation
        current_appointment = await self.adapter.get_appointment_by_id(appointment_id)
        if current_appointment is None:
            return None
        
        # Validate status transition at model level
        appointment_data.validate_status_transition(current_appointment.status)
        
        # Proceed with update
        return await self.adapter.update_appointment(appointment_id, appointment_data)
    
    async def cancel_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """
        Cancel an appointment.
        Cancelled appointments cannot be reinstated
        """
        return await self.update_appointment_status(appointment_id, AppointmentStatus.CANCELLED)
    
    async def mark_appointment_attended(self, appointment_id: str) -> Optional[Appointment]:
        """
        Mark an appointment as attended.
        """
        return await self.update_appointment_status(appointment_id, AppointmentStatus.ATTENDED)
    
    async def mark_overdue_appointments_as_missed(self, current_time: Optional[datetime] = None) -> List[Appointment]:
        """
        Mark overdue appointments as missed.
        
        Returns:
            List of appointments that were marked as missed
        """
        if current_time is None:
            current_time = get_utc_now()
        

        active_statuses = [AppointmentStatus.SCHEDULED, AppointmentStatus.ACTIVE]
        overdue_appointments = []
        
        for status in active_statuses:
            appointments = await self.adapter.get_appointments_by_status(status)
            
            for appointment in appointments:
                if is_appointment_overdue(appointment.time, appointment.duration, current_time):
                    updated_appointment = await self.adapter.update_appointment_status(
                        appointment.id, 
                        AppointmentStatus.MISSED
                    )
                    if updated_appointment:
                        overdue_appointments.append(updated_appointment)
        
        return overdue_appointments
    
    async def get_appointments_by_patient(self, nhs_number: str) -> List[Appointment]:
        """
        Get all appointments for a patient.
        """
        return await self.adapter.get_appointments_by_patient(nhs_number)
    
    async def get_appointments_by_status(self, status: AppointmentStatus) -> List[Appointment]:
        """
        Get appointments by status.
   
        """
        return await self.adapter.get_appointments_by_status(status)
    
    async def delete_appointment(self, appointment_id: str) -> bool:
        """
        Delete an appointment.

        """
        return await self.adapter.delete_appointment(appointment_id)
