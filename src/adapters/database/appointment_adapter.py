from typing import List, Optional
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncConnection

from src.models.appointment import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentStatus
from src.adapters.database.tables import appointments_table


class AppointmentDatabaseAdapter:
    """Appointment repository"""
    
    def __init__(self, connection: AsyncConnection):
        self.connection = connection
    
    async def create_appointment(self, appointment_data: AppointmentCreate) -> Appointment:
        """
        Create a new appointment in the database
        """
        # Convert Pydantic model to dict
        appointment_dict = appointment_data.model_dump()
        
        # Generate ID for the appointment
        from uuid import uuid4
        appointment_dict["id"] = str(uuid4())
        
        # Insert into database
        record = insert(appointments_table).values(**appointment_dict)
        await self.connection.execute(record)
        
        # Return the created appointment
        return Appointment(**appointment_dict)
    
    async def get_appointment_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """
        Get an appointment by ID
        """
        record = select(appointments_table).where(appointments_table.c.id == appointment_id)
        result = await self.connection.execute(record)
        row = result.fetchone()
        
        if row is None:
            return None
        
        return Appointment(**row._asdict())
    
    async def get_appointments_by_patient(self, nhs_number: str) -> List[Appointment]:
        """
        Get all appointments for a patient
        """
        record = (
            select(appointments_table)
            .where(appointments_table.c.patient == nhs_number)
            .order_by(appointments_table.c.time)
        )
        result = await self.connection.execute(record)
        rows = result.fetchall()
        
        return [Appointment(**row._asdict()) for row in rows]
    
    async def get_appointments_by_status(self, status: AppointmentStatus) -> List[Appointment]:
        """
        Get all appointments by status
        """
        record = (
            select(appointments_table)
            .where(appointments_table.c.status == status)
            .order_by(appointments_table.c.time)
        )
        result = await self.connection.execute(record)
        rows = result.fetchall()
        
        return [Appointment(**row._asdict()) for row in rows]
    
    async def get_all_appointments(self) -> List[Appointment]:
        """
        Get all appointments
        """
        record = select(appointments_table).order_by(appointments_table.c.time)
        result = await self.connection.execute(record)
        rows = result.fetchall()
        
        return [Appointment(**row._asdict()) for row in rows]
    
    async def update_appointment(self, appointment_id: str, appointment_data: AppointmentUpdate) -> Optional[Appointment]:
        """
        Update an appointment by ID
        """
        # Only update fields that are provided (not None)
        update_dict = {
            k: v for k, v in appointment_data.model_dump(exclude_unset=True).items() 
            if v is not None
        }
        
        if not update_dict:
            # No fields to update, return existing appointment
            return await self.get_appointment_by_id(appointment_id)
        
        record = (
            update(appointments_table)
            .where(appointments_table.c.id == appointment_id)
            .values(**update_dict)
        )
        result = await self.connection.execute(record)
        
        if result.rowcount == 0:
            return None
        
        return await self.get_appointment_by_id(appointment_id)
    
    async def update_appointment_status(self, appointment_id: str, status: AppointmentStatus) -> Optional[Appointment]:
        """
        Update an appointment status by ID
        """
        record = (
            update(appointments_table)
            .where(appointments_table.c.id == appointment_id)
            .values(status=status)
        )
        result = await self.connection.execute(record)
        
        if result.rowcount == 0:
            return None
        
        return await self.get_appointment_by_id(appointment_id)
    
    async def delete_appointment(self, appointment_id: str) -> bool:
        """
        Delete an appointment by ID
        """
        record = delete(appointments_table).where(appointments_table.c.id == appointment_id)
        result = await self.connection.execute(record)
        
        return result.rowcount > 0
    
    async def appointment_exists(self, appointment_id: str) -> bool:
        """
        Check if an appointment exists by ID
        """
        record = select(appointments_table.c.id).where(appointments_table.c.id == appointment_id)
        result = await self.connection.execute(record)
        row = result.fetchone()
        
        return row is not None
