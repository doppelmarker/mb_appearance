// Test face code parsing with known examples
import { FaceCodeParser } from './src/FaceCodeParser.js';

// Test case from face_code_internal_format.txt
const testFaceCode = '0x000000018000004136db79b6db6db6fb7fffff6d77bf36db0000000000000000';

console.log('Testing face code:', testFaceCode);
console.log('');

// Parse the face code
const parsed = FaceCodeParser.parse(testFaceCode);

console.log('Parsed morphs (slider values):');
console.log('==============================');

const sliderNames = [
    'Face Width',           // 0
    'Face Ratio',          // 1
    'Face Depth',          // 2
    'Temple Width',        // 3
    'Eyebrow Shape',       // 4
    'Eyebrow Depth',       // 5
    'Eyebrow Height',      // 6
    'Eyebrow Position',    // 7
    'Eyelids',            // 8
    'Eye Depth',          // 9
    'Eye Shape',          // 10
    'Eye to Eye Dist',    // 11
    'Eye Width',          // 12
    'Cheek Bones',        // 13
    'Nose Bridge',        // 14
    'Nose Shape',         // 15
    'Nose Size',          // 16
    'Nose Width',         // 17
    'Nose Height',        // 18
    'Cheeks',             // 19
    'Mouth Width',        // 20
    'Mouth-Nose Distance', // 21
    'Jaw Position',       // 22
    'Jaw Width',          // 23
    'Chin Forward',       // 24
    'Chin Shape',         // 25
    'Chin Size',          // 26
];

for (let i = 0; i < parsed.morphs.length; i++) {
    console.log(`Slider ${i} (${sliderNames[i] || 'Unknown'}): ${parsed.morphs[i]}`);
}

console.log('\nRaw morph keys:');
console.log('===============');
for (let i = 0; i < parsed.morphKeys.length; i++) {
    console.log(`morph_key_${i.toString().padStart(2, '0')}: ${parsed.morphKeys[i]}`);
}

console.log('\nAppearance attributes:');
console.log('=====================');
console.log('Hair:', parsed.appearance.hair);
console.log('Beard:', parsed.appearance.beard);
console.log('Skin:', parsed.appearance.skin);
console.log('Hair texture:', parsed.appearance.hair_texture);
console.log('Hair color:', parsed.appearance.hair_color);
console.log('Age:', parsed.appearance.age);
console.log('Skin color:', parsed.appearance.skin_color);

// Test generation
console.log('\n\nTesting face code generation:');
console.log('=============================');

// Create test slider values
const testSliders = new Array(27).fill(0);
// Set some test values matching the expected morphs from the original
testSliders[26] = 3; // Chin Size (morph 0)
testSliders[20] = 6; // Mouth Width (morph 6)
testSliders[18] = 6; // Nose Height (morph 8)

const generated = FaceCodeParser.generate(testSliders);
console.log('Generated face code:', generated);

// Re-parse to verify
const reparsed = FaceCodeParser.parse(generated);
console.log('\nRe-parsed values:');
console.log('Chin Size (slider 26):', reparsed.morphs[26], '(expected 3)');
console.log('Mouth Width (slider 20):', reparsed.morphs[20], '(expected 6)');
console.log('Nose Height (slider 18):', reparsed.morphs[18], '(expected 6)');