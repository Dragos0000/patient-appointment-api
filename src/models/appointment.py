from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
import re

from utils.validators import format_uk_postcode


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
    patient: str = Field(..., description="Patient NHS number or identifier")
    status: AppointmentStatus = Field(..., description="Appointment status")
    time: datetime = Field(..., description="Appointment date and time")
    duration: str = Field(..., description="Duration (e.g., '1h', '30m', '1h 30m')")
    clinician: str = Field(..., description="Name of the clinician")
    department: str = Field(..., description="Department name")
    postcode: str = Field(..., description="Postcode for the appointment location")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

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
    
    patient: str = Field(..., description="Patient NHS number or identifier")
    status: AppointmentStatus = Field(..., description="Appointment status")
    time: datetime = Field(..., description="Appointment date and time")
    duration: str = Field(..., description="Duration (e.g., '1h', '30m', '1h 30m')")
    clinician: str = Field(..., description="Name of the clinician")
    department: str = Field(..., description="Department name")
    postcode: str = Field(..., description="Postcode for the appointment location")

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
                raise ValueError(f"Invalid status transition from {current_status} to {self.status}: Cancelled appointments cannot be reinstated")

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
