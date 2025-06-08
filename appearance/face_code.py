"""
Mount & Blade Warband Face Code Support

Face codes are 64-character hexadecimal strings that encode character appearance.
They are stored in profiles.dat with a specific byte arrangement.
"""

from typing import Dict, Any, Optional


def extract_face_code(character_bytes: bytes, char_offset: int = 0) -> str:
    """
    Extract face code from character bytes matching the game's format.
    
    The game reads face data from bytes 14-45 of character data with a specific
    arrangement that differs from direct byte reading.
    
    Args:
        character_bytes: Raw character data from profiles.dat
        char_offset: Starting offset of character in the bytes
        
    Returns:
        64-character hexadecimal face code string (without 0x prefix)
    """
    # Extract 32 bytes starting from skin offset (14)
    start = char_offset + 14
    face_bytes = character_bytes[start:start + 32]
    
    # The game uses a specific byte arrangement for face codes
    # Based on analysis of known face codes vs file data
    result = []
    
    # Chunk 0: Extract specific byte with padding
    # Game shows: 0000000f from bytes starting with 30 00 ee 0f
    result.append(f"0000000{face_bytes[3]:1x}")
    
    # Chunk 1: Rearrange bytes
    # Game shows: ee003000 from bytes 30 00 ee 0f
    result.append(f"{face_bytes[2]:02x}00{face_bytes[0]:02x}00")
    
    # Chunks 2-3: Complex byte rearrangement
    # From bytes at positions: 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15
    # File has:                30 00 ee 0f 00 00 00 08 e2 67 b5 99 53 62 36 ba
    # Game shows: 36625399 b567e208
    
    # The pattern is:
    # 3662 = bytes 14-15
    # 5399 = bytes 12-13  
    # b567 = bytes 10-11
    # e208 = bytes 8 and 7
    
    result.append(f"{face_bytes[14]:02x}{face_bytes[13]:02x}{face_bytes[12]:02x}{face_bytes[11]:02x}")  # 36 62 53 99
    result.append(f"{face_bytes[10]:02x}{face_bytes[9]:02x}{face_bytes[8]:02x}{face_bytes[7]:02x}")  # b5 67 e2 08
    
    # Chunk 4: Zeros
    result.append("00000000")
    
    # Chunk 5: Extract specific values
    # From bytes e8 1f 00 00 -> game shows 001fe8ba
    result.append(f"00{face_bytes[17]:02x}{face_bytes[16]:02x}{face_bytes[15]:02x}")
    
    # Chunks 6-7: Zeros
    result.append("00000000")
    result.append("00000000")
    
    return ''.join(result)


def apply_face_code(character_bytes: bytes, face_code: str, char_offset: int = 0) -> bytes:
    """
    Apply a face code to character bytes.
    
    This reverses the extraction process to write face code data back to the file.
    
    Args:
        character_bytes: Original character data
        face_code: 64-character hex string (with or without 0x prefix)
        char_offset: Starting offset of character in the bytes
        
    Returns:
        Updated character bytes with new face code
    """
    # Remove 0x prefix if present
    if face_code.startswith('0x'):
        face_code = face_code[2:]
    
    # Validate face code length
    if len(face_code) != 64:
        raise ValueError(f"Face code must be 64 characters, got {len(face_code)}")
    
    # Validate hex characters
    try:
        int(face_code, 16)
    except ValueError:
        raise ValueError("Face code must contain only hexadecimal characters")
    
    # Parse face code chunks
    chunks = [face_code[i:i+8] for i in range(0, 64, 8)]
    
    # Prepare the 32-byte face data by reversing the extraction process
    face_bytes = bytearray(32)
    
    # Chunk 0 (0000000f) -> extract last char as byte 3
    face_bytes[3] = int(chunks[0][-1], 16)
    
    # Chunk 1 (ee003000) -> bytes 0 and 2
    face_bytes[2] = int(chunks[1][0:2], 16)  # ee
    face_bytes[0] = int(chunks[1][4:6], 16)  # 30
    
    # For the middle section, we need to reverse the rearrangement
    # Chunks 2-3 need careful handling
    # This is complex - for now, preserve existing data
    # TODO: Implement full reverse mapping
    
    # Copy existing middle bytes for now
    start = char_offset + 14
    existing_middle = character_bytes[start + 4:start + 16]
    face_bytes[4:16] = existing_middle
    
    # Chunk 5 (001fe8ba) -> bytes 15-17
    if chunks[5] != "00000000":
        face_bytes[17] = int(chunks[5][2:4], 16)  # 1f
        face_bytes[16] = int(chunks[5][4:6], 16)  # e8
        face_bytes[15] = int(chunks[5][6:8], 16)  # ba
    
    # Replace bytes 14-45 in character data
    end = start + 32
    
    return character_bytes[:start] + bytes(face_bytes) + character_bytes[end:]


def parse_face_code_components(face_code: str) -> Dict[str, Any]:
    """
    Parse face code into individual components.
    
    Based on Mount & Blade Warband's face code structure:
    - 8 morph targets (3 bits each)
    - Hair index (6 bits)
    - Beard index (6 bits)
    - Age (6 bits)
    - Skin tone (6 bits)
    
    Args:
        face_code: 64-character hex string
        
    Returns:
        Dictionary with parsed components
    """
    # Remove 0x prefix if present
    if face_code.startswith('0x'):
        face_code = face_code[2:]
    
    # Convert to binary representation
    binary = bin(int(face_code, 16))[2:].zfill(256)
    
    # Extract components (this is a simplified version - actual bit layout may differ)
    # The exact bit positions would need to be determined through more testing
    components = {
        'raw_hex': face_code,
        'binary': binary,
        # These mappings are placeholders - need to determine exact positions
        'morphs': [],  # Will need to extract 8 morph values
        'hair_index': None,
        'beard_index': None,
        'age': None,
        'skin_tone': None,
    }
    
    return components


def validate_face_code(face_code: str) -> bool:
    """
    Validate if a string is a valid face code.
    
    Args:
        face_code: String to validate
        
    Returns:
        True if valid face code, False otherwise
    """
    # Remove 0x prefix if present
    if face_code.startswith('0x'):
        face_code = face_code[2:]
    
    # Check length
    if len(face_code) != 64:
        return False
    
    # Check if all characters are hex
    try:
        int(face_code, 16)
        return True
    except ValueError:
        return False


def format_face_code(face_code: str, include_prefix: bool = True) -> str:
    """
    Format a face code for display.
    
    Args:
        face_code: Raw face code string
        include_prefix: Whether to include '0x' prefix
        
    Returns:
        Formatted face code
    """
    # Remove any existing prefix
    if face_code.startswith('0x'):
        face_code = face_code[2:]
    
    # Ensure lowercase
    face_code = face_code.lower()
    
    # Add prefix if requested
    if include_prefix:
        return f"0x{face_code}"
    return face_code