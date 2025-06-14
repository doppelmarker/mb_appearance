#!/usr/bin/env python3
"""Extract face keys in their exact order from skins.txt"""

with open('/home/devuser/mb_appearance/skins.txt', 'r') as f:
    content = f.read()

# Find the male_head line and extract face keys
lines = content.split('\n')
in_male_head = False
face_keys = []

for line in lines:
    if 'male_head 28' in line:
        # Parse the entire line - it contains all face keys on one line
        parts = line.split()
        i = 2  # Start after "male_head 28"
        while i < len(parts):
            if parts[i].startswith('skinkey_'):
                key_name = parts[i]
                key_index = int(parts[i+1])
                display_name = parts[i+6] if i+6 < len(parts) else ""
                face_keys.append((key_name, key_index, display_name))
                i += 7  # Move to next face key (7 fields per key)
            else:
                break
        break

# Print face keys in order they appear (which is morph key order)
print("Face keys in skins.txt order (morph_key_XX order):")
print("=" * 60)
for idx, (key_name, key_index, display_name) in enumerate(face_keys):
    print(f"morph_key_{idx:02d}: {key_name:30s} (index: {key_index:3d}) - {display_name}")

print("\n\nFor FaceCodeParser.js morphKeyToSliderMapping:")
print("{")
for idx, (key_name, key_index, display_name) in enumerate(face_keys):
    # Find slider index based on our slider names
    slider_idx = None
    clean_name = key_name.replace('skinkey_', '')
    
    # Map to slider indices based on display names
    slider_map = {
        'chin_size': 26,
        'chin_shape': 25, 
        'chin_forward': 24,
        'jaw_width': 23,
        'jaw_position': 22,
        'mouth_nose_distance': 21,
        'mouth_width': 20,
        'cheeks': 19,
        'nose_height': 18,
        'nose_width': 17,
        'nose_size': 16,
        'nose_shape': 15,
        'nose_bridge': 14,
        'cheek_bones': 13,
        'eye_width': 12,
        'eye_to_eye_dist': 11,
        'eye_shape': 10,
        'eye_depth': 9,
        'eyelids': 8,
        'eyebrow_position': 7,
        'eyebrow_height': 6,
        'eyebrow_depth': 5,
        'eyebrow_shape': 4,
        'temple_width': 3,
        'face_depth': 2,
        'face_ratio': 1,
        'face_width': 0,
        'post_edit': 27
    }
    
    if clean_name in slider_map:
        slider_idx = slider_map[clean_name]
        print(f"    {slider_idx}: {idx},  // '{display_name}' -> morph_key_{idx:02d}")