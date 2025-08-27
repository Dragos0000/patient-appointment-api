from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
import re


class AppointmentStatus(str, Enum):
    """Appointment status"""
    SCHEDULED = "scheduled"
    ATTENDED = "attended"
    ACTIVE = "active"
    MISSED = "missed"
    CANCELLED = "cancelled"


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
        from_attributes = True  # For SQLAlchemy compatibility
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
        """Validate UK postcode format."""
        if not v:
            raise ValueError('Postcode is required')
        
        # Basic UK postcode validation
        postcode_pattern = r'^[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}$'
        if not re.match(postcode_pattern, v.upper()):
            raise ValueError('Invalid UK postcode format')
        
        return v.upper()


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
        """Validate UK postcode format."""
        if not v:
            raise ValueError('Postcode is required')
        
        # Basic UK postcode validation
        postcode_pattern = r'^[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}$'
        if not re.match(postcode_pattern, v.upper()):
            raise ValueError('Invalid UK postcode format')
        
        return v.upper()


class AppointmentUpdate(BaseModel):
    """Model for updating an existing appointment"""
    
    patient: Optional[str] = Field(None, description="Patient NHS number")
    status: Optional[AppointmentStatus] = Field(None, description="Appointment status")
    time: Optional[datetime] = Field(None, description="Appointment date and time")
    duration: Optional[str] = Field(None, description="Duration (e.g., '1h', '30m', '1h 30m')")
    clinician: Optional[str] = Field(None, description="Name of the clinician")
    department: Optional[str] = Field(None, description="Department name")
    postcode: Optional[str] = Field(None, description="Postcode for the appointment location")

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
        
        # At least one of hours or minutes must be specified
        if not hours and not minutes:
            raise ValueError('Duration must specify at least hours or minutes')
        
        return v.strip()

    @validator('postcode')
    def validate_postcode(cls, v):
        """Validate UK postcode format."""
        if v is None:
            return v
        
        # Basic UK postcode validation
        postcode_pattern = r'^[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}$'
        if not re.match(postcode_pattern, v.upper()):
            raise ValueError('Invalid UK postcode format')
        
        return v.upper()


Appointment = AppointmentBase
