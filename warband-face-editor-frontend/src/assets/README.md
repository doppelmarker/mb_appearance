# Game Assets Directory

This directory should contain the extracted Mount & Blade Warband face assets:

## Models (place in `/models/`)
- `head_base.glb` - Base head mesh without morph targets
- `head_morphs.glb` - Head mesh with 8+ morph targets (blend shapes)

## Textures (place in `/textures/`)
- `face_white.png` - Light skin tone texture
- `face_tan.png` - Tan skin tone texture  
- `face_dark.png` - Dark skin tone texture

## How to Extract Assets

### Using OpenBRF:
1. Download OpenBRF from: http://www.taleworlds.com/en/Games/Warband/Download
2. Open `meshes_face_gen.brf` from your M&B installation
3. Find head meshes (e.g., `head_male`, `head_female`)
4. Export as OBJ format
5. Convert to GLB using Blender or online converter

### Textures:
1. Open `textures_face_gen.brf` in OpenBRF
2. Export face textures as PNG
3. Name them according to skin tone

## Fallback
If no assets are present, the app will use a procedural head model with synthetic morphs.