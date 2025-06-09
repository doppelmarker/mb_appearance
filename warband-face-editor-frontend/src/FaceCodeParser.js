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
        
        // Extract first 8 morphs from block 1
        const morphs = [];
        const block1Int = parseInt(blocks[1], 16);
        
        // Each morph is 3 bits, extract first 8
        for (let i = 0; i < 8; i++) {
            const bitPosition = i * 3;
            const morphValue = (block1Int >> bitPosition) & 0x7; // Extract 3 bits (0-7)
            morphs.push(morphValue);
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
     * For MVP, we only encode the first 8 morphs
     */
    static generate(morphValues) {
        // Ensure we have at least 8 values
        const morphs = [...morphValues];
        while (morphs.length < 8) {
            morphs.push(0);
        }
        
        // Build block 1 with first 8 morphs
        let block1 = 0;
        for (let i = 0; i < 8; i++) {
            const value = Math.min(7, Math.max(0, morphs[i])); // Clamp to 0-7
            block1 |= (value & 0x7) << (i * 3);
        }
        
        // For MVP, use default values for other blocks
        const block0 = "0000000000000000"; // Default appearance
        const block1Hex = block1.toString(16).padStart(16, '0');
        const block2 = "0000000000000000"; // No morphs 21-42
        const block3 = "0000000000000000"; // Unused
        
        return `0x${block0}${block1Hex}${block2}${block3}`;
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