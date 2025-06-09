# Mount & Blade Warband Face Editor - Frontend MVP

A minimal viable product for displaying and editing Mount & Blade Warband character faces in the browser using Three.js.

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

The app will open automatically at http://localhost:3000

## Features

- **3D Face Rendering**: Displays a head model (procedural fallback if no assets)
- **8 Morph Sliders**: Control facial features (chin, nose, cheeks, etc.)
- **Face Code Support**: Import/export M&B face codes
- **Skin Tone Switching**: Change between light, tan, and dark skin
- **Test Face Codes**: Pre-defined examples to test morphing

## Current Status

This is an MVP that demonstrates:
1. ✅ 3D head rendering with Three.js
2. ✅ Morph target system (synthetic if no real morphs)
3. ✅ Face code parsing and generation
4. ✅ Interactive UI controls
5. ✅ Fallback system when assets are missing

## Adding Real Assets

To use actual M&B assets:
1. Extract head models from `meshes_face_gen.brf` using OpenBRF
2. Convert to GLB format with morph targets
3. Place in `src/assets/models/head_morphs.glb`
4. Extract face textures and place in `src/assets/textures/`

See `src/assets/README.md` for detailed instructions.

## Architecture

- `main.js` - Three.js scene setup and initialization
- `FaceViewer.js` - 3D model loading and rendering
- `MorphControls.js` - UI controls and face code interface
- `FaceCodeParser.js` - Face code encoding/decoding logic

## Next Steps

1. Extract real game assets
2. Implement all 43 morphs
3. Add hair/beard mesh switching
4. Connect to backend API
5. Add WebSocket for real-time updates