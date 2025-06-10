import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { DDSLoader } from 'three/addons/loaders/DDSLoader.js';
import { MD3Loader } from './MD3Loader.js';
import { FaceCodeParser } from './FaceCodeParser.js';

export class FaceViewer {
    constructor(scene) {
        this.scene = scene;
        this.headMesh = null;
        this.objLoader = new OBJLoader();
        this.md3Loader = new MD3Loader();
        this.textures = {};
        this.currentGender = 'male'; // default to male
        this.currentSkinTone = 'white'; // default skin tone
        this.maleHead = null;
        this.femaleHead = null;
        this.useMD3 = true; // Flag to use MD3 with real morphs
    }

    async loadHead(gender = 'male') {
        this.currentGender = gender;
        
        try {
            // Clear existing head mesh
            if (this.headMesh) {
                this.scene.remove(this.headMesh);
                this.headMesh = null;
            }
            
            if (this.useMD3) {
                // Load MD3 model with vertex animation
                const modelPath = gender === 'female' 
                    ? '/female_head.MD3'
                    : '/male_head.MD3';
                    
                console.log(`Loading ${gender} MD3 model with real morphs:`, modelPath);
                
                const md3Data = await new Promise((resolve, reject) => {
                    this.md3Loader.load(
                        modelPath,
                        resolve,
                        (progress) => console.log('Loading progress:', progress),
                        reject
                    );
                });
                
                console.log('MD3 data loaded:', md3Data);
                console.log(`Number of frames: ${md3Data.header.numFrames}`);
                console.log(`Number of surfaces: ${md3Data.header.numSurfaces}`);
                
                // Debug frame names if available
                if (md3Data.frames) {
                    console.log('Frame list:');
                    md3Data.frames.forEach((frame, idx) => {
                        console.log(`  Frame ${idx}: ${frame.name}`);
                    });
                }
                
                // Create geometry with morph targets from MD3 vertex animation
                const geometry = this.createGeometryFromMD3(md3Data);
                
                // Create material with morph support
                const material = new THREE.MeshPhongMaterial({
                    color: 0xffdbac,
                    specular: 0x111111,
                    shininess: 10,
                    side: THREE.DoubleSide
                });
                
                // Enable morphing on the material (newer Three.js approach)
                material.defines = material.defines || {};
                material.defines.USE_MORPHTARGETS = '';
                material.defines.USE_MORPHNORMALS = '';
                
                // Create mesh
                this.headMesh = new THREE.Mesh(geometry, material);
                this.headMesh.name = `${gender}Head`;
                
                // CRITICAL: Set morphTargetInfluences to correct size based on actual morph targets created
                if (this.morphTargetCount > 0) {
                    this.headMesh.morphTargetInfluences = new Array(this.morphTargetCount).fill(0);
                    console.log(`Set morphTargetInfluences size to ${this.morphTargetCount}`, this.headMesh.morphTargetInfluences);
                } else {
                    console.warn('No morph targets were created!');
                }
                
                // Debug morph setup
                console.log('Mesh morph setup:', {
                    morphTargetInfluences: this.headMesh.morphTargetInfluences,
                    morphAttributes: geometry.morphAttributes,
                    morphTargetsRelative: geometry.morphTargetsRelative,
                    material: material
                });
                
                // Store morph mapping for reference
                this.realMorphMapping = this.createRealMorphMapping();
                
                // Morph targets are ready for use
                
            } else {
                // Fallback to OBJ loading
                const modelPath = gender === 'female' 
                    ? '/obj_files/female_head.obj'
                    : '/obj_files/male_head.obj';
                    
                console.log(`Loading ${gender} OBJ model:`, modelPath);
                const object = await this.objLoader.loadAsync(modelPath);
                
                this.headMesh = object;
                this.mirrorHeadGeometry();
                this.setupMorphTargets();
            }
            
            // Common setup for both MD3 and OBJ
            this.headMesh.scale.setScalar(1);
            this.headMesh.position.set(0, 0, 0);
            
            // MD3 models have different orientation than OBJ
            if (this.useMD3) {
                // MD3 models appear to be correctly oriented (0,0,0)
                this.headMesh.rotation.set(0, 0, 0);
            } else {
                // OBJ rotation that was working
                this.headMesh.rotation.set(Math.PI / 2, Math.PI, 0);
            }
            
            this.headMesh.castShadow = true;
            this.headMesh.receiveShadow = true;
            
            this.scene.add(this.headMesh);
            console.log(`Successfully added ${gender} head model to scene`);
            
            // Apply default skin tone
            this.setSkinTone(this.currentSkinTone);
            
            // Debug what's in the scene
            this.debugScene();
            
            return true;
            
        } catch (error) {
            console.error('Failed to load head model:', error);
            console.log('Creating fallback procedural head');
            
            // FALLBACK: Create a procedural head
            this.createProceduralHead();
            return false;
        }
    }

