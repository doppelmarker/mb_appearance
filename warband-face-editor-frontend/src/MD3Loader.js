import * as THREE from 'three';

/**
 * MD3 Loader for Three.js
 * Loads Quake 3 MD3 models with vertex animation support
 * Specifically adapted for Mount & Blade face morphs
 */
export class MD3Loader {
    constructor() {
        this.littleEndian = true;
    }

    load(url, onLoad, onProgress, onError) {
        const loader = new THREE.FileLoader();
        loader.setResponseType('arraybuffer');
        
        loader.load(
            url,
            (data) => {
                try {
                    const result = this.parse(data);
                    onLoad(result);
                } catch (error) {
                    if (onError) onError(error);
                    else console.error('MD3Loader:', error);
                }
            },
            onProgress,
            onError
        );
    }

    parse(buffer) {
        const data = new DataView(buffer);
        let offset = 0;

        // Read MD3 header
        const header = this.readHeader(data, offset);
        offset = header.offset;

        if (header.ident !== 'IDP3') {
            throw new Error('Not a valid MD3 file');
        }

        // Read frames (vertex animation keyframes)
        const frames = [];
        offset = header.framesOffset;
        for (let i = 0; i < header.numFrames; i++) {
            const frame = this.readFrame(data, offset);
            frames.push(frame);
            offset += 56; // Frame struct size
        }

        // Read surfaces (meshes)
        const surfaces = [];
        offset = header.surfacesOffset;
        
        for (let i = 0; i < header.numSurfaces; i++) {
            const surface = this.readSurface(data, offset, frames);
            surfaces.push(surface);
            offset = surface.nextOffset;
        }

        // For Mount & Blade faces, we only care about the first surface
        if (surfaces.length === 0) {
            throw new Error('No surfaces found in MD3 file');
        }

        return {
            frames: frames,
            surfaces: surfaces,
            surface: surfaces[0], // Main head mesh
            header: header
        };
    }

    readHeader(data, offset) {
        const ident = String.fromCharCode(
            data.getUint8(offset),
            data.getUint8(offset + 1),
            data.getUint8(offset + 2),
            data.getUint8(offset + 3)
        );

        return {
            ident: ident,
            version: data.getInt32(offset + 4, this.littleEndian),
            name: this.readString(data, offset + 8, 64),
            flags: data.getInt32(offset + 72, this.littleEndian),
            numFrames: data.getInt32(offset + 76, this.littleEndian),
            numTags: data.getInt32(offset + 80, this.littleEndian),
            numSurfaces: data.getInt32(offset + 84, this.littleEndian),
            numSkins: data.getInt32(offset + 88, this.littleEndian),
            framesOffset: data.getInt32(offset + 92, this.littleEndian),
            tagsOffset: data.getInt32(offset + 96, this.littleEndian),
            surfacesOffset: data.getInt32(offset + 100, this.littleEndian),
            eofOffset: data.getInt32(offset + 104, this.littleEndian),
            offset: offset + 108
        };
    }

    readFrame(data, offset) {
        return {
            mins: new THREE.Vector3(
                data.getFloat32(offset, this.littleEndian),
                data.getFloat32(offset + 4, this.littleEndian),
                data.getFloat32(offset + 8, this.littleEndian)
            ),
            maxs: new THREE.Vector3(
                data.getFloat32(offset + 12, this.littleEndian),
                data.getFloat32(offset + 16, this.littleEndian),
                data.getFloat32(offset + 20, this.littleEndian)
            ),
            origin: new THREE.Vector3(
                data.getFloat32(offset + 24, this.littleEndian),
                data.getFloat32(offset + 28, this.littleEndian),
                data.getFloat32(offset + 32, this.littleEndian)
            ),
            radius: data.getFloat32(offset + 36, this.littleEndian),
            name: this.readString(data, offset + 40, 16)
        };
    }

