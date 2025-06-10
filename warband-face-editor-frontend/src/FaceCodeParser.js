export class FaceCodeParser {
    // Mapping corrected based on actual testing - rotating the circular permutations
    static sliderToFrameMapping = {
        // Core sliders that work correctly (no change needed)
        5: 22,    // 'Eyebrow Depth' -> T220 ✓
        7: 16,    // 'Eyebrow Position' -> T160 ✓  
        8: 14,    // 'Eyelids' -> T140 ✓
        9: 13,    // 'Eye Depth' -> T130 ✓
        10: 12,   // 'Eye Shape' -> T120 ✓
        11: 11,   // 'Eye to Eye Dist' -> T110 ✓
        12: 15,   // 'Eye Width' -> T150 ✓
        13: 10,   // 'Cheek Bones' -> T100 ✓
        14: 9,    // 'Nose Bridge' -> T90 ✓
        16: 8,    // 'Nose Size' -> T80 ✓
        17: 7,    // 'Nose Width' -> T70 ✓
        18: 6,    // 'Nose Height' -> T60 ✓
        19: 5,    // 'Cheeks' -> T50 ✓

        // Cycle 1 (5 sliders) - rotated to fix the circular permutation
        // Face Width should get Face Depth's frame, Face Depth should get Mouth Width's frame, etc.
        0: 19,    // 'Face Width' -> T190 (was controlling Face Depth, now controls Face Width)
        2: 3,     // 'Face Depth' -> T30 (was controlling Mouth Width, now controls Face Depth)  
        20: 20,   // 'Mouth Width' -> T200 (was controlling Temple Width, now controls Mouth Width)
        3: 23,    // 'Temple Width' -> T230 (was controlling Eyebrow Height, now controls Temple Width)
        6: 17,    // 'Eyebrow Height' -> T170 (was controlling Face Width, now controls Eyebrow Height)

        // Cycle 2 (9 sliders) - rotated to fix the circular permutation
        1: 4,     // 'Face Ratio' -> T40 (was controlling Mouth-Nose Dist, now controls Face Ratio)
        21: 25,   // 'Mouth-Nose Distance' -> T250 (was controlling Jaw Width, now controls Mouth-Nose Dist)
        23: 24,   // 'Jaw Width' -> T240 (was controlling Nose Shape, now controls Jaw Width)
        15: 27,   // 'Nose Shape' -> T270 (was controlling Chin Shape, now controls Nose Shape)
        25: 26,   // 'Chin Shape' -> T260 (was controlling Chin Forward, now controls Chin Shape)
        24: 1,    // 'Chin Forward' -> T10 (was controlling Chin Size, now controls Chin Forward)
        26: 2,    // 'Chin Size' -> T20 (was controlling Jaw Position, now controls Chin Size)
        22: 21,   // 'Jaw Position' -> T210 (was controlling Eyebrow Shape, now controls Jaw Position)
        4: 18     // 'Eyebrow Shape' -> T180 (was controlling Face Ratio, now controls Eyebrow Shape)
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
        14: 26,   // 'Nose Bridge' -> morph_key_26 (SWAPPED: was 8, now gets 7)
        13: 25,   // 'Cheek Bones' -> morph_key_25 (SWAPPED: was 9, now gets 7)
        11: 24,   // 'Eye to Eye Dist' -> morph_key_24 (SWAPPED: was 10, now gets 7)
        10: 23,   // 'Eye Shape' -> morph_key_23 (SWAPPED: was 11, now gets 7)
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
        15: 11,   // 'Nose Shape' -> morph_key_11 (SWAPPED: was 23, now gets 0)
        23: 10,   // 'Jaw Width' -> morph_key_10 (SWAPPED: was 24, now gets 0)
        24: 9,    // 'Chin Forward' -> morph_key_09 (SWAPPED: was 25, now gets 0)
        25: 8     // 'Chin Shape' -> morph_key_08 (SWAPPED: was 26, now gets 0)
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
            if (sliderIndex !== undefined && sliderIndex < 27) {
                sliderValues[sliderIndex] = morphKeys[morphKey];
            }
        }
        
        // Note: Hidden morphs (like morph 27) are preserved in morphKeys but not exposed in sliderValues
        
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
        
        // IMPORTANT: Set hidden morph 27 to 7 (Mount & Blade default)
        // This is a hidden morph not exposed in the UI but required for proper face rendering
        morphKeys[27] = 7;
        
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
        
        // Build block 0 with default appearance attributes
        // Mount & Blade uses skin = 2 as default
        let block0Value = 0n;
        // skin value 2 goes in bits 12-17
        block0Value |= 2n << 12n;
        const block0 = block0Value.toString(16).padStart(16, '0');
        
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