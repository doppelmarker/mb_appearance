# What is skins.txt and how does face.html use it?

## What is skins.txt?

`skins.txt` is a Mount & Blade module file that defines:

1. **Race definitions** (e.g., man, woman)
2. **Face key mappings** - The ORDER and properties of facial morphs
3. **Mesh references** - Hair, beard, and body meshes available
4. **Material definitions** - Skin tones and hair colors
5. **Sound definitions** - Voice sounds for each race

## How face.html reads and uses skins.txt:

### 1. **Drag and Drop Support**
```javascript
droparea.ondrop = function(e) {
    // User can drag skins.txt file onto the page
    parse_skins_txt(e.target.result);
    set_up_dyn_interface();
}
```

### 2. **Dynamic Interface Generation**
face.html dynamically creates the interface based on skins.txt:
- Updates slider labels with the actual face key names
- Creates dropdown menus for hair/beard/skin selections
- Hides unused morph keys

### 3. **Face Key Order Discovery**
The ORDER of face keys in skins.txt determines the morph_key mapping:
```
male_head 28 skinkey_chin_size ... skinkey_chin_shape ... skinkey_chin_forward ...
```
- First face key (chin_size) = morph_key_00
- Second face key (chin_shape) = morph_key_01
- And so on...

### 4. **Race-specific Configuration**
Different races can have:
- Different face key orders
- Different number of active morphs
- Different mesh options

## Why This Matters:

1. **face.html works perfectly because:**
   - It reads skins.txt to get the EXACT face key order
   - Dynamically updates its interface to match
   - Uses raw morph_key indices (fk00, fk01, etc.)

2. **Our implementation was wrong because:**
   - We hardcoded incorrect slider-to-morph mappings
   - Didn't respect the skins.txt face key order
   - Made assumptions about which slider controls which morph

## The Fix:

We've now corrected our `sliderToMorphKeyMapping` to match the exact order from skins.txt, ensuring our sliders control the correct morphs just like in the game!