    readSurface(data, offset, frames) {
        const surfaceStart = offset;
        
        // Read surface header
        const ident = String.fromCharCode(
            data.getUint8(offset),
            data.getUint8(offset + 1),
            data.getUint8(offset + 2),
            data.getUint8(offset + 3)
        );

        const name = this.readString(data, offset + 4, 64);
        const flags = data.getInt32(offset + 68, this.littleEndian);
        const numFrames = data.getInt32(offset + 72, this.littleEndian);
        const numShaders = data.getInt32(offset + 76, this.littleEndian);
        const numVerts = data.getInt32(offset + 80, this.littleEndian);
        const numTriangles = data.getInt32(offset + 84, this.littleEndian);
        const trianglesOffset = data.getInt32(offset + 88, this.littleEndian);
        const shadersOffset = data.getInt32(offset + 92, this.littleEndian);
        const stOffset = data.getInt32(offset + 96, this.littleEndian);
        const vertexOffset = data.getInt32(offset + 100, this.littleEndian);
        const endOffset = data.getInt32(offset + 104, this.littleEndian);

        // Read triangles
        const indices = [];
        offset = surfaceStart + trianglesOffset;
        for (let i = 0; i < numTriangles; i++) {
            indices.push(
                data.getInt32(offset, this.littleEndian),
                data.getInt32(offset + 4, this.littleEndian),
                data.getInt32(offset + 8, this.littleEndian)
            );
            offset += 12;
        }

        // Read texture coordinates
        const uvs = [];
        offset = surfaceStart + stOffset;
        for (let i = 0; i < numVerts; i++) {
            uvs.push(
                data.getFloat32(offset, this.littleEndian),
                1 - data.getFloat32(offset + 4, this.littleEndian) // Flip V
            );
            offset += 8;
        }

        // Read vertices for each frame (vertex animation)
        const frameVertices = [];
        const frameNormals = [];
        
        for (let f = 0; f < numFrames; f++) {
            const vertices = [];
            const normals = [];
            
            offset = surfaceStart + vertexOffset + (f * numVerts * 8); // 8 bytes per vertex
            
            for (let i = 0; i < numVerts; i++) {
                // Read compressed vertex position
                // MD3 uses 1/64 scale, but Mount & Blade might need additional scaling
                const scale = 64.0 * 50.0; // 50x additional scale to match OBJ import scale
                const x = data.getInt16(offset, this.littleEndian) / scale;
                const y = data.getInt16(offset + 2, this.littleEndian) / scale;
                const z = data.getInt16(offset + 4, this.littleEndian) / scale;
                
                vertices.push(x, y, z);
                
                // Read normal (encoded as two bytes for spherical coordinates)
                const normal = this.decodeNormal(
                    data.getUint8(offset + 6),
                    data.getUint8(offset + 7)
                );
                normals.push(normal.x, normal.y, normal.z);
                
                offset += 8;
            }
            
            frameVertices.push(vertices);
            frameNormals.push(normals);
        }

        return {
            name: name,
            numFrames: numFrames,
            numVerts: numVerts,
            numTriangles: numTriangles,
            indices: indices,
            uvs: uvs,
            frameVertices: frameVertices,
            frameNormals: frameNormals,
            nextOffset: surfaceStart + endOffset
        };
    }

    decodeNormal(lat, lng) {
        // Convert from byte angles to radians
        const latRad = lat * (2 * Math.PI) / 255;
        const lngRad = lng * (2 * Math.PI) / 255;
        
        // Convert from spherical to cartesian coordinates
        return new THREE.Vector3(
            Math.cos(latRad) * Math.sin(lngRad),
            Math.sin(latRad) * Math.sin(lngRad),
            Math.cos(lngRad)
        );
    }

    readString(data, offset, maxLength) {
        let str = '';
        for (let i = 0; i < maxLength; i++) {
            const char = data.getUint8(offset + i);
            if (char === 0) break;
            str += String.fromCharCode(char);
        }
        return str;
    }

    /**
     * Create Three.js morph targets from MD3 vertex animation frames
     * For Mount & Blade faces, specific frames correspond to morphs
     */
    createMorphTargets(surface, morphFrameMap) {
        const geometry = new THREE.BufferGeometry();
        
        // Use frame 0 as the base/reference pose
        const baseVertices = new Float32Array(surface.frameVertices[0]);
        const baseNormals = new Float32Array(surface.frameNormals[0]);
        const uvArray = new Float32Array(surface.uvs);
        const indexArray = new Uint16Array(surface.indices);
        
        // Set base geometry
        geometry.setAttribute('position', new THREE.BufferAttribute(baseVertices, 3));
        geometry.setAttribute('normal', new THREE.BufferAttribute(baseNormals, 3));
        geometry.setAttribute('uv', new THREE.BufferAttribute(uvArray, 2));
        geometry.setIndex(new THREE.BufferAttribute(indexArray, 1));
        
        // Create morph attributes
        const morphPositions = [];
        const morphNormals = [];
        
        // Map frame numbers to morph indices based on Mount & Blade's system
        // Frame 10 = morph 0 (chin), Frame 20 = morph 1 (jaw), etc.
        for (let morphIndex = 0; morphIndex < 27; morphIndex++) {
            const frameNumber = (morphIndex + 1) * 10; // 10, 20, 30... 270
            
            if (frameNumber < surface.numFrames) {
                const frameVerts = new Float32Array(surface.frameVertices[frameNumber]);
                const frameNorms = new Float32Array(surface.frameNormals[frameNumber]);
                
                morphPositions.push(new THREE.BufferAttribute(frameVerts, 3));
                morphNormals.push(new THREE.BufferAttribute(frameNorms, 3));
            }
        }
        
        // Assign morph attributes
        if (morphPositions.length > 0) {
            geometry.morphAttributes.position = morphPositions;
            geometry.morphAttributes.normal = morphNormals;
        }
        
        return geometry;
    }
}