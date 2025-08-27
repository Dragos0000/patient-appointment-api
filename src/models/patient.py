"""Patient Pydantic models."""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, validator
import re


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
        """Validate NHS number format."""
        if not v:
            raise ValueError('NHS number is required')
        
        # Remove spaces and validate format - keep as 10 digits without formatting
        nhs_clean = v.replace(' ', '')
        if not re.match(r'^\d{10}$', nhs_clean):
            raise ValueError('NHS number must be 10 digits')
        
        return nhs_clean

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
        """Validate NHS number format."""
        if v is None:
            return v
        
        # Remove spaces and validate format - keep as 10 digits without formatting
        nhs_clean = v.replace(' ', '')
        if not re.match(r'^\d{10}$', nhs_clean):
            raise ValueError('NHS number must be 10 digits')
        
        return nhs_clean

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



Patient = PatientBase