    createProceduralHead() {
        // Create a more head-like shape using multiple geometries
        const headGroup = new THREE.Group();
        
        // Main head (ellipsoid)
        const headGeometry = new THREE.SphereGeometry(0.5, 32, 32);
        // Stretch vertically to be more head-shaped
        headGeometry.scale(0.9, 1.1, 0.95);
        
        const skinMaterial = new THREE.MeshPhongMaterial({ 
            color: 0xffdbac,
            specular: 0x111111,
            shininess: 10
        });
        
        const headMesh = new THREE.Mesh(headGeometry, skinMaterial);
        headGroup.add(headMesh);
        
        // Add simple eyes
        const eyeGeometry = new THREE.SphereGeometry(0.05, 16, 16);
        const eyeMaterial = new THREE.MeshPhongMaterial({ color: 0x333333 });
        
        const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        leftEye.position.set(-0.15, 0.1, 0.4);
        headGroup.add(leftEye);
        
        const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        rightEye.position.set(0.15, 0.1, 0.4);
        headGroup.add(rightEye);
        
        // Add nose
        const noseGeometry = new THREE.ConeGeometry(0.05, 0.15, 8);
        const noseMesh = new THREE.Mesh(noseGeometry, skinMaterial);
        noseMesh.position.set(0, 0, 0.45);
        noseMesh.rotation.x = Math.PI / 2;
        headGroup.add(noseMesh);
        
        this.headMesh = headGroup;
        this.scene.add(this.headMesh);
        
        // Create synthetic morph system for the procedural head
        this.createProceduralMorphs(headMesh);
    }

    mirrorHeadGeometry() {
        // Find the main mesh in the loaded object
        let mainMesh = null;
        this.headMesh.traverse((child) => {
            if (child.isMesh && !mainMesh) {
                mainMesh = child;
            }
        });
        
        if (!mainMesh) return;
        
        // Clone the geometry to create a full head
        const geometry = mainMesh.geometry.clone();
        const positions = geometry.attributes.position.array;
        const normals = geometry.attributes.normal ? geometry.attributes.normal.array : null;
        const uvs = geometry.attributes.uv ? geometry.attributes.uv.array : null;
        
        // Create arrays for the full head (double the size)
        const fullPositions = new Float32Array(positions.length * 2);
        const fullNormals = normals ? new Float32Array(normals.length * 2) : null;
        const fullUvs = uvs ? new Float32Array(uvs.length * 2) : null;
        
        // Copy original half
        fullPositions.set(positions, 0);
        if (fullNormals) fullNormals.set(normals, 0);
        if (fullUvs) fullUvs.set(uvs, 0);
        
        // Create mirrored half
        const vertexCount = positions.length / 3;
        for (let i = 0; i < vertexCount; i++) {
            const idx = i * 3;
            const mirrorIdx = (vertexCount + i) * 3;
            
            // Mirror X position
            fullPositions[mirrorIdx] = -positions[idx];
            fullPositions[mirrorIdx + 1] = positions[idx + 1];
            fullPositions[mirrorIdx + 2] = positions[idx + 2];
            
            // Mirror normals
            if (fullNormals) {
                fullNormals[mirrorIdx] = -normals[idx];
                fullNormals[mirrorIdx + 1] = normals[idx + 1];
                fullNormals[mirrorIdx + 2] = normals[idx + 2];
            }
        }
        
        // Fix UV coordinates - flip V for both halves
        if (fullUvs) {
            // First, flip V coordinates for the original half
            for (let i = 0; i < uvs.length / 2; i++) {
                const idx = i * 2;
                fullUvs[idx + 1] = 1 - uvs[idx + 1]; // Flip V coordinate
            }
            
            // Then copy UVs for mirrored half
            const uvCount = uvs.length / 2;
            for (let i = 0; i < uvCount; i++) {
                const idx = i * 2;
                const mirrorIdx = (uvCount + i) * 2;
                fullUvs[mirrorIdx] = 1 - uvs[idx]; // Mirror U coordinate
                fullUvs[mirrorIdx + 1] = 1 - uvs[idx + 1]; // Copy flipped V
            }
        }
        
        // Create new geometry with full head
        const fullGeometry = new THREE.BufferGeometry();
        fullGeometry.setAttribute('position', new THREE.BufferAttribute(fullPositions, 3));
        if (fullNormals) {
            fullGeometry.setAttribute('normal', new THREE.BufferAttribute(fullNormals, 3));
        }
        if (fullUvs) {
            fullGeometry.setAttribute('uv', new THREE.BufferAttribute(fullUvs, 2));
        }
        
        // Handle indices if they exist
        if (geometry.index) {
            const indices = geometry.index.array;
            const fullIndices = new Uint16Array(indices.length * 2);
            
            // Copy original indices
            fullIndices.set(indices, 0);
            
            // Create mirrored indices (reversed winding order)
            for (let i = 0; i < indices.length; i += 3) {
                const mirrorIdx = indices.length + i;
                fullIndices[mirrorIdx] = indices[i] + vertexCount;
                fullIndices[mirrorIdx + 1] = indices[i + 2] + vertexCount; // Reversed
                fullIndices[mirrorIdx + 2] = indices[i + 1] + vertexCount; // Reversed
            }
            
            fullGeometry.setIndex(new THREE.BufferAttribute(fullIndices, 1));
        }
        
        // Create new mesh with the full geometry
        const material = new THREE.MeshPhongMaterial({
            color: 0xffdbac,
            specular: 0x111111,
            shininess: 10,
            side: THREE.DoubleSide,
            transparent: false,
            opacity: 1.0
        });
        
        // Enable morphing (newer Three.js approach)
        material.defines = material.defines || {};
        material.defines.USE_MORPHTARGETS = '';
        material.defines.USE_MORPHNORMALS = '';
        
        const fullHeadMesh = new THREE.Mesh(fullGeometry, material);
        fullHeadMesh.name = 'FullHead';
        
        // Compute vertex normals to ensure proper lighting
        fullGeometry.computeVertexNormals();
        
        // Clear the current head mesh
        if (this.headMesh) {
            this.scene.remove(this.headMesh);
        }
        
        // Set the new full head mesh
        this.headMesh = fullHeadMesh;
    }

