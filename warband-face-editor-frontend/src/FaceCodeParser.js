export class FaceCodeParser {
    // Mapping from frontend slider index to frame INDEX (not frame name) based on MD3 structure
    static sliderToFrameMapping = {
        // The MD3 has frames: T0, T10, T20, T30... T280 (29 frames total)
        // Frame names correspond to the original M&B morph frame numbers
        26: 1,    // 'Chin Size' -> frame index 1 (T10)
        22: 2,    // 'Jaw Position' -> frame index 2 (T20)
        20: 3,    // 'Mouth Width' -> frame index 3 (T30)
        21: 4,    // 'Mouth-Nose Distance' -> frame index 4 (T40)
        19: 5,    // 'Cheeks' -> frame index 5 (T50)
        18: 6,    // 'Nose Height' -> frame index 6 (T60)
        17: 7,    // 'Nose Width' -> frame index 7 (T70)
        16: 8,    // 'Nose Size' -> frame index 8 (T80)
        14: 9,    // 'Nose Bridge' -> frame index 9 (T90)
        13: 10,   // 'Cheek Bones' -> frame index 10 (T100)
        11: 11,   // 'Eye to Eye Dist' -> frame index 11 (T110)
        10: 12,   // 'Eye Shape' -> frame index 12 (T120)
        9: 13,    // 'Eye Depth' -> frame index 13 (T130)
        8: 14,    // 'Eyelids' -> frame index 14 (T140)
        12: 15,   // 'Eye Width' -> frame index 15 (T150)
        7: 16,    // 'Eyebrow Position' -> frame index 16 (T160)
        
        // Additional frames if available
        0: 17,    // 'Face Width' -> frame index 17 (T170)
        1: 18,    // 'Face Ratio' -> frame index 18 (T180)
        2: 19,    // 'Face Depth' -> frame index 19 (T190)
        3: 20,    // 'Temple Width' -> frame index 20 (T200)
        4: 21,    // 'Eyebrow Shape' -> frame index 21 (T210)
        5: 22,    // 'Eyebrow Depth' -> frame index 22 (T220)
        6: 23,    // 'Eyebrow Height' -> frame index 23 (T230)
        15: 24,   // 'Nose Shape' -> frame index 24 (T240)
        23: 25,   // 'Jaw Width' -> frame index 25 (T250)
        24: 26,   // 'Chin Forward' -> frame index 26 (T260)
        25: 27    // 'Chin Shape' -> frame index 27 (T270)
    };

    // Legacy mapping for face code parsing (morph key based)
    static sliderToMorphKeyMapping = {
        26: 0,    // 'Chin Size' -> morph_key_00
        22: 1,    // 'Jaw Position' -> morph_key_01
        20: 2,    // 'Mouth Width' -> morph_key_02
        21: 3,    // 'Mouth-Nose Distance' -> morph_key_03
        19: 4,    // 'Cheeks' -> morph_key_04
        18: 5,    // 'Nose Height' -> morph_key_05
        17: 6,    // 'Nose Width' -> morph_key_06
        16: 7,    // 'Nose Size' -> morph_key_07
        14: 8,    // 'Nose Bridge' -> morph_key_08
        13: 9,    // 'Cheek Bones' -> morph_key_09
        11: 10,   // 'Eye to Eye Dist' -> morph_key_10
        10: 11,   // 'Eye Shape' -> morph_key_11
        9: 12,    // 'Eye Depth' -> morph_key_12
        8: 13,    // 'Eyelids' -> morph_key_13
        12: 14,   // 'Eye Width' -> morph_key_14
        7: 15,    // 'Eyebrow Position' -> morph_key_15
        
        // Unmapped sliders
        0: 16,    // 'Face Width' -> morph_key_16
        1: 17,    // 'Face Ratio' -> morph_key_17
        2: 18,    // 'Face Depth' -> morph_key_18
        3: 19,    // 'Temple Width' -> morph_key_19
        4: 20,    // 'Eyebrow Shape' -> morph_key_20
        5: 21,    // 'Eyebrow Depth' -> morph_key_21
        6: 22,    // 'Eyebrow Height' -> morph_key_22
        15: 23,   // 'Nose Shape' -> morph_key_23
        23: 24,   // 'Jaw Width' -> morph_key_24
        24: 25,   // 'Chin Forward' -> morph_key_25
        25: 26    // 'Chin Shape' -> morph_key_26
    };

    // Reverse mapping from morph key to slider index
    static morphKeyToSliderMapping = {};
    
    // Initialize reverse mapping
    static {
        for (const [sliderIndex, morphKey] of Object.entries(this.sliderToMorphKeyMapping)) {
            this.morphKeyToSliderMapping[morphKey] = parseInt(sliderIndex);
        }
    }

    /**
     * Parse a Mount & Blade Warband face code into components
     * Extracts all 43 morph keys and maps them to slider values
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
        
        // Extract all 43 morph keys from blocks 1 and 2
        const morphKeys = new Array(43).fill(0);
        
        // Block 1 contains morph_key_00 through morph_key_20 (21 morphs * 3 bits = 63 bits)
        const block1Int = BigInt('0x' + blocks[1]);
        for (let i = 0; i < 21; i++) {
            const bitPosition = BigInt(i * 3);
            const value = Number((block1Int >> bitPosition) & 0x7n);
            morphKeys[i] = value;
        }
        
        // Block 2 contains morph_key_21 through morph_key_42 (22 morphs * 3 bits = 66 bits)
        const block2Int = BigInt('0x' + blocks[2]);
        for (let i = 0; i < 22; i++) {
            const bitPosition = BigInt(i * 3);
            const value = Number((block2Int >> bitPosition) & 0x7n);
            morphKeys[21 + i] = value;
        }
        
        // Convert morph keys to slider values using our mapping
        const sliderValues = new Array(27).fill(0);
        for (let morphKey = 0; morphKey < morphKeys.length; morphKey++) {
            const sliderIndex = this.morphKeyToSliderMapping[morphKey];
            if (sliderIndex !== undefined) {
                sliderValues[sliderIndex] = morphKeys[morphKey];
            }
        }
        
        // Also extract appearance attributes from block 0
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
            morphs: sliderValues,      // Now correctly mapped to slider indices
            morphKeys: morphKeys,      // Raw morph key values for debugging
            appearance: appearance,
            raw: faceCode
        };
    }
    
    /**
     * Generate a face code from slider values
     * Maps slider values to correct morph keys and encodes them
     */
    static generate(sliderValues) {
        // Ensure we have at least 27 values
        const sliders = [...sliderValues];
        while (sliders.length < 27) {
            sliders.push(0);
        }
        
        // Create array of 43 morph keys initialized to 0
        const morphKeys = new Array(43).fill(0);
        
        // Map slider values to correct morph keys
        for (let sliderIndex = 0; sliderIndex < sliders.length; sliderIndex++) {
            const morphKey = this.sliderToMorphKeyMapping[sliderIndex];
            if (morphKey !== undefined) {
                morphKeys[morphKey] = Math.min(7, Math.max(0, sliders[sliderIndex] || 0));
            }
        }
        
        // Build block 1 with morph_key_00 through morph_key_20
        let block1Value = 0n;
        for (let i = 0; i < 21; i++) {
            const value = BigInt(morphKeys[i]);
            const bitPosition = BigInt(i * 3);
            block1Value |= value << bitPosition;
        }
        const block1Hex = block1Value.toString(16).padStart(16, '0');
        
        // Build block 2 with morph_key_21 through morph_key_42
        let block2Value = 0n;
        for (let i = 0; i < 22; i++) {
            const value = BigInt(morphKeys[21 + i]);
            const bitPosition = BigInt(i * 3);
            block2Value |= value << bitPosition;
        }
        const block2Hex = block2Value.toString(16).padStart(16, '0');
        
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