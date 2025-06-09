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

## In Progress 🚧

### Face Morphing System
- [ ] Implement actual mesh deformation based on morph values
- [ ] Connect sliders to face code values
- [ ] Parse and apply Mount & Blade face codes

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