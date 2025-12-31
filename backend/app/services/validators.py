"""
Validation functions for onboarding data.
Each validator checks and formats user input for specific data types.
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


def validate_email(email: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, cleaned_email, error_message)
    """
    email = email.strip().lower()
    
    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, None, "Please provide a valid email address (e.g., info@practice.com)"
    
    return True, email, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate and format phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, formatted_phone, error_message)
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if we have 10 or 11 digits
    if len(digits) == 10:
        formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return True, formatted, None
    elif len(digits) == 11 and digits[0] == '1':
        formatted = f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return True, formatted, None
    else:
        return False, None, "Please provide a valid 10-digit phone number"


def validate_url(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, cleaned_url, error_message)
    """
    url = url.strip()
    
    # Add https:// if no protocol specified
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return True, url, None
        else:
            return False, None, "Please provide a valid URL (e.g., https://practice.com)"
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return False, None, "Please provide a valid URL"


def validate_hex_color(color: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate hex color code.
    
    Args:
        color: Color code to validate
        
    Returns:
        Tuple of (is_valid, formatted_color, error_message)
    """
    color = color.strip()
    
    # Add # if not present
    if not color.startswith('#'):
        color = f'#{color}'
    
    # Validate hex format
    if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):
        # Convert short form to long form
        if len(color) == 4:
            color = f'#{color[1]}{color[1]}{color[2]}{color[2]}{color[3]}{color[3]}'
        return True, color.upper(), None
    else:
        return False, None, "Please provide a valid hex color code (e.g., #FF5733 or #F57)"


