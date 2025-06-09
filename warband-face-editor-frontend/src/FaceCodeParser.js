export class FaceCodeParser {
    /**
     * Parse a Mount & Blade Warband face code into components
     * For MVP, we focus on extracting the first 8 morphs from block 1
     */
    static parse(faceCode) {
        // Remove 0x prefix if present
        if (faceCode.startsWith('0x')) {
            faceCode = faceCode.slice(2);
        }
        
        // Validate face code length
        if (faceCode.length !== 64) {
            throw new Error(`Face code must be 64 characters, got ${faceCode.length}`);
        }
        
        // Validate hex characters
        if (!/^[0-9a-fA-F]+$/.test(faceCode)) {
            throw new Error('Face code must contain only hexadecimal characters');
        }
        
        // Split into 4 blocks of 16 hex chars each
        const blocks = [
            faceCode.slice(0, 16),   // Block 0: appearance attributes
            faceCode.slice(16, 32),  // Block 1: morphs 0-20
            faceCode.slice(32, 48),  // Block 2: morphs 21-42
            faceCode.slice(48, 64)   // Block 3: unused
        ];
        
        // Extract all 27 morphs from blocks 1 and 2
        const morphs = [];
        
        // Block 1 contains morphs 0-20 (21 morphs * 3 bits = 63 bits)
        const block1 = blocks[1];
        for (let i = 0; i < 21; i++) {
            const byteOffset = Math.floor((i * 3) / 8);
            const bitOffset = (i * 3) % 8;
            const hexOffset = byteOffset * 2;
            
            // Get the morph value (3 bits)
            let value;
            if (bitOffset <= 5) {
                // Morph fits within single byte
                const byte = parseInt(block1.substr(hexOffset, 2), 16);
                value = (byte >> bitOffset) & 0x7;
            } else {
                // Morph crosses byte boundary
                const byte1 = parseInt(block1.substr(hexOffset, 2), 16);
                const byte2 = parseInt(block1.substr(hexOffset + 2, 2), 16);
                const combined = byte1 | (byte2 << 8);
                value = (combined >> bitOffset) & 0x7;
            }
            morphs.push(value);
        }
        
        // Block 2 contains morphs 21-26 (6 more morphs)
        const block2 = blocks[2];
        for (let i = 0; i < 6; i++) {
            const byteOffset = Math.floor((i * 3) / 8);
            const bitOffset = (i * 3) % 8;
            const hexOffset = byteOffset * 2;
            
            let value;
            if (bitOffset <= 5) {
                const byte = parseInt(block2.substr(hexOffset, 2), 16);
                value = (byte >> bitOffset) & 0x7;
            } else {
                const byte1 = parseInt(block2.substr(hexOffset, 2), 16);
                const byte2 = parseInt(block2.substr(hexOffset + 2, 2), 16);
                const combined = byte1 | (byte2 << 8);
                value = (combined >> bitOffset) & 0x7;
            }
            morphs.push(value);
        }
        
        // Also extract some appearance attributes from block 0 for future use
        const block0Int = parseInt(blocks[0], 16);
        
        const appearance = {
            hair: block0Int & 0x3F,                    // bits 0-5
            beard: (block0Int >> 6) & 0x3F,            // bits 6-11
            skin: (block0Int >> 12) & 0x3F,            // bits 12-17
            hair_texture: (block0Int >> 18) & 0x3F,    // bits 18-23
            hair_color: (block0Int >> 24) & 0x3F,      // bits 24-29
            age: (block0Int >> 30) & 0x3F,             // bits 30-35
            skin_color: (block0Int >> 36) & 0x3F       // bits 36-41
        };
        
        return {
            morphs: morphs,
            appearance: appearance,
            raw: faceCode
        };
    }
    
    /**
     * Generate a face code from morph values
     * Encodes all 27 morphs
     */
    static generate(morphValues) {
        // Ensure we have at least 27 values
        const morphs = [...morphValues];
        while (morphs.length < 27) {
            morphs.push(0);
        }
        
        // Build block 1 with morphs 0-20
        let block1Hex = '';
        const block1Bits = [];
        for (let i = 0; i < 21; i++) {
            const value = Math.min(7, Math.max(0, morphs[i] || 0)); // Clamp to 0-7
            // Add 3 bits for this morph
            block1Bits.push((value >> 2) & 1);
            block1Bits.push((value >> 1) & 1);
            block1Bits.push(value & 1);
        }
        
        // Convert bits to hex
        for (let i = 0; i < 64; i += 4) {
            let nibble = 0;
            for (let j = 0; j < 4 && i + j < block1Bits.length; j++) {
                nibble |= (block1Bits[i + j] << j);
            }
            block1Hex = nibble.toString(16) + block1Hex;
        }
        block1Hex = block1Hex.padStart(16, '0');
        
        // Build block 2 with morphs 21-26
        let block2Hex = '';
        const block2Bits = [];
        for (let i = 21; i < 27; i++) {
            const value = Math.min(7, Math.max(0, morphs[i] || 0));
            block2Bits.push((value >> 2) & 1);
            block2Bits.push((value >> 1) & 1);
            block2Bits.push(value & 1);
        }
        
        // Pad remaining bits
        while (block2Bits.length < 64) {
            block2Bits.push(0);
        }
        
        // Convert bits to hex
        for (let i = 0; i < 64; i += 4) {
            let nibble = 0;
            for (let j = 0; j < 4; j++) {
                nibble |= (block2Bits[i + j] << j);
            }
            block2Hex = nibble.toString(16) + block2Hex;
        }
        block2Hex = block2Hex.padStart(16, '0');
        
        // Default values for other blocks
        const block0 = "0000000000000000"; // Default appearance
        const block3 = "0000000000000000"; // Unused
        
        return `0x${block0}${block1Hex}${block2Hex}${block3}`;
    }
    
    /**
     * Validate if a string is a valid face code
     */
    static validate(faceCode) {
        try {
            this.parse(faceCode);
            return true;
        } catch (error) {
            return false;
        }
    }
    
    /**
     * Convert M&B skin index to skin tone name
     */
    static getSkinTone(skinIndex) {
        // Based on M&B skin values from documentation
        if (skinIndex === 0) return 'white';
        if (skinIndex === 16) return 'light';
        if (skinIndex === 32) return 'tan';
        if (skinIndex === 48) return 'dark';
        if (skinIndex === 64) return 'black';
        
        // Approximate for in-between values
        if (skinIndex < 24) return 'white';
        if (skinIndex < 40) return 'tan';
        return 'dark';
    }
}