    createSyntheticMorphs() {
        const mainMesh = this.headMesh;
        if (!mainMesh || !mainMesh.geometry) return;
        
        const geometry = mainMesh.geometry;
        const position = geometry.attributes.position;
        
        // Store original positions
        this.originalPositions = new Float32Array(position.array);
        
        // Create morph targets - each stores DELTAS from original position
        const morphTargets = [];
        
        // Morph 0: Chin Size (affects chin height and projection)
        const chinMorph = new Float32Array(position.array); // Start with original positions
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            // Target lower face area
            if (y < -0.2) { 
                const influence = Math.abs(y + 0.2) / 0.3; // Smooth falloff
                chinMorph[i * 3] = x; // Keep X same
                chinMorph[i * 3 + 1] = y - (0.15 * influence); // Move down
                chinMorph[i * 3 + 2] = z + (0.05 * influence); // Slightly forward
            } else {
                // Keep original position for unaffected vertices
                chinMorph[i * 3] = x;
                chinMorph[i * 3 + 1] = y;
                chinMorph[i * 3 + 2] = z;
            }
        }
        
        // Morph 1: Nose Length (nose projection)
        const noseMorph = new Float32Array(position.array);
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            // Target nose area (front-center of face)
            if (z > 0.2 && Math.abs(y) < 0.15 && Math.abs(x) < 0.1) {
                const influence = (z - 0.2) / 0.2;
                noseMorph[i * 3] = x;
                noseMorph[i * 3 + 1] = y;
                noseMorph[i * 3 + 2] = z + (0.12 * influence); // Project forward
            } else {
                noseMorph[i * 3] = x;
                noseMorph[i * 3 + 1] = y;
                noseMorph[i * 3 + 2] = z;
            }
        }
        
        // Morph 2: Cheek Width (face width at cheekbone level)
        const cheekMorph = new Float32Array(position.array);
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            // Target cheek area (sides of face at eye level)
            if (Math.abs(x) > 0.15 && Math.abs(y) < 0.2 && Math.abs(y) > 0.05) {
                const influence = (Math.abs(x) - 0.15) / 0.2;
                const direction = x > 0 ? 1 : -1;
                cheekMorph[i * 3] = x + (direction * 0.1 * influence); // Widen
                cheekMorph[i * 3 + 1] = y;
                cheekMorph[i * 3 + 2] = z;
            } else {
                cheekMorph[i * 3] = x;
                cheekMorph[i * 3 + 1] = y;
                cheekMorph[i * 3 + 2] = z;
            }
        }
        
        // Morph 3: Eye Size (eye area scale)
        const eyeMorph = new Float32Array(position.array);
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            // Target eye socket area
            if (Math.abs(x) > 0.05 && Math.abs(x) < 0.25 && 
                y > 0.05 && y < 0.2 && z > 0.1) {
                const eyeCenterX = x > 0 ? 0.15 : -0.15;
                const eyeCenterY = 0.12;
                const distFromCenter = Math.sqrt(
                    Math.pow(x - eyeCenterX, 2) + 
                    Math.pow(y - eyeCenterY, 2)
                );
                if (distFromCenter < 0.1) {
                    const influence = 1 - (distFromCenter / 0.1);
                    // Scale away from eye center
                    eyeMorph[i * 3] = x + ((x - eyeCenterX) * 0.3 * influence);
                    eyeMorph[i * 3 + 1] = y + ((y - eyeCenterY) * 0.3 * influence);
                    eyeMorph[i * 3 + 2] = z;
                } else {
                    eyeMorph[i * 3] = x;
                    eyeMorph[i * 3 + 1] = y;
                    eyeMorph[i * 3 + 2] = z;
                }
            } else {
                eyeMorph[i * 3] = x;
                eyeMorph[i * 3 + 1] = y;
                eyeMorph[i * 3 + 2] = z;
            }
        }
        
        // Morph 4: Forehead Height 
        const foreheadMorph = new Float32Array(position.array);
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            // Target forehead area
            if (y > 0.2) {
                const influence = (y - 0.2) / 0.3;
                foreheadMorph[i * 3] = x;
                foreheadMorph[i * 3 + 1] = y + (0.1 * influence); // Move up
                foreheadMorph[i * 3 + 2] = z - (0.03 * influence); // Slightly back
            } else {
                foreheadMorph[i * 3] = x;
                foreheadMorph[i * 3 + 1] = y;
                foreheadMorph[i * 3 + 2] = z;
            }
        }
        
        // Morph 5: Jaw Width (lower face width)
        const jawMorph = new Float32Array(position.array);
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            // Target jaw area
            if (Math.abs(x) > 0.1 && y < -0.1 && y > -0.35) {
                const influence = Math.abs(y + 0.1) / 0.25;
                const direction = x > 0 ? 1 : -1;
                jawMorph[i * 3] = x + (direction * 0.12 * influence);
                jawMorph[i * 3 + 1] = y;
                jawMorph[i * 3 + 2] = z;
            } else {
                jawMorph[i * 3] = x;
                jawMorph[i * 3 + 1] = y;
                jawMorph[i * 3 + 2] = z;
            }
        }
        
        // Morph 6: Mouth Width
        const mouthMorph = new Float32Array(position.array);
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            // Target mouth area
            if (Math.abs(x) < 0.15 && y > -0.2 && y < -0.05 && z > 0.25) {
                const influence = 1 - (Math.abs(x) / 0.15);
                const direction = x > 0 ? 1 : -1;
                mouthMorph[i * 3] = x + (direction * 0.08 * influence);
                mouthMorph[i * 3 + 1] = y;
                mouthMorph[i * 3 + 2] = z;
            } else {
                mouthMorph[i * 3] = x;
                mouthMorph[i * 3 + 1] = y;
                mouthMorph[i * 3 + 2] = z;
            }
        }
        
        // Morph 7: Brow Height
        const browMorph = new Float32Array(position.array);
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            const z = position.getZ(i);
            
            // Target brow area
            if (Math.abs(x) < 0.25 && y > 0.15 && y < 0.25 && z > 0.15) {
                const influence = 1 - Math.abs(y - 0.2) / 0.05;
                browMorph[i * 3] = x;
                browMorph[i * 3 + 1] = y + (0.05 * influence); // Raise brow
                browMorph[i * 3 + 2] = z + (0.03 * influence); // Project forward
            } else {
                browMorph[i * 3] = x;
                browMorph[i * 3 + 1] = y;
                browMorph[i * 3 + 2] = z;
            }
        }
        
        // Set up morph attributes
        const morphAttributes = [
            chinMorph, noseMorph, cheekMorph, eyeMorph,
            foreheadMorph, jawMorph, mouthMorph, browMorph
        ];
        
        geometry.morphAttributes.position = [];
        morphAttributes.forEach((morphData, index) => {
            const attribute = new THREE.BufferAttribute(morphData, 3);
            attribute.name = `morph${index}`;
            geometry.morphAttributes.position.push(attribute);
        });
        
        // Initialize morph target influences for all 27 morphs
        // We only have 8 actual morph targets, but we'll map the 27 sliders to them
        mainMesh.morphTargetInfluences = new Array(8).fill(0);
        
        // Store all 27 morph values separately
        this.allMorphValues = new Array(27).fill(0);
        
        // Map which morphs affect which morph targets
        this.morphMapping = {
            0: [2],      // Face Width -> cheek morph
            1: [0, 4],   // Face Ratio -> chin + forehead
            2: [2, 5],   // Face Depth -> cheek + jaw
            3: [4],      // Temple Width -> forehead
            4: [7],      // Eyebrow Shape -> brow
            5: [7],      // Eyebrow Depth -> brow
            6: [7],      // Eyebrow Height -> brow
            7: [7],      // Eyebrow Position -> brow
            8: [3],      // Eyelids -> eye
            9: [3],      // Eye Depth -> eye
            10: [3],     // Eye Shape -> eye
            11: [3],     // Eye to Eye Dist -> eye
            12: [3],     // Eye Width -> eye
            13: [2],     // Cheek Bones -> cheek
            14: [1],     // Nose Bridge -> nose
            15: [1],     // Nose Shape -> nose
            16: [1],     // Nose Size -> nose
            17: [1],     // Nose Width -> nose
            18: [1],     // Nose Height -> nose
            19: [2],     // Cheeks -> cheek
            20: [6],     // Mouth Width -> mouth
            21: [6],     // Mouth-Nose Distance -> mouth
            22: [5],     // Jaw Position -> jaw
            23: [5],     // Jaw Width -> jaw
            24: [0],     // Chin Forward -> chin
            25: [0],     // Chin Shape -> chin
            26: [0]      // Chin Size -> chin
        };
        
        // Update the material to support morphing (newer Three.js approach)
        if (mainMesh.material) {
            mainMesh.material.defines = mainMesh.material.defines || {};
            mainMesh.material.defines.USE_MORPHTARGETS = '';
            mainMesh.material.defines.USE_MORPHNORMALS = '';
            mainMesh.material.needsUpdate = true;
        }
        
        console.log('Created 8 synthetic morph targets with proper deltas');
    }

    applyMaterials(object) {
        // Apply materials to the head mesh and all its children
        if (object.isMesh) {
            // Apply default material immediately
            const defaultMaterial = new THREE.MeshPhongMaterial({ 
                color: 0xffdbac,
                specular: 0x111111,
                shininess: 10
            });
            object.material = defaultMaterial;
            console.log('Applied default material to mesh:', object.name);
            
            // Try to load texture asynchronously
            this.loadBasicTexture().then(texture => {
                if (texture) {
                    object.material = new THREE.MeshPhongMaterial({ 
                        map: texture,
                        specular: 0x111111,
                        shininess: 10
                    });
                    console.log('Applied texture material to mesh:', object.name);
                }
            }).catch(error => {
                console.log('Texture loading failed, keeping default material');
            });
        }
        
        // Recursively apply to children
        if (object.children) {
            object.children.forEach(child => this.applyMaterials(child));
        }
    }

    async loadBasicTexture() {
        try {
            const texture = await new THREE.TextureLoader().loadAsync('/src/assets/textures/face_white.png');
            texture.colorSpace = THREE.SRGBColorSpace;
            return texture;
        } catch (error) {
            console.warn('Texture not found, using default material');
            return null;
        }
    }

    setupMorphTargets() {
        // Skip if using MD3 - morphs are already set up
        if (this.useMD3) {
            console.log('Using MD3 with real morph targets, skipping synthetic morph creation');
            return;
        }
        
        // Since headMesh is now a single mesh after mirroring, we can work with it directly
        const headMesh = this.headMesh;
        console.log('setupMorphTargets - head mesh:', headMesh);
        
        if (headMesh && headMesh.isMesh && headMesh.geometry) {
            if (!headMesh.morphTargetInfluences || headMesh.morphTargetInfluences.length === 0) {
                console.log('No morph targets found, creating synthetic ones');
                this.createSyntheticMorphs();
            } else {
                console.log(`Found ${headMesh.morphTargetInfluences.length} existing morph targets`);
            }
        } else {
            console.log('No suitable mesh found for morphing - OBJ model may not have geometry');
            // DON'T create procedural head if we already have an OBJ loaded
            console.log('Skipping procedural head creation since OBJ is loaded');
        }
    }

    findMainHeadMesh(object) {
        // Find the main mesh with geometry
        if (object.isMesh && object.geometry && object.geometry.attributes.position) {
            return object;
        }
        
        // Search children
        if (object.children) {
            for (const child of object.children) {
                const found = this.findMainHeadMesh(child);
                if (found) return found;
            }
        }
        
        return null;
    }

    debugScene() {
        console.log('=== SCENE DEBUG ===');
        console.log('Total scene children:', this.scene.children.length);
        this.scene.children.forEach((child, index) => {
            console.log(`Scene child ${index}:`, child.type, child.name || 'unnamed');
            if (child.isGroup || child.isObject3D) {
                child.traverse((subchild) => {
                    if (subchild.isMesh) {
                        console.log(`  - Mesh: ${subchild.name || 'unnamed'}, visible: ${subchild.visible}, geometry vertices: ${subchild.geometry?.attributes?.position?.count || 0}`);
                    }
                });
            }
        });
        console.log('=== END SCENE DEBUG ===');
    }

    async switchGender(gender) {
        if (gender !== this.currentGender) {
            const success = await this.loadHead(gender);
            if (success) {
                // Reapply the current skin tone to use gender-specific texture
                this.setSkinTone(this.currentSkinTone);
            }
            return success;
        }
        return true;
    }

    createProceduralMorphs(headMesh) {
        // Simple morph system for procedural head
        this.proceduralMorphs = {
            chinSize: 0,
            noseLength: 0,
            cheekWidth: 0,
            foreheadHeight: 0,
            jawWidth: 0,
            mouthWidth: 0,
            eyeSize: 0,
            browHeight: 0
        };
        
        // Store original scales and positions
        this.originalScale = headMesh.scale.clone();
        
        // Simulate morph influences array
        this.headMesh.morphTargetInfluences = new Array(8).fill(0);
        
        // Override the setter to apply procedural morphs
        const morphInfluences = this.headMesh.morphTargetInfluences;
        Object.defineProperty(this.headMesh, 'morphTargetInfluences', {
            get: () => morphInfluences,
            set: (values) => {
                values.forEach((value, index) => {
                    morphInfluences[index] = value;
                });
                this.applyProceduralMorphs();
            }
        });
    }

    applyProceduralMorphs() {
        if (!this.headMesh || !this.headMesh.morphTargetInfluences) return;
        
        const influences = this.headMesh.morphTargetInfluences;
        const head = this.headMesh.children[0]; // Main head mesh
        
        if (head) {
            // Apply simple transformations based on morph values
            // Chin size - scale Y bottom
            head.scale.y = this.originalScale.y + (influences[0] * 0.2);
            
            // Cheek width - scale X
            head.scale.x = this.originalScale.x + (influences[2] * 0.15);
            
            // Forehead height - move head up slightly
            head.position.y = influences[3] * 0.1;
        }
    }

    async loadTextures() {
        const ddsLoader = new DDSLoader();
        
        // Initialize texture storage for both genders
        this.textures = {
            male: {},
            female: {}
        };
        
        // Define gender-specific texture paths with more variety
        const genderTextures = {
            male: {
                young: '/dds_textures/manface_young.dds',
                young2: '/dds_textures/manface_young_2.dds',
                young3: '/dds_textures/manface_young_3.dds',
                warrior: '/dds_textures/manface_7.dds',
                midage: '/dds_textures/manface_midage.dds',
                midage2: '/dds_textures/manface_midage_2.dds',
                rugged: '/dds_textures/manface_rugged.dds',
                african: '/dds_textures/manface_african.dds'
            },
            female: {
                young: '/dds_textures/womanface_young.dds',
                pretty: '/dds_textures/womanface_a.dds',
                mature: '/dds_textures/womanface_b.dds',
                brown: '/dds_textures/womanface_brown.dds',
                african: '/dds_textures/womanface_african.dds'
            }
        };
        
        // Additional texture variations for future use
        this.textureVariations = {
            male: {
                young: [
                    '/dds_textures/manface_young.dds',
                    '/dds_textures/manface_young_2.dds',
                    '/dds_textures/manface_young_3.dds'
                ],
                aged: [
                    '/dds_textures/manface_1_aged.dds',
                    '/dds_textures/manface_2_aged.dds',
                    '/dds_textures/manface_african_old.dds'
                ]
            },
            female: {
                young: [
                    '/dds_textures/womanface_young.dds',
                    '/dds_textures/womanface_a.dds',
                    '/dds_textures/womanface_b.dds'
                ],
                aged: [
                    '/dds_textures/womanface_1_aged.dds',
                    '/dds_textures/womanface_2_aged.dds',
                    '/dds_textures/womanface_african_aged.dds'
                ]
            }
        };
        
        // Load textures for both genders
        let totalLoaded = 0;
        for (const [gender, textures] of Object.entries(genderTextures)) {
            for (const [tone, path] of Object.entries(textures)) {
                try {
                    const texture = await new Promise((resolve, reject) => {
                        ddsLoader.load(
                            path,
                            (texture) => resolve(texture),
                            undefined,
                            (error) => reject(error)
                        );
                    });
                    
                    texture.colorSpace = THREE.SRGBColorSpace;
                    texture.flipY = false; // Don't flip texture since we're flipping UVs
                    texture.wrapS = THREE.RepeatWrapping;
                    texture.wrapT = THREE.RepeatWrapping;
                    this.textures[gender][tone] = texture;
                    console.log(`Loaded ${gender} ${tone} skin DDS texture from ${path}`);
                    totalLoaded++;
                } catch (e) {
                    console.warn(`Could not load ${gender} ${tone} skin texture from ${path}:`, e);
                }
            }
        }
        
        // Report loading status
        if (totalLoaded === 0) {
            console.log('No DDS textures found, using color-based materials');
        } else {
            console.log(`Successfully loaded ${totalLoaded} DDS textures`);
        }
    }

    setSkinTone(tone) {
        if (!this.headMesh || !this.headMesh.material) return;
        
        // Track current skin tone
        this.currentSkinTone = tone;
        
        // Get gender-specific texture
        const genderTextures = this.textures[this.currentGender] || {};
        const texture = genderTextures[tone];
        
        if (texture) {
            // Apply texture if available
            this.headMesh.material.map = texture;
            this.headMesh.material.color.setHex(0xffffff); // Reset color to white when using texture
            this.headMesh.material.needsUpdate = true;
            console.log(`Applied ${this.currentGender} ${tone} skin texture`);
        } else {
            // Fallback to a neutral skin color
            this.headMesh.material.map = null;
            this.headMesh.material.color.setHex(0xffdbac);
            this.headMesh.material.specular.setHex(0x222222);
            this.headMesh.material.needsUpdate = true;
            console.log(`Applied default skin color (no texture available for ${this.currentGender} ${tone})`);
        }
        
        // Ensure morph targets stay enabled (newer Three.js approach)
        this.headMesh.material.defines = this.headMesh.material.defines || {};
        this.headMesh.material.defines.USE_MORPHTARGETS = '';
        this.headMesh.material.defines.USE_MORPHNORMALS = '';
        this.headMesh.material.needsUpdate = true;
    }
    
    // Apply morph value from the 27 sliders to the actual morph targets
    applyMorphValue(sliderIndex, value) {
        if (!this.headMesh || !this.headMesh.morphTargetInfluences) return;
        
        console.log(`applyMorphValue called: slider ${sliderIndex} (${this.getSliderName(sliderIndex)}) value ${value}`);
        
        if (this.useMD3) {
            // Use the pre-computed mapping from createGeometryFromMD3
            const morphTargetIndex = this.sliderToMorphTargetIndex?.[sliderIndex];
            console.log(`Mapping slider ${sliderIndex} to morph target ${morphTargetIndex}`);
            
            if (morphTargetIndex !== undefined && morphTargetIndex < this.headMesh.morphTargetInfluences.length) {
                const oldValue = this.headMesh.morphTargetInfluences[morphTargetIndex];
                this.headMesh.morphTargetInfluences[morphTargetIndex] = value;
                console.log(`✓ Slider ${sliderIndex} (${this.getSliderName(sliderIndex)}) -> Morph Target ${morphTargetIndex}: ${oldValue} -> ${value}`);
                console.log('Current morph influences:', [...this.headMesh.morphTargetInfluences]);
            } else {
                console.warn(`✗ Slider ${sliderIndex} (${this.getSliderName(sliderIndex)}) has no corresponding morph target (index: ${morphTargetIndex}, max: ${this.headMesh.morphTargetInfluences.length - 1})`);
            }
        } else {
            // Synthetic morph mapping for OBJ mode
            if (this.allMorphValues) {
                this.allMorphValues[sliderIndex] = value;
            }
            
            if (this.morphMapping && this.morphMapping[sliderIndex]) {
                const targets = this.morphMapping[sliderIndex];
                targets.forEach(targetIndex => {
                    if (targetIndex < this.headMesh.morphTargetInfluences.length) {
                        let sum = 0;
                        let count = 0;
                        for (let i = 0; i < 27; i++) {
                            if (this.morphMapping[i] && this.morphMapping[i].includes(targetIndex)) {
                                sum += (this.allMorphValues[i] || 0);
                                count++;
                            }
                        }
                        this.headMesh.morphTargetInfluences[targetIndex] = count > 0 ? sum / count : 0;
                    }
                });
            }
        }
    }
    
    // Create geometry from MD3 data with morph targets
    createGeometryFromMD3(md3Data) {
        const surface = md3Data.surface;
        const geometry = new THREE.BufferGeometry();
        
        console.log(`Surface has ${surface.numFrames} frames total`);
        
        // Use frame 0 as the base/reference pose
        const baseVertices = new Float32Array(surface.frameVertices[0]);
        const baseNormals = new Float32Array(surface.frameNormals[0]);
        const uvArray = new Float32Array(surface.uvs);
        const indexArray = new Uint16Array(surface.indices);
        
        // Mirror the geometry to create full head
        const mirroredData = this.mirrorMD3Geometry(baseVertices, baseNormals, uvArray, indexArray);
        
        // Set base geometry with mirrored data
        geometry.setAttribute('position', new THREE.BufferAttribute(mirroredData.positions, 3));
        geometry.setAttribute('normal', new THREE.BufferAttribute(mirroredData.normals, 3));
        geometry.setAttribute('uv', new THREE.BufferAttribute(mirroredData.uvs, 2));
        geometry.setIndex(new THREE.BufferAttribute(mirroredData.indices, 1));
        
        // Ensure normals are properly normalized after mirroring
        geometry.normalizeNormals();
        
        // Create morph attributes from vertex animation frames
        const morphPositions = [];
        const morphNormals = [];
        
        // Use direct frame mapping from documentation
        const sliderToFrameMap = FaceCodeParser.sliderToFrameMapping;
        
        console.log('Using correct morph key to frame mapping');
        console.log('Slider to frame mapping:', sliderToFrameMap);
        
        // Create mapping from slider index to morph target index
        // Only create morph targets for sliders that have valid frames
        this.sliderToMorphTargetIndex = {};
        let morphTargetIndex = 0;
        
        // First pass: create morph targets only for valid frames
        for (let sliderIndex = 0; sliderIndex < 27; sliderIndex++) {
            const frameNumber = sliderToFrameMap[sliderIndex];
            
            if (frameNumber && frameNumber < surface.numFrames) {
                // Get frame vertices and mirror them
                const frameVerts = new Float32Array(surface.frameVertices[frameNumber]);
                const frameNorms = new Float32Array(surface.frameNormals[frameNumber]);
                
                // DEBUG: Check if this frame is actually different from base frame
                const baseVerts = new Float32Array(surface.frameVertices[0]);
                let maxDiff = 0;
                for (let i = 0; i < Math.min(frameVerts.length, baseVerts.length); i++) {
                    const diff = Math.abs(frameVerts[i] - baseVerts[i]);
                    if (diff > maxDiff) maxDiff = diff;
                }
                console.log(`Frame ${frameNumber} max difference from base: ${maxDiff}`);
                
                const mirroredFrame = this.mirrorMD3Geometry(frameVerts, frameNorms, uvArray, indexArray);
                
                morphPositions.push(new THREE.BufferAttribute(mirroredFrame.positions, 3));
                morphNormals.push(new THREE.BufferAttribute(mirroredFrame.normals, 3));
                
                // Store the mapping
                this.sliderToMorphTargetIndex[sliderIndex] = morphTargetIndex;
                morphTargetIndex++;
                
                console.log(`Slider ${sliderIndex} (${this.getSliderName(sliderIndex)}) -> Frame ${frameNumber} -> Morph Target ${this.sliderToMorphTargetIndex[sliderIndex]}`);
            } else {
                if (frameNumber) {
                    console.warn(`Frame ${frameNumber} not available for slider ${sliderIndex} (only ${surface.numFrames} frames total)`);
                } else {
                    console.log(`No frame mapping for slider ${sliderIndex} (${this.getSliderName(sliderIndex)})`);
                }
            }
        }
        
        console.log(`Created ${morphPositions.length} morph targets for ${Object.keys(this.sliderToMorphTargetIndex).length} sliders`);
        console.log('Final slider to morph target mapping:', this.sliderToMorphTargetIndex);
        
        // Assign morph attributes
        geometry.morphAttributes.position = morphPositions;
        geometry.morphAttributes.normal = morphNormals;
        
        // Store the morph count for setting morphTargetInfluences later
        this.morphTargetCount = morphPositions.length;
        console.log(`Will set morphTargetInfluences array size to ${this.morphTargetCount}`);
        
        // TRY WITHOUT CONVERTING TO RELATIVE MORPHS FIRST
        // The MD3 data might already be in the right format
        console.log('Using absolute morph targets (not converting to relative)');
        geometry.morphTargetsRelative = false;
        
        // TODO: If absolute doesn't work, try relative conversion:
        /*
        // Convert absolute morphs to relative (deltas from base)
        const basePositions = geometry.attributes.position.array;
        const geometryNormals = geometry.attributes.normal.array;
        
        for (let i = 0; i < morphPositions.length; i++) {
            const morphPosArray = morphPositions[i].array;
            const morphNormArray = morphNormals[i].array;
            
            // Calculate deltas
            for (let j = 0; j < morphPosArray.length; j++) {
                morphPosArray[j] = morphPosArray[j] - basePositions[j];
            }
            for (let j = 0; j < morphNormArray.length; j++) {
                morphNormArray[j] = morphNormArray[j] - geometryNormals[j];
            }
        }
        
        geometry.morphTargetsRelative = true;
        */
        
        console.log(`Created geometry with ${morphPositions.length} morph targets`);
        console.log('Morph mode: absolute (testing without conversion)');
        
        return geometry;
    }
    
    // Mirror MD3 geometry to create full head
    mirrorMD3Geometry(positions, normals, uvs, indices) {
        const vertexCount = positions.length / 3;
        
        // Create arrays for the full head (double the size)
        const fullPositions = new Float32Array(positions.length * 2);
        const fullNormals = new Float32Array(normals.length * 2);
        const fullUvs = new Float32Array(uvs.length * 2);
        
        // Copy original half
        fullPositions.set(positions, 0);
        fullNormals.set(normals, 0);
        
        // Copy and flip UVs for original half
        for (let i = 0; i < uvs.length / 2; i++) {
            const idx = i * 2;
            fullUvs[idx] = uvs[idx];
            fullUvs[idx + 1] = 1 - uvs[idx + 1]; // Flip V
        }
        
        // Create mirrored half
        for (let i = 0; i < vertexCount; i++) {
            const idx = i * 3;
            const mirrorIdx = (vertexCount + i) * 3;
            
            // Mirror X position
            fullPositions[mirrorIdx] = -positions[idx];
            fullPositions[mirrorIdx + 1] = positions[idx + 1];
            fullPositions[mirrorIdx + 2] = positions[idx + 2];
            
            // Mirror normals
            fullNormals[mirrorIdx] = -normals[idx];
            fullNormals[mirrorIdx + 1] = normals[idx + 1];
            fullNormals[mirrorIdx + 2] = normals[idx + 2];
        }
        
        // Mirror UVs
        const uvCount = uvs.length / 2;
        for (let i = 0; i < uvCount; i++) {
            const idx = i * 2;
            const mirrorIdx = (uvCount + i) * 2;
            fullUvs[mirrorIdx] = 1 - uvs[idx]; // Mirror U
            fullUvs[mirrorIdx + 1] = 1 - uvs[idx + 1]; // Copy flipped V
        }
        
        // Create full indices
        const fullIndices = new Uint16Array(indices.length * 2);
        fullIndices.set(indices, 0);
        
        // Create mirrored indices (reversed winding)
        for (let i = 0; i < indices.length; i += 3) {
            const mirrorIdx = indices.length + i;
            fullIndices[mirrorIdx] = indices[i] + vertexCount;
            fullIndices[mirrorIdx + 1] = indices[i + 2] + vertexCount; // Reversed
            fullIndices[mirrorIdx + 2] = indices[i + 1] + vertexCount; // Reversed
        }
        
        return {
            positions: fullPositions,
            normals: fullNormals,
            uvs: fullUvs,
            indices: fullIndices
        };
    }
    
    // Get slider name for debugging
    getSliderName(index) {
        const sliderNames = [
            'Face Width',           // 0
            'Face Ratio',           // 1
            'Face Depth',           // 2
            'Temple Width',         // 3
            'Eyebrow Shape',        // 4
            'Eyebrow Depth',        // 5
            'Eyebrow Height',       // 6
            'Eyebrow Position',     // 7
            'Eyelids',              // 8
            'Eye Depth',            // 9
            'Eye Shape',            // 10
            'Eye to Eye Dist',      // 11
            'Eye Width',            // 12
            'Cheek Bones',          // 13
            'Nose Bridge',          // 14
            'Nose Shape',           // 15
            'Nose Size',            // 16
            'Nose Width',           // 17
            'Nose Height',          // 18
            'Cheeks',               // 19
            'Mouth Width',          // 20
            'Mouth-Nose Distance',  // 21
            'Jaw Position',         // 22
            'Jaw Width',            // 23
            'Chin Forward',         // 24
            'Chin Shape',           // 25
            'Chin Size'             // 26
        ];
        return sliderNames[index] || `Slider ${index}`;
    }

    // Create mapping for real morphs from MD3
    createRealMorphMapping() {
        // Direct mapping - each of the 27 sliders maps to its morph target
        return {
            'Face Width': 0,
            'Face Ratio': 1,
            'Face Depth': 2,
            'Temple Width': 3,
            'Eyebrow Shape': 4,
            'Eyebrow Depth': 5,
            'Eyebrow Height': 6,
            'Eyebrow Position': 7,
            'Eyelids': 8,
            'Eye Depth': 9,
            'Eye Shape': 10,
            'Eye to Eye Dist': 11,
            'Eye Width': 12,
            'Cheek Bones': 13,
            'Nose Bridge': 14,
            'Nose Shape': 15,
            'Nose Size': 16,
            'Nose Width': 17,
            'Nose Height': 18,
            'Cheeks': 19,
            'Mouth Width': 20,
            'Mouth-Nose Distance': 21,
            'Jaw Position': 22,
            'Jaw Width': 23,
            'Chin Forward': 24,
            'Chin Shape': 25,
            'Chin Size': 26
        };
    }
}