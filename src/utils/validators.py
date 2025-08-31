import re
from typing import Optional


def validate_nhs_number_checksum(nhs_number: str) -> bool:
    """
    Return True if the NHS number is valid (Mod 11), else False.  
    Based on: https://www.datadictionary.nhs.uk/attributes/nhs_number.html
    
    """
    cleaned_nhs_number = re.sub(r"\D", "", nhs_number)  # strip non-digits
    if not re.fullmatch(r"\d{10}", cleaned_nhs_number):
        return False

    nhs_digits = list(map(int, cleaned_nhs_number))
    weighted_sum = sum(
        digit_value * (10 - digit_index)
        for digit_index, digit_value in enumerate(nhs_digits[:9])
    )
    calculated_check_digit = (11 - (weighted_sum % 11)) % 11  # maps 11→0

    return calculated_check_digit != 10 and calculated_check_digit == nhs_digits[9]


def format_nhs_number(nhs_number: str) -> Optional[str]:
    """
    Format NHS number to standard format (remove non-digits, validate checksum).
    """
    if not nhs_number:
        return None
    
    clean_nhs = re.sub(r"\D", "", nhs_number)
    
    if validate_nhs_number_checksum(nhs_number):
        return clean_nhs
    
    return None


def validate_uk_postcode_format(postcode: str) -> bool:
    """
    Validate UK postcode format 
    
    Supports all valid UK postcode patterns:
    - AA9A 9AA (e.g., "SW1A 1AA")
    - A9A 9AA (e.g., "M1A 1AA") 
    - A9 9AA (e.g., "M1 1AA")
    - A99 9AA (e.g., "M60 1NW")
    - AA9 9AA (e.g., "CR0 2YR")
    - AA99 9AA (e.g., "DN55 1PT")
    """
    if not postcode:
        return False
    
    clean_postcode = postcode.replace(' ', '').upper()
    
    patterns = [
        r'^[A-Z]{2}[0-9][A-Z][0-9][A-Z]{2}$',  # AA9A9AA
        r'^[A-Z][0-9][A-Z][0-9][A-Z]{2}$',     # A9A9AA
        r'^[A-Z][0-9][0-9][A-Z]{2}$',          # A99AA
        r'^[A-Z][0-9]{2}[0-9][A-Z]{2}$',       # A999AA
        r'^[A-Z]{2}[0-9][0-9][A-Z]{2}$',       # AA99AA
        r'^[A-Z]{2}[0-9]{2}[0-9][A-Z]{2}$',    # AA999AA
    ]
    
    for pattern in patterns:
        if re.match(pattern, clean_postcode):
            return True
    
    return False


def format_uk_postcode(postcode: str) -> Optional[str]:
    """
    Format UK postcode to standard format (uppercase with space).

    """
    if not postcode:
        return None
    
    # Clean and validate
    clean_postcode = postcode.replace(' ', '').upper()
    
    if not validate_uk_postcode_format(postcode):
        return None
    
    if len(clean_postcode) >= 5:
        outward_code = clean_postcode[:-3]
        inward_code = clean_postcode[-3:]
        return f"{outward_code} {inward_code}"
    
    return None



