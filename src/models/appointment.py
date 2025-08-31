from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
import re

from src.utils.validators import format_uk_postcode
from src.utils.timezone_utils import ensure_timezone_aware, format_datetime_for_api, is_timezone_aware


class AppointmentStatus(str, Enum):
    """Appointment status"""
    SCHEDULED = "scheduled"
    ATTENDED = "attended"
    ACTIVE = "active"
    MISSED = "missed"
    CANCELLED = "cancelled"


def validate_status_transition(current_status: Optional[AppointmentStatus], new_status: AppointmentStatus) -> bool:
    """
    Validate if a status transition is allowed.
    Returns:
        True if transition is valid, False otherwise
    """
    if current_status is None:
        # New appointment - any initial status is allowed
        return True
    
    if current_status == AppointmentStatus.CANCELLED and new_status != AppointmentStatus.CANCELLED:
        # Cannot reinstate cancelled appointments
        return False
    
    # All other transitions are allowed
    return True


class AppointmentBase(BaseModel):
    """Base appointment model"""
    
    id: str = Field(..., description="Unique appointment identifier")
    patient: str = Field(..., description="Patient NHS number")
    status: AppointmentStatus = Field(..., description="Appointment status")
    time: datetime = Field(..., description="Appointment date and time")
    duration: str = Field(..., description="Duration (e.g., '1h', '30m', '1h 30m')")
    clinician: str = Field(..., description="Name of the clinician")
    department: str = Field(..., description="Department name")
    postcode: str = Field(..., description="Postcode for the appointment location")

    class Config:
        json_encoders = {
            datetime: lambda v: format_datetime_for_api(v) if v else None
        }

    @validator('patient')
    def validate_patient_nhs_number(cls, v):
        """Validate patient NHS number with checksum validation."""
        if not v:
            raise ValueError('Patient NHS number is required')
        
        from src.utils.validators import format_nhs_number
        formatted_nhs = format_nhs_number(v)
        if formatted_nhs is None:
            raise ValueError('Invalid patient NHS number: must be 10 digits with valid checksum')
        
        return formatted_nhs

    @validator('duration')
    def validate_duration_format(cls, v):
        """Validate duration format (e.g., '1h', '30m', '1h 30m')."""
        if not v:
            raise ValueError('Duration is required')
        
        # Pattern for duration: optional hours and/or minutes
        pattern = r'^(?:(\d+)h)?(?:\s*(\d+)m)?$'
        match = re.match(pattern, v.strip())
        
        if not match:
            raise ValueError('Duration must be in format like "1h", "30m", or "1h 30m"')
        
        hours, minutes = match.groups()
        
        # At least one of hours or minutes must be specified
        if not hours and not minutes:
            raise ValueError('Duration must specify at least hours or minutes')
        
        return v.strip()

    @validator('time')
    def validate_timezone_aware(cls, v):
        """Ensure appointment time is timezone-aware."""
        if not v:
            raise ValueError('Appointment time is required')
        
        if not is_timezone_aware(v):
            raise ValueError('Appointment time must be timezone-aware (include timezone information)')
        
        return v

    @validator('postcode')
    def validate_postcode(cls, v):
        """Validate and format UK postcode."""
        if not v:
            raise ValueError('Postcode is required')
        
        formatted_postcode = format_uk_postcode(v)
        if formatted_postcode is None:
            raise ValueError('Invalid UK postcode format')
        
        return formatted_postcode


