# Mount & Blade Warband Face Editor - Frontend MVP Implementation Guide

## Context for LLMs

This document provides a sequential implementation plan for creating a minimal viable product (MVP) that displays a Mount & Blade Warband character face in a web browser using Three.js. The goal is to validate the technical feasibility before building complex backend integrations.

**Key Principle**: Start with hardcoded assets and static data, then progressively add dynamic features.

## MVP Goals

1. **Prove we can render M&B faces in browser** - Display a static 3D head model
2. **Test morph target system** - Verify blend shapes work with M&B face data  
3. **Validate texture switching** - Show different skin tones
4. **Confirm performance** - Ensure smooth rendering on average hardware

## Project Structure

```
warband-face-editor-frontend/
├── index.html              # Simple HTML entry point
├── src/
│   ├── main.js            # Entry point, Three.js setup
│   ├── FaceViewer.js      # Core 3D face rendering class
│   ├── MorphControls.js   # UI sliders for morphs
│   └── assets/            # Manually extracted game assets
│       ├── models/
│       │   ├── head_base.glb        # Base head mesh
│       │   └── head_morphs.glb      # Head with morph targets
│       └── textures/
│           ├── face_white.png       # Skin tone variations
│           ├── face_tan.png
│           └── face_dark.png
├── public/                # Static assets
└── package.json          # Dependencies
```

## Sequential Implementation Tasks

### Phase 1: Basic 3D Viewer (Day 1)

**Goal**: Display ANY 3D head model in the browser

#### Task 1.1: Project Setup
```bash
# Create project structure
mkdir warband-face-editor-frontend
cd warband-face-editor-frontend
npm init -y

# Install minimal dependencies
npm install three vite

# Create basic file structure
mkdir -p src/assets/{models,textures} public
```

#### Task 1.2: Minimal HTML + Three.js Scene
Create `index.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>M&B Face Editor MVP</title>
    <style>
        body { margin: 0; overflow: hidden; }
        #canvas { width: 100vw; height: 100vh; }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <script type="module" src="/src/main.js"></script>
</body>
</html>
```

Create `src/main.js`:
```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// Basic Three.js setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });

renderer.setSize(window.innerWidth, window.innerHeight);
camera.position.set(0, 0, 5);

// Add lighting
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(0, 1, 1);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));

// Add controls
const controls = new OrbitControls(camera, renderer.domElement);

// TEMPORARY: Add a cube to test the scene
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Render loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();
```

**Success Criteria**: See a rotating green cube in the browser

### Phase 2: Manual Asset Extraction (Day 1-2)

**Goal**: Extract ONE head model from M&B files

#### Task 2.1: Extract Base Head Mesh
```bash
# Using OpenBRF (manual process):
# 1. Open meshes_face_gen.brf in OpenBRF
# 2. Find "head_male" or similar mesh
# 3. Export as OBJ
# 4. Convert to GLB using Blender or online converter
# 5. Place in src/assets/models/head_base.glb
```

#### Task 2.2: Extract One Face Texture
```bash
# Using OpenBRF:
# 1. Open textures_face_gen.brf
# 2. Export one face texture as PNG
# 3. Place in src/assets/textures/face_white.png
```

#### Task 2.3: Create FaceViewer Class
Create `src/FaceViewer.js`:
```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

export class FaceViewer {
    constructor(scene) {
        this.scene = scene;
        this.headMesh = null;
        this.loader = new GLTFLoader();
    }

    async loadHead() {
        try {
            // Load the manually extracted head model
            const gltf = await this.loader.loadAsync('/src/assets/models/head_base.glb');
            this.headMesh = gltf.scene.children[0];
            
            // Apply basic material with texture
            const texture = new THREE.TextureLoader().load('/src/assets/textures/face_white.png');
            this.headMesh.material = new THREE.MeshPhongMaterial({ map: texture });
            
            this.scene.add(this.headMesh);
            return true;
        } catch (error) {
            console.error('Failed to load head model:', error);
            // FALLBACK: Create a sphere as placeholder
            const geometry = new THREE.SphereGeometry(1, 32, 32);
            const material = new THREE.MeshPhongMaterial({ color: 0xffdbac });
            this.headMesh = new THREE.Mesh(geometry, material);
            this.scene.add(this.headMesh);
            return false;
        }
    }
}
```

Update `src/main.js`:
```javascript
import { FaceViewer } from './FaceViewer.js';

// ... previous setup code ...

// Remove the cube, add face viewer
const faceViewer = new FaceViewer(scene);
await faceViewer.loadHead();
```

