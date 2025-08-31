from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncConnection

from src.adapters.database.connection import get_db_connection
from src.services.appointment_service import AppointmentBusinessService
from src.models.appointment import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentStatus
from src.models.api_responses import APIResponse, APIListResponse, PaginationInfo

router = APIRouter(prefix="/appointments", tags=["appointments"])


async def get_appointment_service(connection: AsyncConnection = Depends(get_db_connection)) -> AppointmentBusinessService:
    """Dependency to get appointment business service."""
    return AppointmentBusinessService(connection)


@router.post("", response_model=APIResponse[Appointment], status_code=201)
async def create_appointment(
    appointment_data: AppointmentCreate,
    service: AppointmentBusinessService = Depends(get_appointment_service)
) -> APIResponse[Appointment]:
    """
    Create a new appointment.

    """
    try:
        appointment = await service.create_appointment(appointment_data)
        return APIResponse(data=appointment, message="Appointment created successfully")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{appointment_id}", response_model=APIResponse[Appointment])
async def get_appointment(
    appointment_id: str,
    service: AppointmentBusinessService = Depends(get_appointment_service)
) -> APIResponse[Appointment]:
    """
    Get an appointment by ID.

    """
    try:
        appointment = await service.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with ID {appointment_id} not found"
            )
        
        return APIResponse(data=appointment, message="Appointment retrieved successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=APIListResponse[Appointment])
async def get_appointments(
    limit: int = Query(50, ge=1, le=100, description="Number of appointments to return"),
    offset: int = Query(0, ge=0, description="Number of appointments to skip"),
    patient: Optional[str] = Query(None, description="Filter by patient NHS number"),
    status: Optional[AppointmentStatus] = Query(None, description="Filter by appointment status"),
    department: Optional[str] = Query(None, description="Filter by department"),
    clinician: Optional[str] = Query(None, description="Filter by clinician"),
    service: AppointmentBusinessService = Depends(get_appointment_service)
) -> APIListResponse[Appointment]:
    """
    Get appointments with optional filtering and pagination.

    """
    try:
        # Apply filters based on query parameters
        if patient:
            appointments = await service.get_appointments_by_patient(patient)
        elif status:
            appointments = await service.get_appointments_by_status(status)
        else:
            # Get all appointments (we'll need to add this method to the service)
            appointments = await service.adapter.get_all_appointments()
        
        # Apply additional filters
        if department:
            appointments = [apt for apt in appointments if apt.department.lower() == department.lower()]
        
        if clinician:
            appointments = [apt for apt in appointments if clinician.lower() in apt.clinician.lower()]
        
        # Apply pagination
        total = len(appointments)
        paginated_appointments = appointments[offset:offset + limit]
        has_next = offset + limit < total
        
        pagination = PaginationInfo(
            total=total,
            limit=limit,
            offset=offset,
            has_next=has_next
        )
        
        return APIListResponse(
            data=paginated_appointments,
            pagination=pagination,
            message="Appointments retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{appointment_id}", response_model=APIResponse[Appointment])
async def update_appointment(
    appointment_id: str,
    appointment_data: AppointmentUpdate,
    service: AppointmentBusinessService = Depends(get_appointment_service)
) -> APIResponse[Appointment]:
    """
    Update an appointment by ID.
    
    """
    try:
        updated_appointment = await service.update_appointment(appointment_id, appointment_data)
        if not updated_appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with ID {appointment_id} not found"
            )
        
        return APIResponse(data=updated_appointment, message="Appointment updated successfully")
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{appointment_id}", status_code=204)
async def delete_appointment(
    appointment_id: str,
    service: AppointmentBusinessService = Depends(get_appointment_service)
) -> None:
    """
    Delete an appointment by ID.

    """
    try:
        deleted = await service.delete_appointment(appointment_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with ID {appointment_id} not found"
            )
        
        # Return 204 No Content for successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{appointment_id}/cancel", response_model=APIResponse[Appointment])
async def cancel_appointment(
    appointment_id: str,
    service: AppointmentBusinessService = Depends(get_appointment_service)
) -> APIResponse[Appointment]:
    """
    Cancel an appointment.

    """
    try:
        cancelled_appointment = await service.cancel_appointment(appointment_id)
        if not cancelled_appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with ID {appointment_id} not found"
            )
        
        return APIResponse(data=cancelled_appointment, message="Appointment cancelled successfully")
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{appointment_id}/attend", response_model=APIResponse[Appointment])
async def mark_appointment_attended(
    appointment_id: str,
    service: AppointmentBusinessService = Depends(get_appointment_service)
) -> APIResponse[Appointment]:
    """
    Mark an appointment as attended.

    """
    try:
        attended_appointment = await service.mark_appointment_attended(appointment_id)
        if not attended_appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with ID {appointment_id} not found"
            )
        
        return APIResponse(data=attended_appointment, message="Appointment marked as attended")
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/mark-overdue-as-missed", response_model=APIListResponse[Appointment])
async def mark_overdue_appointments_as_missed(
    service: AppointmentBusinessService = Depends(get_appointment_service)
) -> APIListResponse[Appointment]:
    """
    Mark all overdue appointments as missed.

    """
    try:
        missed_appointments = await service.mark_overdue_appointments_as_missed()
        
        return APIListResponse(
            data=missed_appointments,
            message=f"Marked {len(missed_appointments)} overdue appointments as missed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