class AppointmentCreate(BaseModel):
    """Model for creating a new appointment"""
    
    patient: str = Field(..., description="Patient NHS number")
    status: AppointmentStatus = Field(..., description="Appointment status")
    time: datetime = Field(..., description="Appointment date and time")
    duration: str = Field(..., description="Duration (e.g., '1h', '30m', '1h 30m')")
    clinician: str = Field(..., description="Name of the clinician")
    department: str = Field(..., description="Department name")
    postcode: str = Field(..., description="Postcode for the appointment location")

    @validator('patient')
    def validate_patient_nhs_number(cls, v):
        """Validate patient NHS number with checksum validation."""
        if not v:
            raise ValueError('Patient NHS number is required')
        
        from src.utils.validators import format_nhs_number
        formatted_nhs = format_nhs_number(v)
        if formatted_nhs is None:
            raise ValueError('Invalid patient NHS number: must be 10 digits with valid checksum')
        
        return formatted_nhs

    @validator('duration')
    def validate_duration_format(cls, v):
        """Validate duration format (e.g., '1h', '30m', '1h 30m')."""
        if not v:
            raise ValueError('Duration is required')
        
        # Pattern for duration: optional hours and/or minutes
        pattern = r'^(?:(\d+)h)?(?:\s*(\d+)m)?$'
        match = re.match(pattern, v.strip())
        
        if not match:
            raise ValueError('Duration must be in format like "1h", "30m", or "1h 30m"')
        
        hours, minutes = match.groups()
        
        # At least one of hours or minutes must be specified
        if not hours and not minutes:
            raise ValueError('Duration must specify at least hours or minutes')
        
        return v.strip()

    @validator('time')
    def validate_timezone_aware(cls, v):
        """Ensure appointment time is timezone-aware."""
        if not v:
            raise ValueError('Appointment time is required')
        
        if not is_timezone_aware(v):
            raise ValueError('Appointment time must be timezone-aware (include timezone information)')
        
        return v

    @validator('postcode')
    def validate_postcode(cls, v):
        """Validate and format UK postcode."""
        if not v:
            raise ValueError('Postcode is required')
        
        formatted_postcode = format_uk_postcode(v)
        if formatted_postcode is None:
            raise ValueError('Invalid UK postcode format')
        
        return formatted_postcode


class AppointmentUpdate(BaseModel):
    """Model for updating an existing appointment"""
    
    patient: Optional[str] = Field(None, description="Patient NHS number")
    status: Optional[AppointmentStatus] = Field(None, description="Appointment status")
    time: Optional[datetime] = Field(None, description="Appointment date and time")
    duration: Optional[str] = Field(None, description="Duration (e.g., '1h', '30m', '1h 30m')")
    clinician: Optional[str] = Field(None, description="Name of the clinician")
    department: Optional[str] = Field(None, description="Department name")
    postcode: Optional[str] = Field(None, description="Postcode for the appointment location")
    
    def validate_status_transition(self, current_status: Optional[AppointmentStatus]) -> None:
        """
        Validate status transition if status is being updated.
        """
        if self.status is not None:
            if not validate_status_transition(current_status, self.status):
                raise ValueError(f"Invalid status transition from {current_status.value} to {self.status.value}: Cancelled appointments cannot be reinstated")

    @validator('patient')
    def validate_patient_nhs_number(cls, v):
        """Validate patient NHS number with checksum validation."""
        if v is None:
            return v
        
        from src.utils.validators import format_nhs_number
        formatted_nhs = format_nhs_number(v)
        if formatted_nhs is None:
            raise ValueError('Invalid patient NHS number: must be 10 digits with valid checksum')
        
        return formatted_nhs

    @validator('duration')
    def validate_duration_format(cls, v):
        """Validate duration format (e.g., '1h', '30m', '1h 30m')."""
        if v is None:
            return v
        
        # Pattern for duration: optional hours and/or minutes
        pattern = r'^(?:(\d+)h)?(?:\s*(\d+)m)?$'
        match = re.match(pattern, v.strip())
        
        if not match:
            raise ValueError('Duration must be in format like "1h", "30m", or "1h 30m"')
        
        hours, minutes = match.groups()
        

        if not hours and not minutes:
            raise ValueError('Duration must specify at least hours or minutes')
        
        return v.strip()

    @validator('time')
    def validate_timezone_aware(cls, v):
        """Ensure appointment time is timezone-aware if provided."""
        if v is None:
            return v
        
        if not is_timezone_aware(v):
            raise ValueError('Appointment time must be timezone-aware (include timezone information)')
        
        return v

    @validator('postcode')
    def validate_postcode(cls, v):
        """Validate and format UK postcode."""
        if v is None:
            return v
        
        formatted_postcode = format_uk_postcode(v)
        if formatted_postcode is None:
            raise ValueError('Invalid UK postcode format')
        
        return formatted_postcode


Appointment = AppointmentBase