**Success Criteria**: See a 3D head (or sphere fallback) with texture

### Phase 3: Add Morph Targets (Day 2-3)

**Goal**: Test blend shape morphing

#### Task 3.1: Extract Head with Morphs
```bash
# More complex extraction:
# 1. In OpenBRF, find morph variations (chin_size, nose_length, etc)
# 2. Export base + 8 morph targets as separate OBJ files
# 3. Use Blender to combine into single GLB with shape keys
# 4. Save as head_morphs.glb
```

#### Task 3.2: Fallback Morph Generation
If extraction is too complex, create synthetic morphs:
```javascript
// In FaceViewer.js - add synthetic morph targets
createSyntheticMorphs() {
    if (!this.headMesh || !this.headMesh.geometry) return;
    
    const geometry = this.headMesh.geometry;
    const position = geometry.attributes.position;
    
    // Create simple morph targets for testing
    const morphTargets = [];
    
    // Morph 1: Bigger chin (move bottom vertices down)
    const chinMorph = new Float32Array(position.count * 3);
    for (let i = 0; i < position.count; i++) {
        const y = position.getY(i);
        if (y < -0.5) { // Bottom part of head
            chinMorph[i * 3] = 0;
            chinMorph[i * 3 + 1] = -0.2; // Move down
            chinMorph[i * 3 + 2] = 0;
        }
    }
    morphTargets.push({ name: 'chin_size', array: chinMorph });
    
    // Add more synthetic morphs...
    
    // Apply morph attributes
    morphTargets.forEach((target, index) => {
        geometry.setAttribute(`morphTarget${index}`, 
            new THREE.BufferAttribute(target.array, 3));
    });
    
    geometry.morphAttributes.position = morphTargets.map((t, i) => 
        geometry.getAttribute(`morphTarget${i}`));
    
    this.headMesh.morphTargetInfluences = new Array(morphTargets.length).fill(0);
}
```

#### Task 3.3: Create Morph Controls UI
Create `src/MorphControls.js`:
```javascript
export class MorphControls {
    constructor(faceViewer) {
        this.faceViewer = faceViewer;
        this.container = this.createUI();
    }
    
    createUI() {
        const container = document.createElement('div');
        container.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            padding: 10px;
            color: white;
            font-family: monospace;
        `;
        
        // Hardcoded 8 morphs for MVP
        const morphNames = [
            'Chin Size', 'Nose Length', 'Cheek Width', 'Eye Size',
            'Forehead Height', 'Jaw Width', 'Mouth Width', 'Brow Height'
        ];
        
        morphNames.forEach((name, index) => {
            const label = document.createElement('div');
            label.textContent = name;
            
            const slider = document.createElement('input');
            slider.type = 'range';
            slider.min = 0;
            slider.max = 7;  // M&B uses 0-7 range
            slider.value = 0;
            slider.style.width = '200px';
            
            slider.addEventListener('input', (e) => {
                const value = e.target.value / 7; // Normalize to 0-1
                this.updateMorph(index, value);
            });
            
            container.appendChild(label);
            container.appendChild(slider);
        });
        
        document.body.appendChild(container);
        return container;
    }
    
    updateMorph(index, value) {
        if (this.faceViewer.headMesh?.morphTargetInfluences) {
            this.faceViewer.headMesh.morphTargetInfluences[index] = value;
        }
    }
}
```

**Success Criteria**: Sliders that visibly deform the head mesh

### Phase 4: Face Code Integration (Day 3)

**Goal**: Test face code parsing and morph application

#### Task 4.1: Add Face Code Parser
Create `src/FaceCodeParser.js`:
```javascript
export class FaceCodeParser {
    // Simplified face code parsing for MVP
    static parse(faceCode) {
        // Remove 0x prefix
        if (faceCode.startsWith('0x')) {
            faceCode = faceCode.slice(2);
        }
        
        // For MVP, just extract first 8 morphs from block 1
        // Real implementation would parse all 43 morphs
        const morphs = [];
        
        // Simple extraction - each morph is 3 bits
        const block1 = faceCode.slice(16, 32); // Second 16 chars
        const block1Int = parseInt(block1, 16);
        
        for (let i = 0; i < 8; i++) {
            const shift = i * 3;
            const value = (block1Int >> shift) & 0x7; // Extract 3 bits
            morphs.push(value);
        }
        
        return { morphs };
    }
    
