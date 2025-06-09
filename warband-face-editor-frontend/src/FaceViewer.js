import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { DDSLoader } from 'three/addons/loaders/DDSLoader.js';

export class FaceViewer {
    constructor(scene) {
        this.scene = scene;
        this.headMesh = null;
        this.loader = new OBJLoader();
        this.textures = {};
        this.currentGender = 'male'; // default to male
        this.maleHead = null;
        this.femaleHead = null;
    }

    async loadHead(gender = 'male') {
        this.currentGender = gender;
        
        try {
            // Clear existing head mesh
            if (this.headMesh) {
                this.scene.remove(this.headMesh);
                this.headMesh = null;
            }
            
            // Load the appropriate OBJ model  
            const modelPath = gender === 'female' 
                ? '/obj_files/female_head.obj'
                : '/obj_files/male_head.obj';
                
            console.log(`Loading ${gender} head model:`, modelPath);
            const object = await this.loader.loadAsync(modelPath);
            
            // Get the head mesh from the OBJ
            this.headMesh = object;
            console.log('Loaded OBJ object:', this.headMesh);
            console.log('OBJ children:', this.headMesh.children);
            console.log('OBJ structure:', JSON.stringify(this.headMesh, null, 2));
            
            // Mirror the half-head to create full head
            this.mirrorHeadGeometry();
            
            // Check if the scene has any visible meshes
            let meshCount = 0;
            this.headMesh.traverse((child) => {
                if (child.isMesh) {
                    meshCount++;
                    console.log('Found mesh:', child.name, 'geometry:', child.geometry, 'material:', child.material);
                    console.log('Mesh visible:', child.visible, 'scale:', child.scale);
                }
            });
            console.log(`Total meshes found: ${meshCount}`);
            
            // Apply material to all meshes in the scene
            // Skip if we already have a properly configured material from mirroring
            if (!this.headMesh.material || !this.headMesh.material.side) {
                this.applyMaterials(this.headMesh);
            }
            
            // Ensure proper scale and position
            this.headMesh.scale.setScalar(1);
            this.headMesh.position.set(0, 0, 0);
            this.headMesh.rotation.set(0, 0, 0);
            
            // Make sure all children are visible
            this.headMesh.traverse((child) => {
                if (child.isMesh) {
                    child.visible = true;
                    child.castShadow = true;
                    child.receiveShadow = true;
                }
            });
            
            this.scene.add(this.headMesh);
            console.log(`Successfully added ${gender} head model to scene`);
            console.log('Head mesh scale:', this.headMesh.scale);
            console.log('Head mesh position:', this.headMesh.position);
            
            // Debug what's in the scene
            this.debugScene();
            
            // Try to create synthetic morphs if the model doesn't have them
            this.setupMorphTargets();
            
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
        
        // Create morph targets
        const morphTargets = [];
        
        // Morph 1: Chin Size (move bottom vertices down/up)
        const chinMorph = new Float32Array(position.count * 3);
        for (let i = 0; i < position.count; i++) {
            const y = position.getY(i);
            if (y < -0.3) { // Bottom part of head
                chinMorph[i * 3] = 0;
                chinMorph[i * 3 + 1] = -0.15; // Move down
                chinMorph[i * 3 + 2] = 0.05; // Slightly forward
            }
        }
        
        // Morph 2: Nose Length (move nose area forward)
        const noseMorph = new Float32Array(position.count * 3);
        for (let i = 0; i < position.count; i++) {
            const z = position.getZ(i);
            const y = position.getY(i);
            if (z > 0.3 && Math.abs(y) < 0.2) { // Nose area
                noseMorph[i * 3] = 0;
                noseMorph[i * 3 + 1] = 0;
                noseMorph[i * 3 + 2] = 0.1; // Move forward
            }
        }
        
        // Morph 3: Cheek Width (widen middle face)
        const cheekMorph = new Float32Array(position.count * 3);
        for (let i = 0; i < position.count; i++) {
            const x = position.getX(i);
            const y = position.getY(i);
            if (Math.abs(x) > 0.2 && Math.abs(y) < 0.2) { // Cheek area
                cheekMorph[i * 3] = x > 0 ? 0.1 : -0.1; // Widen
                cheekMorph[i * 3 + 1] = 0;
                cheekMorph[i * 3 + 2] = 0;
            }
        }
        
        // Morph 4: Forehead Height (move top vertices up)
        const foreheadMorph = new Float32Array(position.count * 3);
        for (let i = 0; i < position.count; i++) {
            const y = position.getY(i);
            if (y > 0.3) { // Top part of head
                foreheadMorph[i * 3] = 0;
                foreheadMorph[i * 3 + 1] = 0.1; // Move up
                foreheadMorph[i * 3 + 2] = 0;
            }
        }
        
        // Add more morphs for the full 8
        const jawMorph = new Float32Array(position.count * 3);
        const mouthMorph = new Float32Array(position.count * 3);
        const eyeMorph = new Float32Array(position.count * 3);
        const browMorph = new Float32Array(position.count * 3);
        
        // Set up morph attributes
        const morphAttributes = [
            chinMorph, noseMorph, cheekMorph, foreheadMorph,
            jawMorph, mouthMorph, eyeMorph, browMorph
        ];
        
        geometry.morphAttributes.position = [];
        morphAttributes.forEach((morphData, index) => {
            const attribute = new THREE.BufferAttribute(morphData, 3);
            attribute.name = `morph${index}`;
            geometry.morphAttributes.position.push(attribute);
        });
        
        // Initialize morph target influences
        mainMesh.morphTargetInfluences = new Array(8).fill(0);
        
        // Update the material to support morphing
        if (mainMesh.material) {
            mainMesh.material.morphTargets = true;
        }
        
        console.log('Created 8 synthetic morph targets');
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
            return await this.loadHead(gender);
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
        
        // Define DDS texture paths based on skin tone
        const texturePaths = {
            white: '/dds_textures/manface_young_2.dds',     // Light skin
            tan: '/dds_textures/manface_midage.dds',        // Tan/medium skin
            dark: '/dds_textures/manface_african.dds'       // Dark skin
        };
        
        // Additional texture variations we can use
        this.textureVariations = {
            young: [
                '/dds_textures/manface_young.dds',
                '/dds_textures/manface_young_2.dds',
                '/dds_textures/manface_young_3.dds'
            ],
            aged: [
                '/dds_textures/manface_1_aged.dds',
                '/dds_textures/manface_2_aged.dds',
                '/dds_textures/manface_african_old.dds'
            ],
            rugged: [
                '/dds_textures/manface_rugged.dds',
                '/dds_textures/manface_midage_2.dds'
            ]
        };
        
        // Try to load each texture
        for (const [tone, path] of Object.entries(texturePaths)) {
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
                this.textures[tone] = texture;
                console.log(`Loaded ${tone} skin DDS texture from ${path}`);
            } catch (e) {
                console.warn(`Could not load ${tone} skin texture from ${path}:`, e);
            }
        }
        
        // If no textures loaded, we'll use color fallbacks
        if (Object.keys(this.textures).length === 0) {
            console.log('No DDS textures found, using color-based materials');
        } else {
            console.log(`Successfully loaded ${Object.keys(this.textures).length} DDS textures`);
        }
    }

    setSkinTone(tone) {
        if (!this.headMesh || !this.headMesh.material) return;
        
        // Define skin tone colors for fallback
        const skinColors = {
            white: { color: 0xffdbac, specular: 0x222222 },
            tan: { color: 0xd4a373, specular: 0x111111 },
            dark: { color: 0x8b6239, specular: 0x050505 }
        };
        
        const selectedSkin = skinColors[tone] || skinColors.white;
        
        if (this.textures[tone]) {
            // Apply texture if available
            this.headMesh.material.map = this.textures[tone];
            this.headMesh.material.color.setHex(0xffffff); // Reset color to white when using texture
            this.headMesh.material.needsUpdate = true;
            console.log(`Applied ${tone} skin texture`);
        } else {
            // Fallback to color-based material
            this.headMesh.material.map = null;
            this.headMesh.material.color.setHex(selectedSkin.color);
            this.headMesh.material.specular.setHex(selectedSkin.specular);
            this.headMesh.material.needsUpdate = true;
            console.log(`Applied ${tone} skin color (no texture available)`);
        }
    }
}