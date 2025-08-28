from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncConnection

from src.adapters.database.connection import get_db_connection
from src.adapters.database.patient_adapter import PatientDatabaseAdapter
from src.models.patient import Patient, PatientCreate, PatientUpdate
from src.models.api_responses import APIResponse, APIListResponse, PaginationInfo

router = APIRouter(prefix="/patients", tags=["patients"])


async def get_patient_adapter(connection: AsyncConnection = Depends(get_db_connection)) -> PatientDatabaseAdapter:
    """Dependency to get patient database adapter."""
    return PatientDatabaseAdapter(connection)


@router.post("", response_model=APIResponse[Patient], status_code=201)
async def create_patient(
    patient_data: PatientCreate,
    adapter: PatientDatabaseAdapter = Depends(get_patient_adapter)
) -> APIResponse[Patient]:
    """
    Create a new patient.        
    Raises:
        HTTPException: If patient already exists or validation fails
    """
    try:
        # Check if patient already exists
        existing_patient = await adapter.get_patient_by_nhs_number(patient_data.nhs_number)
        if existing_patient:
            raise HTTPException(
                status_code=409,
                detail=f"Patient with NHS number {patient_data.nhs_number} already exists"
            )
        
        # Create the patient
        patient = await adapter.create_patient(patient_data)
        return APIResponse(data=patient, message="Patient created successfully")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{nhs_number}", response_model=APIResponse[Patient])
async def get_patient(
    nhs_number: str,
    adapter: PatientDatabaseAdapter = Depends(get_patient_adapter)
) -> APIResponse[Patient]:
    """
    Get a patient by NHS number.        
    Raises:
        HTTPException: If patient not found
    """
    try:
        patient = await adapter.get_patient_by_nhs_number(nhs_number)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail=f"Patient with NHS number {nhs_number} not found"
            )
        
        return APIResponse(data=patient, message="Patient retrieved successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=APIListResponse[Patient])
async def get_patients(
    limit: int = Query(50, ge=1, le=100, description="Number of patients to return"),
    offset: int = Query(0, ge=0, description="Number of patients to skip"),
    adapter: PatientDatabaseAdapter = Depends(get_patient_adapter)
) -> APIListResponse[Patient]:
    """
    Get all patients with pagination.    
    Returns:
        List of patients with pagination info
    """
    try:
        # Get all patients (for now, we'll implement basic pagination)
        all_patients = await adapter.get_all_patients()
        
        # Apply pagination
        total = len(all_patients)
        paginated_patients = all_patients[offset:offset + limit]
        has_next = offset + limit < total
        
        pagination = PaginationInfo(
            total=total,
            limit=limit,
            offset=offset,
            has_next=has_next
        )
        
        return APIListResponse(
            data=paginated_patients,
            pagination=pagination,
            message="Patients retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{nhs_number}", response_model=APIResponse[Patient])
async def update_patient(
    nhs_number: str,
    patient_data: PatientUpdate,
    adapter: PatientDatabaseAdapter = Depends(get_patient_adapter)
) -> APIResponse[Patient]:
    """
    Update a patient by NHS number.        
    Raises:
        HTTPException: If patient not found or validation fails
    """
    try:
        updated_patient = await adapter.update_patient(nhs_number, patient_data)
        if not updated_patient:
            raise HTTPException(
                status_code=404,
                detail=f"Patient with NHS number {nhs_number} not found"
            )
        
        return APIResponse(data=updated_patient, message="Patient updated successfully")
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{nhs_number}", status_code=204)
async def delete_patient(
    nhs_number: str,
    adapter: PatientDatabaseAdapter = Depends(get_patient_adapter)
) -> None:
    """
    Delete a patient by NHS number.
    Raises:
        HTTPException: If patient not found
    """
    try:
        deleted = await adapter.delete_patient(nhs_number)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Patient with NHS number {nhs_number} not found"
            )
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{nhs_number}/appointments", response_model=APIListResponse)
async def get_patient_appointments(
    nhs_number: str,
    adapter: PatientDatabaseAdapter = Depends(get_patient_adapter)
) -> APIListResponse:
    """
    Get all appointments for a patient.
    Raises:
        HTTPException: If patient not found
    """
    try:
        # First check if patient exists
        patient = await adapter.get_patient_by_nhs_number(nhs_number)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail=f"Patient with NHS number {nhs_number} not found"
            )
        
        # TODO: This will be implemented when the appointment adapter is created
        # For now, return empty list
        return APIListResponse(
            data=[],
            message="Patient appointments retrieved successfully (not implemented yet)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
