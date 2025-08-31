from typing import List, Optional
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncConnection

from src.models.patient import Patient, PatientCreate, PatientUpdate
from src.adapters.database.tables import patients_table


class PatientDatabaseAdapter:
    """Patient repository """
    
    def __init__(self, connection: AsyncConnection):
        self.connection = connection
    
    async def create_patient(self, patient_data: PatientCreate) -> Patient:
        """
        Create a new patient in the database
        """
        # Convert Pydantic model to dict
        patient_dict = patient_data.model_dump()
        
        # Insert into database
        record = insert(patients_table).values(**patient_dict)
        await self.connection.execute(record)
        
        # Return the created patient
        return Patient(**patient_dict)
    
    async def get_patient_by_nhs_number(self, nhs_number: str) -> Optional[Patient]:
        """
        Get a patient by NHS number
        """
        record = select(patients_table).where(patients_table.c.nhs_number == nhs_number)
        result = await self.connection.execute(record)
        row = result.fetchone()
        
        if row is None:
            return None
        
        return Patient(**row._asdict())
    
    async def get_all_patients(self) -> List[Patient]:
        """
        Get all patients
        """
        record = select(patients_table).order_by(patients_table.c.name)
        result = await self.connection.execute(record)
        rows = result.fetchall()
        
        return [Patient(**row._asdict()) for row in rows]
    
    async def update_patient(self, nhs_number: str, patient_data: PatientUpdate) -> Optional[Patient]:
        """
        Update a patient by NHS number
        """
        # Only update fields that are provided (not None)
        update_dict = {
            k: v for k, v in patient_data.model_dump(exclude_unset=True).items() 
            if v is not None
        }
        
        if not update_dict:
            # No fields to update, return existing patient
            return await self.get_patient_by_nhs_number(nhs_number)
        
        record = (
            update(patients_table)
            .where(patients_table.c.nhs_number == nhs_number)
            .values(**update_dict)
        )
        result = await self.connection.execute(record)
        
        if result.rowcount == 0:
            return None
        
        return await self.get_patient_by_nhs_number(nhs_number)
    
    async def delete_patient(self, nhs_number: str) -> bool:
        """
        Delete a patient by NHS number
        """
        record = delete(patients_table).where(patients_table.c.nhs_number == nhs_number)
        result = await self.connection.execute(record)
        
        return result.rowcount > 0
    
    async def patient_exists(self, nhs_number: str) -> bool:
        """
        Check if a patient exists by NHS number
        """
        record = select(patients_table.c.nhs_number).where(patients_table.c.nhs_number == nhs_number)
        result = await self.connection.execute(record)
        row = result.fetchone()
        
        return row is not None
