#!/usr/bin/env python3
"""
Example of using mb-app as a library for face code manipulation.

This demonstrates how the warband-face-editor web service could use mb-app.
"""

from appearance.service import list_characters
from appearance.face_code import extract_face_code, apply_face_code, validate_face_code

def main():
    # Example 1: List characters with face codes
    print("=== Listing characters with face codes ===")
    characters = list_characters()
    for char in characters[:3]:  # Show first 3
        print(f"Character: {char['name']}")
        print(f"  Index: {char['index']}")
        print(f"  Sex: {char['sex']}")
        print(f"  Face Code: {char.get('face_code', 'N/A')}")
        print()
    
    # Example 2: Validate a face code
    print("=== Validating face codes ===")
    test_codes = [
        "0000000fee00300036625399b567e20800000000001fe8ba0000000000000000",  # Valid
        "0xinvalidcode",  # Invalid
        "0000000fee003000"  # Too short
    ]
    
    for code in test_codes:
        is_valid = validate_face_code(code)
        print(f"Face code: {code[:20]}... is {'valid' if is_valid else 'invalid'}")
    
    # Example 3: Extract face code from raw character data
    print("\n=== Direct face code extraction ===")
    # This would be used when reading profiles.dat directly
    # Here we'll use the test data from our unit test
    test_char_data = bytes.fromhex(
        "0100000061010000" +  # name length + name start
        "00ffffffff003000ee0f000000" +  # banner + appearance start
        "08e267b599536236bae81f0000000000000000000000000000000000000000" +  # appearance
        "000000000000"  # padding
    )
    
    face_code = extract_face_code(test_char_data, char_offset=0)
    print(f"Extracted face code: {face_code}")
    
    # Example 4: Apply a face code to character data
    print("\n=== Applying face code ===")
    new_face_code = "0000000fee00300036625399b567e20800000000001fe8ba0000000000000000"
    
    # Apply the face code
    modified_data = apply_face_code(test_char_data, new_face_code, char_offset=0)
    
    # Extract it back to verify
    verified_code = extract_face_code(modified_data, char_offset=0)
    print(f"Applied face code:  {new_face_code}")
    print(f"Verified extraction: {verified_code}")
    print(f"Match: {new_face_code == verified_code}")


if __name__ == "__main__":
    main()