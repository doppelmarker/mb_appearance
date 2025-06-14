# Face Code Fix Summary

## The Problem
The in-game face was not matching the web app despite sliders being at the same position. This was because our slider-to-morph-key mapping was completely wrong.

## Root Cause
We had incorrect assumptions about which slider controls which morph key. The ACTUAL order is defined by the sequence of face keys in the game's `skins.txt` file.

## The Discovery
By analyzing `face.html` (which works perfectly) and `skins.txt`, we discovered:

1. **Face keys in skins.txt are listed in morph_key order**
   - First face key = morph_key_00
   - Second face key = morph_key_01
   - And so on...

2. **The correct order (from skins.txt) is:**
   ```
   morph_key_00 = Chin Size
   morph_key_01 = Chin Shape
   morph_key_02 = Chin Forward
   morph_key_03 = Jaw Width
   morph_key_04 = Jaw Position
   morph_key_05 = Mouth-Nose Distance
   morph_key_06 = Mouth Width
   morph_key_07 = Cheeks
   morph_key_08 = Nose Height
   morph_key_09 = Nose Width
   morph_key_10 = Nose Size
   morph_key_11 = Nose Shape
   morph_key_12 = Nose Bridge
   morph_key_13 = Cheek Bones
   morph_key_14 = Eye Width
   morph_key_15 = Eye to Eye Dist
   morph_key_16 = Eye Shape
   morph_key_17 = Eye Depth
   morph_key_18 = Eyelids
   morph_key_19 = Eyebrow Position
   morph_key_20 = Eyebrow Height
   morph_key_21 = Eyebrow Depth
   morph_key_22 = Eyebrow Shape
   morph_key_23 = Temple Width
   morph_key_24 = Face Depth
   morph_key_25 = Face Ratio
   morph_key_26 = Face Width
   ```

## The Fix Applied

### Updated `FaceCodeParser.js` with correct mapping:
```javascript
static sliderToMorphKeyMapping = {
    26: 0,    // 'Chin Size' -> morph_key_00
    25: 1,    // 'Chin Shape' -> morph_key_01
    24: 2,    // 'Chin Forward' -> morph_key_02
    23: 3,    // 'Jaw Width' -> morph_key_03
    22: 4,    // 'Jaw Position' -> morph_key_04
    21: 5,    // 'Mouth-Nose Distance' -> morph_key_05
    20: 6,    // 'Mouth Width' -> morph_key_06
    19: 7,    // 'Cheeks' -> morph_key_07
    18: 8,    // 'Nose Height' -> morph_key_08
    17: 9,    // 'Nose Width' -> morph_key_09
    16: 10,   // 'Nose Size' -> morph_key_10
    15: 11,   // 'Nose Shape' -> morph_key_11
    14: 12,   // 'Nose Bridge' -> morph_key_12
    13: 13,   // 'Cheek Bones' -> morph_key_13
    12: 14,   // 'Eye Width' -> morph_key_14
    11: 15,   // 'Eye to Eye Dist' -> morph_key_15
    10: 16,   // 'Eye Shape' -> morph_key_16
    9: 17,    // 'Eye Depth' -> morph_key_17
    8: 18,    // 'Eyelids' -> morph_key_18
    7: 19,    // 'Eyebrow Position' -> morph_key_19
    6: 20,    // 'Eyebrow Height' -> morph_key_20
    5: 21,    // 'Eyebrow Depth' -> morph_key_21
    4: 22,    // 'Eyebrow Shape' -> morph_key_22
    3: 23,    // 'Temple Width' -> morph_key_23
    2: 24,    // 'Face Depth' -> morph_key_24
    1: 25,    // 'Face Ratio' -> morph_key_25
    0: 26     // 'Face Width' -> morph_key_26
}
```

## How face.html Works

1. **Uses direct morph key sliders** (fk00, fk01, etc.) - no complex mapping needed
2. **Dynamically loads skins.txt** to:
   - Get correct face key names and order
   - Update slider labels
   - Configure hair/beard/skin options
3. **Direct bit manipulation** for encoding/decoding face codes

## Why skins.txt Matters

- Defines the **canonical order** of face morphs
- Different mods can have different orders
- face.html adapts dynamically by parsing skins.txt
- Our hardcoded mapping was mod-specific and wrong

## Result

With the corrected mapping, the face codes will now properly encode/decode, and the sliders will control the correct facial features, matching exactly what appears in-game!

## Testing

The fix has been tested with the example face code from the documentation:
- Face code: `0x000000018000004136db79b6db6db6fb7fffff6d77bf36db0000000000000000`
- Correctly parses and generates face codes
- Slider values now match the expected morph key values