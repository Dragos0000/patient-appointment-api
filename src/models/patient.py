"""Patient Pydantic models."""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, validator

from utils.validators import format_nhs_number, format_uk_postcode


class PatientBase(BaseModel):
    """Base patient model"""
    
    nhs_number: str = Field(..., description="NHS number (10 digits)")
    name: str = Field(..., min_length=1, max_length=255, description="Patient's full name")
    date_of_birth: date = Field(..., description="Patient's date of birth")
    postcode: str = Field(..., min_length=1, max_length=10, description="UK postcode")

    class Config:
        from_attributes = True  # For SQLAlchemy compatibility
        json_encoders = {
            date: lambda v: v.isoformat()
        }

    @validator('nhs_number')
    def validate_nhs_number(cls, v):
        """Validate and format NHS number with checksum validation."""
        if not v:
            raise ValueError('NHS number is required')
        
        formatted_nhs = format_nhs_number(v)
        if formatted_nhs is None:
            raise ValueError('Invalid NHS number: must be 10 digits with valid checksum')
        
        return formatted_nhs

    @validator('postcode')
    def validate_postcode(cls, v):
        """Validate and format UK postcode."""
        if not v:
            raise ValueError('Postcode is required')
        
        formatted_postcode = format_uk_postcode(v)
        if formatted_postcode is None:
            raise ValueError('Invalid UK postcode format')
        
        return formatted_postcode


class PatientCreate(PatientBase):
    """Model for creating a new patient."""
    pass


class PatientUpdate(BaseModel):
    """Model for updating an existing patient."""
    
    nhs_number: Optional[str] = Field(None, description="NHS number (10 digits)")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Patient's full name")
    date_of_birth: Optional[date] = Field(None, description="Patient's date of birth")
    postcode: Optional[str] = Field(None, min_length=1, max_length=10, description="UK postcode")

    @validator('nhs_number')
    def validate_nhs_number(cls, v):
        """Validate and format NHS number with checksum validation."""
        if v is None:
            return v
        
        formatted_nhs = format_nhs_number(v)
        if formatted_nhs is None:
            raise ValueError('Invalid NHS number: must be 10 digits with valid checksum')
        
        return formatted_nhs

    @validator('postcode')
    def validate_postcode(cls, v):
        """Validate and format UK postcode."""
        if v is None:
            return v
        
        formatted_postcode = format_uk_postcode(v)
        if formatted_postcode is None:
            raise ValueError('Invalid UK postcode format')
        
        return formatted_postcode



Patient = PatientBase
