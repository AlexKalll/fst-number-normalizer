import pytest
import sys
import os

# Add project root to Python path for direct execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.normalize import normalize_text


@pytest.mark.parametrize(
    "inp,exp",
    [
        # Basic single digits
        ("I have 3 dogs", "I have three dogs"),
        ("The number is 0.", "The number is zero."),
        ("Count to 9.", "Count to nine."),
        
        # Teens
        ("She is 10 years old.", "She is ten years old."),
        ("I have 15 apples.", "I have fifteen apples."),
        ("The answer is 19.", "The answer is nineteen."),
        
        # Two-digit numbers (multiples of 10)
        ("He is 20 years old.", "He is twenty years old."),
        ("The price is 50 dollars.", "The price is fifty dollars."),
        ("I have 90 items.", "I have ninety items."),
        
        # Two-digit numbers (hyphenated)
        ("She is 21 years old.", "She is twenty-one years old."),
        ("I have 45 books.", "I have forty-five books."),
        ("The number is 99.", "The number is ninety-nine."),
        
        # Hundreds (exact multiples)
        ("I have 100 dollars.", "I have one hundred dollars."),
        ("The count is 200.", "The count is two hundred."),
        ("She has 900 items.", "She has nine hundred items."),
        
        # Hundreds with single digit remainder
        ("I have 101 dollars.", "I have one hundred one dollars."),
        ("The number is 205.", "The number is two hundred five."),
        ("She has 909 items.", "She has nine hundred nine items."),
        
        # Hundreds with teens remainder
        ("I have 110 dollars.", "I have one hundred ten dollars."),
        ("The number is 215.", "The number is two hundred fifteen."),
        ("She has 919 items.", "She has nine hundred nineteen items."),
        
        # Hundreds with tens remainder
        ("I have 120 dollars.", "I have one hundred twenty dollars."),
        ("The number is 245.", "The number is two hundred forty-five."),
        ("She has 999 items.", "She has nine hundred ninety-nine items."),
        
        # Special case: 1000
        ("The year is 1000.", "The year is one thousand."),
        ("I have 1000 books.", "I have one thousand books."),
        
        # Multiple numbers in text
        ("I have 3 dogs and 21 cats.", "I have three dogs and twenty-one cats."),
        ("She is 25 years old and has 100 dollars.", "She is twenty-five years old and has one hundred dollars."),
        ("Zero to 1000: 0 1 10 15 20 45 100 101 999 1000",
         "Zero to one thousand: zero one ten fifteen twenty forty-five one hundred one hundred one nine hundred ninety-nine one thousand"),
        
        # Edge cases
        ("No numbers here.", "No numbers here."),
        ("The number 1001 is too large.", "The number 1001 is too large."),  # Outside range
        ("I have -5 apples.", "I have -5 apples."),  # Negative (outside range)
        ("The code is 0123.", "The code is 0123."),  # Leading zero (preserved)
        
        # Boundary cases
        ("The minimum is 0.", "The minimum is zero."),
        ("The maximum is 1000.", "The maximum is one thousand."),
        ("Numbers: 0, 1, 99, 100, 999, 1000.", "Numbers: zero, one, ninety-nine, one hundred, nine hundred ninety-nine, one thousand."),
    ],
)
def test_basic_numbers(inp, exp):
    """Test number normalization with various inputs."""
    out = normalize_text(inp)
    assert out == exp, f"Expected '{exp}', got '{out}'"


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # Empty string
    assert normalize_text("") == ""
    
    # Only numbers
    assert normalize_text("0") == "zero"
    assert normalize_text("1000") == "one thousand"
    
    # Numbers at word boundaries
    assert normalize_text("a0b") == "a0b"  # Not a word boundary (0 inside word)
    assert normalize_text("0abc") == "0abc"  # No word boundary between 0 and abc
    assert normalize_text("abc0") == "abc0"  # No word boundary between abc and 0
    assert normalize_text("0 abc") == "zero abc"  # Word boundary with space
    assert normalize_text("abc 0") == "abc zero"  # Word boundary with space