def validate_state_code(state: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate US state code.
    
    Args:
        state: State code to validate
        
    Returns:
        Tuple of (is_valid, uppercase_state, error_message)
    """
    state = state.strip().upper()
    
    # List of valid US state codes
    valid_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC', 'PR', 'VI', 'GU', 'AS', 'MP'
    }
    
    if state in valid_states:
        return True, state, None
    else:
        return False, None, "Please provide a valid two-letter state code (e.g., CA, NY)"


def validate_zip_code(zip_code: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate ZIP code.
    
    Args:
        zip_code: ZIP code to validate
        
    Returns:
        Tuple of (is_valid, formatted_zip, error_message)
    """
    # Remove spaces and dashes
    clean_zip = zip_code.replace(' ', '').replace('-', '')
    
    if re.match(r'^\d{5}$', clean_zip):
        return True, clean_zip, None
    elif re.match(r'^\d{9}$', clean_zip):
        formatted = f"{clean_zip[:5]}-{clean_zip[5:]}"
        return True, formatted, None
    else:
        return False, None, "Please provide a valid 5-digit ZIP code"


def validate_terminology(term: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate terminology preference.
    
    Args:
        term: Terminology to validate
        
    Returns:
        Tuple of (is_valid, validated_term, error_message)
    """
    term = term.strip().lower()
    
    valid_terms = ['patients', 'members', 'clients']
    
    # Try to match partial input
    matches = [t for t in valid_terms if t.startswith(term) or term in t]
    
    if len(matches) == 1:
        return True, matches[0], None
    elif len(matches) > 1:
        return False, None, f"Did you mean one of these? {', '.join(matches)}"
    else:
        return False, None, "Please choose: 'patients', 'members', or 'clients'"


def parse_address(address_text: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Parse free-form address text into structured components.
    
    Args:
        address_text: Free-form address string
        
    Returns:
        Tuple of (is_valid, address_dict, error_message)
    """
    lines = [line.strip() for line in address_text.strip().split('\n') if line.strip()]
    
    if len(lines) < 2:
        return False, None, "Please provide the full address including street, city, state, and ZIP code"
    
    # Try to parse the last line as "City, State ZIP"
    last_line = lines[-1]
    
    # Pattern: "City, ST ZIP" or "City, ST ZIP-XXXX"
    pattern = r'^(.+),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)$'
    match = re.match(pattern, last_line, re.IGNORECASE)
    
    if match:
        city = match.group(1).strip()
        state = match.group(2).upper()
        zip_code = match.group(3)
        street = ' '.join(lines[:-1])
        
        # Validate state
        is_valid_state, validated_state, _ = validate_state_code(state)
        if not is_valid_state:
            return False, None, "Invalid state code in address"
        
        address_dict = {
            'street': street,
            'city': city,
            'state': validated_state,
            'zip': zip_code
        }
        
        return True, address_dict, None
    else:
        return False, None, "Please format the address as: Street, City, State ZIP (e.g., 123 Main St, Los Angeles, CA 90210)"


def parse_social_links(text: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Parse social media links from text.
    
    Args:
        text: Text containing social media URLs
        
    Returns:
        Tuple of (is_valid, social_links_dict, error_message)
    """
    if text.lower() in ['none', 'no', 'n/a', 'na', 'skip']:
        return True, {}, None
    
    # Extract URLs from text
    url_pattern = r'https?://(?:www\.)?[\w\-\.]+\.[\w\-\.]+/?[^\s]*'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    
    if not urls:
        # Maybe user provided just usernames or domains
        return False, None, "Please provide full URLs (e.g., https://facebook.com/yourpage). If you don't have any, type 'none'"
    
    social_links = {}
    platforms = {
        'facebook': ['facebook.com', 'fb.com'],
        'instagram': ['instagram.com'],
        'linkedin': ['linkedin.com'],
        'twitter': ['twitter.com', 'x.com']
    }
    
    for url in urls:
        url_lower = url.lower()
        for platform, domains in platforms.items():
            if any(domain in url_lower for domain in domains):
                social_links[platform] = url
                break
    
    if not social_links:
        return False, None, "I couldn't identify the social media platforms. Please provide URLs for Facebook, Instagram, LinkedIn, or Twitter"
    
    return True, social_links, None


def parse_brand_colors(text: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Parse brand colors from text.
    
    Args:
        text: Text describing or containing color codes
        
    Returns:
        Tuple of (is_valid, colors_dict, error_message)
    """
    # Extract hex codes
    hex_pattern = r'#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})\b'
    hex_codes = re.findall(hex_pattern, text)
    
    if len(hex_codes) >= 2:
        # Validate and format
        is_valid_1, color_1, _ = validate_hex_color(hex_codes[0])
        is_valid_2, color_2, _ = validate_hex_color(hex_codes[1])
        
        if is_valid_1 and is_valid_2:
            return True, {'primary': color_1, 'secondary': color_2}, None
    
    # If not enough hex codes, ask for clarification
    if len(hex_codes) == 1:
        return False, None, "I found one color. Please provide both primary and secondary colors in hex format (e.g., #FF5733 #0066CC)"
    else:
        return False, None, "Please provide two colors in hex format (e.g., #FF5733 for primary and #0066CC for secondary)"


def parse_business_goals(text: str) -> Tuple[bool, Optional[list], Optional[str]]:
    """
    Parse business goals from text.
    
    Args:
        text: Text containing business goals
        
    Returns:
        Tuple of (is_valid, goals_list, error_message)
    """
    # Split by common separators
    separators = ['\n', ';', '|']
    goals = [text]
    
    for sep in separators:
        if sep in text:
            goals = [g.strip() for g in text.split(sep) if g.strip()]
            break
    
    # If still one item, try to split by numbered list
    if len(goals) == 1:
        # Pattern for numbered lists: "1. Goal", "1) Goal", etc.
        numbered = re.split(r'\d+[\.\)]\s+', text)
        numbered = [g.strip() for g in numbered if g.strip()]
        if len(numbered) > 1:
            goals = numbered
    
    # Filter and clean
    goals = [g.strip().rstrip('.,;') for g in goals if g.strip()]
    
    if not goals:
        return False, None, "Please provide at least one business goal"
    
    if len(goals) > 5:
        return False, None, "Please provide your top 3-5 business goals"
    
    return True, goals, None


def validate_text(text: str, min_length: int = 1, max_length: int = 500) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate general text input.
    
    Args:
        text: Text to validate
        min_length: Minimum length (default 1)
        max_length: Maximum length (default 500)
        
    Returns:
        Tuple of (is_valid, cleaned_text, error_message)
    """
    text = text.strip()
    
    if len(text) < min_length:
        return False, None, f"Please provide at least {min_length} character(s)"
    
    if len(text) > max_length:
        return False, None, f"Please keep your answer under {max_length} characters"
    
    return True, text, None


def validate_boolean(text: str) -> Tuple[bool, Optional[bool], Optional[str]]:
    """
    Validate Yes/No response.
    
    Args:
        text: User's response
        
    Returns:
        Tuple of (is_valid, boolean_value, error_message)
    """
    text = text.strip().lower()
    
    yes_responses = ['yes', 'y', 'yeah', 'yep', 'sure', 'ok', 'okay', 'true', '1']
    no_responses = ['no', 'n', 'nope', 'nah', 'false', '0']
    
    if text in yes_responses:
        return True, True, None
    elif text in no_responses:
        return True, False, None
    else:
        return False, None, "Please answer with 'Yes' or 'No'"


def validate_choice(text: str, valid_options: list) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate multiple choice response.
    
    Args:
        text: User's response
        valid_options: List of valid option strings
        
    Returns:
        Tuple of (is_valid, selected_option, error_message)
    """
    text = text.strip()
    
    # Try exact match first
    for option in valid_options:
        if text.lower() == option.lower():
            return True, option, None
    
    # Try partial match
    for option in valid_options:
        if text.lower() in option.lower() or option.lower() in text.lower():
            return True, option, None
    
    options_str = ", ".join(valid_options)
    return False, None, f"Please choose from: {options_str}"


def validate_multi_select(text: str, valid_options: list) -> Tuple[bool, Optional[list], Optional[str]]:
    """
    Validate multi-select response.
    
    Args:
        text: User's response (comma-separated or line-separated)
        valid_options: List of valid option strings
        
    Returns:
        Tuple of (is_valid, selected_options_list, error_message)
    """
    text = text.strip()
    
    # Handle "none" or "no" responses
    if text.lower() in ['none', 'no', 'n/a', 'na']:
        return True, ['None'], None
    
    # Split by comma, semicolon, or newline
    if ',' in text:
        selections = [s.strip() for s in text.split(',')]
    elif ';' in text:
        selections = [s.strip() for s in text.split(';')]
    elif '\n' in text:
        selections = [s.strip() for s in text.split('\n')]
    else:
        selections = [text.strip()]
    
    matched_options = []
    
    for selection in selections:
        matched = False
        for option in valid_options:
            if selection.lower() == option.lower() or selection.lower() in option.lower():
                if option not in matched_options:
                    matched_options.append(option)
                matched = True
                break
        
        if not matched and selection.lower() not in ['none', '']:
            options_str = ", ".join(valid_options)
            return False, None, f"'{selection}' is not a valid option. Please choose from: {options_str}"
    
    if not matched_options:
        options_str = ", ".join(valid_options)
        return False, None, f"Please select at least one option from: {options_str}"
    
    return True, matched_options, None


def validate_scale(text: str, min_val: int = 1, max_val: int = 5) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validate scale response (e.g., 1-5).
    
    Args:
        text: User's response
        min_val: Minimum value (default 1)
        max_val: Maximum value (default 5)
        
    Returns:
        Tuple of (is_valid, integer_value, error_message)
    """
    text = text.strip()
    
    try:
        value = int(text)
        if min_val <= value <= max_val:
            return True, value, None
        else:
            return False, None, f"Please enter a number between {min_val} and {max_val}"
    except ValueError:
        return False, None, f"Please enter a number between {min_val} and {max_val}"
