# Warband Face Editor Frontend - Backlog

## Completed Features ✅

### 1. Basic 3D Viewer Setup
- [x] Three.js scene with proper lighting
- [x] OrbitControls for camera manipulation
- [x] Responsive canvas that fills the viewport
- [x] Dark theme UI

### 2. OBJ Model Loading
- [x] Replaced GLTF loader with OBJ loader for Mount & Blade models
- [x] Successfully loading male and female head models from `/obj_files/`
- [x] Fixed model orientation (was showing top of head, now shows face)
- [x] Proper camera positioning and zoom level

### 3. Geometry Mirroring
- [x] Implemented full head creation from half-head OBJ models
- [x] Proper UV coordinate mirroring for texture mapping
- [x] Fixed normal calculations for proper lighting on both halves

### 4. DDS Texture Loading
- [x] Integrated DDSLoader for Mount & Blade texture format
- [x] Loading textures from `/dds_textures/` directory
- [x] Fixed upside-down texture issue by flipping UV coordinates

### 5. Gender System
- [x] Male/Female toggle buttons
- [x] Gender-specific model loading
- [x] Gender-specific texture sets
- [x] Smooth switching between genders with texture preservation

### 6. Advanced Skin System
- [x] Expanded from 3 basic tones to full texture variety:
  - **Male**: 8 skins (Young, Young Tan, Young Dark, Warrior, Middle Aged, Weathered, Rugged, African)
  - **Female**: 5 skins (Young, Pretty, Mature, Brown, African)
- [x] Dropdown UI with proper styling
- [x] Gender-aware skin selection that updates when switching
- [x] Default skin application on load

### 7. UI/UX Improvements
- [x] Fixed dropdown styling (all options visible with dark theme)
- [x] Proper lighting setup for face visibility
- [x] Info panel with instructions
- [x] Gender toggle buttons with active state
- [x] Skin type dropdown with hover effects

## Completed Features ✅ (continued)

### 8. Face Morphing System
- [x] Implemented mesh deformation with 8 core morph targets
- [x] Connected all 27 sliders to face code values
- [x] Full Mount & Blade face code parsing (27 morphs from 64-char hex)
- [x] Proper morph target deltas instead of absolute positions
- [x] Mapping system to connect 27 game sliders to 8 mesh morphs
- [x] Test face codes with proper extraction of all morph values

### 9. Complete UI System
- [x] All 27 face morphing sliders matching the game:
  - Face Width, Face Ratio, Face Depth, Temple Width
  - Eyebrow Shape/Depth/Height/Position
  - Eyelids, Eye Depth/Shape/Distance/Width
  - Cheek Bones, Nose Bridge/Shape/Size/Width/Height
  - Cheeks, Mouth Width, Mouth-Nose Distance
  - Jaw Position/Width, Chin Forward/Shape/Size
- [x] Scrollable controls panel with custom styling
- [x] Real-time face code generation
- [x] Apply face code functionality
- [x] Randomize button with bell-curve distribution for natural-looking faces

### 10. Real Morph Data from MD3 Files
- [x] MD3 loader implementation for Three.js
- [x] Extract vertex animation frames as morph targets
- [x] Load male_head.MD3 and female_head.MD3 with real morphs
- [x] Map 27 sliders directly to MD3 vertex animation frames
- [x] Mirror geometry to create full head from half
- [x] Fix morphTargetsRelative for absolute vertex positions
- [x] Convert absolute morphs to relative deltas
- [x] Adjust MD3 model scale to match OBJ scale (50x)
- [x] Fix camera and model orientation for MD3
- [x] Create proper slider-to-frame mapping for morphs
- [x] Debug frame indexing (testing sequential 1-27)
- [x] 100% accurate face deformation matching Mount & Blade

## In Progress 🚧

### Advanced Mesh Morphing
- [ ] Create more sophisticated morph targets for better deformation
- [ ] Implement normal recalculation for smoother morphing
- [ ] Add more vertex regions for finer control

## Planned Features 📋

### 1. Face Code Integration
- [ ] Decode face codes like `00000000000000006c3199cc1bdc235500000000001c11810000000000000000`
- [ ] Map face code values to morph targets
- [ ] Real-time face updates from code changes
- [ ] Generate face codes from current morph values

### 2. Additional Assets
- [ ] Hair models (man_hair_*.obj, woman_hair_*.obj)
- [ ] Beard models (male_beard_*.obj)
- [ ] Proper texture mapping for all variations

### 3. Export/Import
- [ ] Save current face configuration
- [ ] Export face code for game use
- [ ] Import face codes from clipboard

### 4. Visual Enhancements
- [ ] Better lighting presets
- [ ] Background options
- [ ] Screenshot functionality

## Technical Debt 🔧

- [ ] Error handling for missing textures/models
- [ ] Loading states for assets
- [ ] Performance optimization for texture switching
- [ ] Mobile responsiveness

## Known Issues 🐛

- Face morphing sliders currently don't affect the mesh (synthetic morphs not working)
- Need to implement proper Mount & Blade face code parsing
- Some textures might not align perfectly with UV mapping