    static generate(morphValues) {
        // Simplified generation for MVP
        let block1 = 0;
        morphValues.forEach((value, i) => {
            if (i < 8) {
                block1 |= (value & 0x7) << (i * 3);
            }
        });
        
        // Create minimal valid face code
        const block0 = "0000000000000000";
        const block1Hex = block1.toString(16).padStart(16, '0');
        const block2 = "0000000000000000";
        const block3 = "0000000000000000";
        
        return `0x${block0}${block1Hex}${block2}${block3}`;
    }
}
```

#### Task 4.2: Add Face Code Input
Update UI to include face code input:
```javascript
// In MorphControls.js
addFaceCodeInput() {
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Paste face code...';
    input.style.cssText = 'width: 100%; margin: 10px 0;';
    
    const button = document.createElement('button');
    button.textContent = 'Apply Face Code';
    button.onclick = () => {
        const parsed = FaceCodeParser.parse(input.value);
        this.applyMorphs(parsed.morphs);
    };
    
    this.container.appendChild(input);
    this.container.appendChild(button);
}
```

**Success Criteria**: Can paste a face code and see morphs update

### Phase 5: Texture Switching (Day 4)

**Goal**: Test skin tone changes

#### Task 5.1: Add Texture Switcher
```javascript
// In FaceViewer.js
async loadTextures() {
    this.textures = {
        white: await new THREE.TextureLoader().loadAsync('/src/assets/textures/face_white.png'),
        tan: await new THREE.TextureLoader().loadAsync('/src/assets/textures/face_tan.png'),
        dark: await new THREE.TextureLoader().loadAsync('/src/assets/textures/face_dark.png')
    };
}

setSkinTone(tone) {
    if (this.headMesh && this.textures[tone]) {
        this.headMesh.material.map = this.textures[tone];
        this.headMesh.material.needsUpdate = true;
    }
}
```

**Success Criteria**: Can switch between skin tones smoothly

## Testing Strategy

### Manual Testing Checklist
1. [ ] Page loads without errors
2. [ ] 3D head model displays (or fallback sphere)
3. [ ] Camera controls work (orbit, zoom)
4. [ ] At least one morph slider visibly changes the face
5. [ ] Face code input accepts valid codes
6. [ ] Skin tone switcher changes texture
7. [ ] Performance is smooth (30+ FPS)

### Test Face Codes
```javascript
// Minimal test codes with different morph values
const TEST_CODES = [
    "0x00000000000000000000000000000000000000000000000000000000000000000", // All zeros
    "0x00000000000000001b6db6db6db6db6d000000000000000000000000000000000", // Some morphs
    "0x0000000000000000ffffffffffffffff000000000000000000000000000000000"  // Max morphs
];
```

## Success Metrics

1. **Rendering Works**: Can display a 3D head in browser
2. **Morphs Function**: At least 4 morphs visibly change face shape
3. **Performance OK**: Maintains 30+ FPS on average laptop
4. **Code Integration**: Can apply face codes to update morphs

## Next Steps After MVP

Once MVP proves the concept:
1. Build proper asset pipeline for all morphs
2. Integrate with backend API
3. Add WebSocket for real-time updates
4. Implement full 43-morph system
5. Add hair/beard mesh switching
6. Polish UI/UX

## Common Issues & Solutions

### Issue: Model won't load
```javascript
// Fallback to procedural geometry
if (!model) {
    console.warn('Using fallback geometry');
    return createProceduralHead();
}
```

### Issue: Morphs don't work
```javascript
// Use simple vertex displacement as fallback
if (!mesh.morphTargetInfluences) {
    console.warn('Using manual vertex morphing');
    return applyManualMorphing(mesh, morphValues);
}
```

### Issue: Textures appear black
```javascript
// Ensure proper material setup
material.map = texture;
material.needsUpdate = true;
renderer.outputEncoding = THREE.sRGBEncoding;
texture.encoding = THREE.sRGBEncoding;
```

## Implementation Timeline

- **Day 1**: Basic Three.js setup + Manual asset extraction
- **Day 2**: Display static head with texture
- **Day 3**: Add morph targets (real or synthetic)
- **Day 4**: Face code integration + UI controls
- **Day 5**: Polish and testing

Total: ~1 week for working MVP

## Key Decisions

1. **Start with manual assets** - Don't build pipeline yet
2. **Use fallbacks everywhere** - Ensure something always displays
3. **Limit to 8 morphs** - Sufficient to prove concept
4. **Skip backend initially** - Use hardcoded data
5. **Focus on visual proof** - Performance optimization comes later

---

Remember: This is an MVP to validate that we CAN render M&B faces in a browser. Once proven, we can build the full system with confidence.