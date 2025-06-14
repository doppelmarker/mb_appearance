#!/usr/bin/env python3
"""Extract face keys in their exact order from skins.txt"""

# The face keys in the exact order they appear in skins.txt
# This order determines the morph_key_XX mapping
face_keys_in_order = [
    ('skinkey_chin_size', 'Chin_Size'),
    ('skinkey_chin_shape', 'Chin_Shape'),
    ('skinkey_chin_forward', 'Chin_Forward'),
    ('skinkey_jaw_width', 'Jaw_Width'),
    ('skinkey_jaw_position', 'Jaw_Position'),
    ('skinkey_mouth_nose_distance', 'Mouth-Nose_Distance'),
    ('skinkey_mouth_width', 'Mouth_Width'),
    ('skinkey_cheeks', 'Cheeks'),
    ('skinkey_nose_height', 'Nose_Height'),
    ('skinkey_nose_width', 'Nose_Width'),
    ('skinkey_nose_size', 'Nose_Size'),
    ('skinkey_nose_shape', 'Nose_Shape'),
    ('skinkey_nose_bridge', 'Nose_Bridge'),
    ('skinkey_cheek_bones', 'Cheek_Bones'),
    ('skinkey_eye_width', 'Eye_Width'),
    ('skinkey_eye_to_eye_dist', 'Eye_to_Eye_Dist'),
    ('skinkey_eye_shape', 'Eye_Shape'),
    ('skinkey_eye_depth', 'Eye_Depth'),
    ('skinkey_eyelids', 'Eyelids'),
    ('skinkey_eyebrow_position', 'Eyebrow_Position'),
    ('skinkey_eyebrow_height', 'Eyebrow_Height'),
    ('skinkey_eyebrow_depth', 'Eyebrow_Depth'),
    ('skinkey_eyebrow_shape', 'Eyebrow_Shape'),
    ('skinkey_temple_width', 'Temple_Width'),
    ('skinkey_face_depth', 'Face_Depth'),
    ('skinkey_face_ratio', 'Face_Ratio'),
    ('skinkey_face_width', 'Face_Width'),
    ('skinkey_post_edit', 'Post-Edit'),
]

# Our slider index mapping based on the order in MorphControls.js
slider_names = [
    'Face Width',           # 0
    'Face Ratio',          # 1
    'Face Depth',          # 2
    'Temple Width',        # 3
    'Eyebrow Shape',       # 4
    'Eyebrow Depth',       # 5
    'Eyebrow Height',      # 6
    'Eyebrow Position',    # 7
    'Eyelids',            # 8
    'Eye Depth',          # 9
    'Eye Shape',          # 10
    'Eye to Eye Dist',    # 11
    'Eye Width',          # 12
    'Cheek Bones',        # 13
    'Nose Bridge',        # 14
    'Nose Shape',         # 15
    'Nose Size',          # 16
    'Nose Width',         # 17
    'Nose Height',        # 18
    'Cheeks',             # 19
    'Mouth Width',        # 20
    'Mouth-Nose Distance', # 21
    'Jaw Position',       # 22
    'Jaw Width',          # 23
    'Chin Forward',       # 24
    'Chin Shape',         # 25
    'Chin Size',          # 26
]

print("CRITICAL DISCOVERY:")
print("==================")
print("In skins.txt, the face keys are listed in the EXACT ORDER")
print("that corresponds to morph_key_00 through morph_key_27!")
print()
print("morph_key_00 = Chin Size (first in skins.txt)")
print("morph_key_01 = Chin Shape (second in skins.txt)")
print("... and so on")
print()

print("\nCorrect morphKeyToSliderMapping for FaceCodeParser.js:")
print("static morphKeyToSliderMapping = {")

for morph_idx, (key_name, display_name) in enumerate(face_keys_in_order[:27]):  # Only first 27, post_edit is special
    # Find which slider index this should map to
    slider_idx = None
    for idx, slider_name in enumerate(slider_names):
        if slider_name.replace('-', ' ').replace(' ', '').lower() == display_name.replace('_', '').replace('-', '').replace(' ', '').lower():
            slider_idx = idx
            break
    
    if slider_idx is not None:
        print(f"    {morph_idx}: {slider_idx},    // morph_key_{morph_idx:02d} -> '{slider_names[slider_idx]}'")
    else:
        print(f"    // {morph_idx}: ???,    // morph_key_{morph_idx:02d} -> '{display_name}' (NOT FOUND)")

print("};")

print("\n\nReverse mapping (sliderToMorphKeyMapping):")
print("static sliderToMorphKeyMapping = {")

# Create reverse mapping
morph_to_slider = {}
for morph_idx, (key_name, display_name) in enumerate(face_keys_in_order[:27]):
    for idx, slider_name in enumerate(slider_names):
        if slider_name.replace('-', ' ').lower() == display_name.replace('_', ' ').lower():
            morph_to_slider[morph_idx] = idx
            break

# Print reverse mapping
for slider_idx in range(27):
    morph_key = None
    for m_idx, s_idx in morph_to_slider.items():
        if s_idx == slider_idx:
            morph_key = m_idx
            break
    
    if morph_key is not None:
        print(f"    {slider_idx}: {morph_key},    // '{slider_names[slider_idx]}' -> morph_key_{morph_key:02d}")
    else:
        print(f"    // {slider_idx}: ???,    // '{slider_names[slider_idx]}' (NO MORPH KEY)")

print("};")