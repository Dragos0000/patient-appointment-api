import pytest

from src.utils.validators import (
    validate_nhs_number_checksum,
    format_nhs_number,
    validate_uk_postcode_format,
    format_uk_postcode
)




def test_valid_nhs_numbers():
    """Test valid NHS numbers with correct checksums."""
    valid_numbers = [
        "9434765919",  
        "9434765870",  
        "9434765838",  
        "9434765846",  
    ]
    
    for nhs_number in valid_numbers:
        assert validate_nhs_number_checksum(nhs_number), f"NHS number {nhs_number} should be valid"


def test_invalid_nhs_numbers():
    """Test invalid NHS numbers with incorrect checksums."""
    invalid_numbers = [
        "9434765918",  
        "9434765871",  
        "1234567890",  
        "1234567891",  
        "1234567892",  
    ]
    
    for nhs_number in invalid_numbers:
        assert not validate_nhs_number_checksum(nhs_number), f"NHS number {nhs_number} should be invalid"


def test_nhs_number_format_validation():
    """Test NHS number format validation."""
    
    assert not validate_nhs_number_checksum("123456789")    
    assert not validate_nhs_number_checksum("12345678901")  
    assert not validate_nhs_number_checksum("123456789a")   
    assert not validate_nhs_number_checksum("")             
    assert not validate_nhs_number_checksum("abc")          


def test_nhs_number_with_spaces():
    """Test NHS numbers with spaces are handled correctly."""
    
    assert validate_nhs_number_checksum("943 476 5919")
    assert validate_nhs_number_checksum("943-476-5919")
    assert validate_nhs_number_checksum(" 9434765919 ")


def test_format_nhs_number_valid():
    """Test formatting valid NHS numbers."""
    assert format_nhs_number("943 476 5919") == "9434765919"
    assert format_nhs_number("943-476-5919") == "9434765919"
    assert format_nhs_number(" 9434765919 ") == "9434765919"
    assert format_nhs_number("9434765919") == "9434765919"


def test_format_nhs_number_invalid():
    """Test formatting invalid NHS numbers returns None."""
    assert format_nhs_number("1234567890") is None
    assert format_nhs_number("123456789") is None
    assert format_nhs_number("abc") is None
    assert format_nhs_number("") is None
    assert format_nhs_number(None) is None


def test_nhs_checksum_algorithm_steps():
    """Test the NHS checksum algorithm step by step."""
    
    nhs_number = "9434765919"
    
    # Manual calculation using the in algorithm
    digits = [9, 4, 3, 4, 7, 6, 5, 9, 1, 9]  
    
    # weighted sum for first 9 digits
    weighted_sum = sum(
        digit_value * (10 - digit_index)
        for digit_index, digit_value in enumerate(digits[:9])
    )
    # 9*10 + 4*9 + 3*8 + 4*7 + 7*6 + 6*5 + 5*4 + 9*3 + 1*2
    # = 90 + 36 + 24 + 28 + 42 + 30 + 20 + 27 + 2 = 299
    assert weighted_sum == 299
    
    # check digit
    calculated_check_digit = (11 - (weighted_sum % 11)) % 11
    # (11 - (299 % 11)) % 11 = (11 - 2) % 11 = 9
    
    assert calculated_check_digit == 9
   
    # matches the actual check digit and is not 10
    assert calculated_check_digit != 10
     # TODO: check if the following step/check is correct as wording is a bit confusing STEP 5
    assert calculated_check_digit == digits[9]
    

    assert validate_nhs_number_checksum("9434765919")


def test_nhs_special_cases():
    """Test NHS number special cases (check digit 0 and invalid 10)."""
    # Test case where check digit is 0 (valid case)
    # "0000000000" has weighted sum = 0, so (11-0)%11 = 0, which matches check digit 0
    assert validate_nhs_number_checksum("0000000000")
    
    # Test a known invalid number
    assert not validate_nhs_number_checksum("1234567891")  # Wrong check digit




def test_valid_postcode_formats():
    """Test all valid UK postcode formats."""
    valid_postcodes = ["SW1A 1AA", "W1A 0AX", "EC1A 1BB", "M1A 1AA", "B33 8TH", "M1 1AA", "B1 1HQ", "L1 8JQ",
        "M60 1NW", "B99 1TL", "CR0 2YR", "DN1 3XX", "DN55 1PT", "W1T 3NF",
    ]
    
    for postcode in valid_postcodes:
        assert validate_uk_postcode_format(postcode), f"Postcode {postcode} should be valid"


def test_invalid_postcode_formats():
    """Test invalid postcode formats."""
    invalid_postcodes = [
        "",           # Empty
        "A",          # Too short
        "A1",         # Too short
        "A1 1",       # Too short
        "AA1A 1AAA",  # Too long
        "1A1 1AA",    # Starts with number
        "AA1A 1A1",   # Invalid inward code
        "AA1A A11",   # Invalid inward code
        "AAAA 1AA",   # Too many letters in area
    ]
    
    for postcode in invalid_postcodes:
        assert not validate_uk_postcode_format(postcode), f"Postcode {postcode} should be invalid"


def test_postcode_case_insensitive():
    """Test postcode validation is case insensitive."""
    assert validate_uk_postcode_format("sw1a 1aa")
    assert validate_uk_postcode_format("SW1A 1AA")
    assert validate_uk_postcode_format("Sw1A 1aA")


def test_postcode_with_no_spaces():
    """Test postcodes without spaces are handled."""
    assert validate_uk_postcode_format("SW1A1AA")
    assert validate_uk_postcode_format("M11AA")
    assert validate_uk_postcode_format("B331HQ")


def test_format_uk_postcode_valid():
    """Test formatting valid postcodes."""
    test_cases = [
        ("SW1A1AA", "SW1A 1AA"),
        ("sw1a1aa", "SW1A 1AA"),
        ("SW1A 1AA", "SW1A 1AA"),
        ("  sw1a 1aa  ", "SW1A 1AA"),
        ("M11AA", "M1 1AA"),
        ("B331HQ", "B33 1HQ"),
    ]
    
    for input_postcode, expected in test_cases:
        result = format_uk_postcode(input_postcode)
        assert result == expected, f"Expected {expected}, got {result}"


def test_format_uk_postcode_invalid():
    """Test formatting invalid postcodes returns None."""
    invalid_postcodes = [
        "", "A", "1A1 1AA", "AA1A 1A1", None
    ]
    
    for postcode in invalid_postcodes:
        assert format_uk_postcode(postcode) is None



def test_nhs_number_none_and_empty():
    """Test NHS number validation with None and empty values."""
    assert not validate_nhs_number_checksum("")
    assert format_nhs_number("") is None
    assert format_nhs_number(None) is None


def test_postcode_none_and_empty():
    """Test postcode validation with None and empty values."""
    assert not validate_uk_postcode_format("")
    assert not validate_uk_postcode_format(None)
    assert format_uk_postcode("") is None
    assert format_uk_postcode(None) is None


def test_whitespace_handling():
    """Test handling of various whitespace characters."""
    assert validate_nhs_number_checksum("  9434765919  ")
    assert format_nhs_number("\t9434765919\n") == "9434765919"

    assert validate_uk_postcode_format("  SW1A 1AA  ")
    
    assert format_uk_postcode("SW1A1AA") == "SW1A 1AA"


def test_special_characters():
    """Test handling of special characters."""
    assert validate_nhs_number_checksum("943-476-5919")
    assert validate_nhs_number_checksum("943.476.5919") 
    
    assert not validate_uk_postcode_format("SW1A-1AA")
    assert not validate_uk_postcode_format("SW1A.1AA")