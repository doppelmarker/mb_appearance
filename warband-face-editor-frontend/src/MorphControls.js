import { FaceCodeParser } from './FaceCodeParser.js';

export class MorphControls {
    constructor(faceViewer) {
        this.faceViewer = faceViewer;
        this.morphValues = new Array(27).fill(0);
        this.container = this.createUI();
    }
    
    createUI() {
        const container = document.createElement('div');
        container.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.85);
            padding: 15px;
            color: white;
            font-family: 'Courier New', monospace;
            border-radius: 8px;
            width: 320px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        `;
        
        // Title
        const title = document.createElement('h3');
        title.textContent = 'Face Morphs';
        title.style.cssText = 'margin: 0 0 15px 0; font-size: 16px; text-align: center;';
        container.appendChild(title);
        
        // All 27 morph sliders as shown in the game
        const morphNames = [
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
        
        this.sliders = [];
        
        morphNames.forEach((name, index) => {
            const controlDiv = document.createElement('div');
            controlDiv.style.cssText = 'margin-bottom: 12px;';
            
            const label = document.createElement('div');
            label.style.cssText = 'font-size: 12px; margin-bottom: 4px; display: flex; justify-content: space-between;';
            
            const nameSpan = document.createElement('span');
            nameSpan.textContent = name;
            
            const valueSpan = document.createElement('span');
            valueSpan.id = `morph-value-${index}`;
            valueSpan.textContent = '0';
            valueSpan.style.color = '#4CAF50';
            
            label.appendChild(nameSpan);
            label.appendChild(valueSpan);
            
            const slider = document.createElement('input');
            slider.type = 'range';
            slider.min = 0;
            slider.max = 7;  // M&B uses 0-7 range
            slider.value = 0;
            slider.style.cssText = 'width: 100%; cursor: pointer;';
            
            slider.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                this.morphValues[index] = value;
                valueSpan.textContent = value;
                this.updateMorph(index, value / 7); // Normalize to 0-1
                this.updateFaceCode();
            });
            
            this.sliders.push(slider);
            
            controlDiv.appendChild(label);
            controlDiv.appendChild(slider);
            container.appendChild(controlDiv);
        });
        
        // Separator
        const separator = document.createElement('hr');
        separator.style.cssText = 'margin: 20px 0; border: none; border-top: 1px solid #444;';
        container.appendChild(separator);
        
        // Face code section
        this.addFaceCodeSection(container);
        
        // Skin tone section
        this.addSkinToneSection(container);
        
        document.body.appendChild(container);
        return container;
    }
    
    addFaceCodeSection(container) {
        const faceCodeDiv = document.createElement('div');
        
        const faceCodeLabel = document.createElement('div');
        faceCodeLabel.textContent = 'Face Code:';
        faceCodeLabel.style.cssText = 'font-size: 12px; margin-bottom: 8px; font-weight: bold;';
        
        this.faceCodeInput = document.createElement('textarea');
        this.faceCodeInput.placeholder = 'Paste face code here...';
        this.faceCodeInput.style.cssText = `
            width: 100%;
            height: 60px;
            margin: 5px 0;
            padding: 8px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            background: rgba(255,255,255,0.1);
            border: 1px solid #555;
            color: white;
            border-radius: 4px;
            resize: none;
        `;
        
        const buttonDiv = document.createElement('div');
        buttonDiv.style.cssText = 'display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;';
        
        const applyButton = document.createElement('button');
        applyButton.textContent = 'Apply Code';
        applyButton.style.cssText = `
            flex: 1;
            padding: 8px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
        `;
        applyButton.onmouseover = () => applyButton.style.background = '#45a049';
        applyButton.onmouseout = () => applyButton.style.background = '#4CAF50';
        
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy Code';
        copyButton.style.cssText = `
            flex: 1;
            padding: 8px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
        `;
        copyButton.onmouseover = () => copyButton.style.background = '#1976D2';
        copyButton.onmouseout = () => copyButton.style.background = '#2196F3';
        
        const randomizeButton = document.createElement('button');
        randomizeButton.textContent = 'Randomize';
        randomizeButton.style.cssText = `
            flex: 1;
            padding: 8px;
            background: #FF9800;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
        `;
        randomizeButton.onmouseover = () => randomizeButton.style.background = '#F57C00';
        randomizeButton.onmouseout = () => randomizeButton.style.background = '#FF9800';
        
        applyButton.onclick = () => {
            try {
                const code = this.faceCodeInput.value.trim();
                if (!code) return;
                
                const parsed = FaceCodeParser.parse(code);
                this.applyMorphs(parsed.morphs);
                this.showMessage('Face code applied!', 'success');
            } catch (error) {
                console.error('Invalid face code:', error);
                this.showMessage('Invalid face code!', 'error');
            }
        };
        
        copyButton.onclick = () => {
            this.faceCodeInput.select();
            document.execCommand('copy');
            this.showMessage('Copied to clipboard!', 'success');
        };
        
        randomizeButton.onclick = () => {
            this.randomizeFace();
            this.showMessage('Randomized face!', 'success');
        };
        
        // Test codes dropdown
        const testCodesDiv = document.createElement('div');
        testCodesDiv.style.cssText = 'margin-top: 10px;';
        
        const testLabel = document.createElement('label');
        testLabel.textContent = 'Test Codes: ';
        testLabel.style.cssText = 'font-size: 11px; margin-right: 5px;';
        
        const testSelect = document.createElement('select');
        testSelect.style.cssText = `
            padding: 4px;
            background: rgba(255,255,255,0.1);
            border: 1px solid #555;
            color: white;
            border-radius: 3px;
            font-size: 11px;
        `;
        
        const testCodes = [
            { name: 'Default', code: '0x00000000000000000000000000000000000000000000000000000000000000000' },
            { name: 'Strong Chin', code: '0x00000000000000001b00000000000000000000000000000000000000000000000' },
            { name: 'Long Nose', code: '0x000000000000000000db000000000000000000000000000000000000000000000' },
            { name: 'Wide Face', code: '0x00000000000000000000db6d00000000000000000000000000000000000000000' },
            { name: 'Mixed Features', code: '0x00000000000000001b6db6db6db6db6d000000000000000000000000000000000' }
        ];
        
        testCodes.forEach(test => {
            const option = document.createElement('option');
            option.value = test.code;
            option.textContent = test.name;
            testSelect.appendChild(option);
        });
        
        testSelect.onchange = (e) => {
            if (e.target.value) {
                this.faceCodeInput.value = e.target.value;
            }
        };
        
        testCodesDiv.appendChild(testLabel);
        testCodesDiv.appendChild(testSelect);
        
        faceCodeDiv.appendChild(faceCodeLabel);
        faceCodeDiv.appendChild(this.faceCodeInput);
        buttonDiv.appendChild(applyButton);
        buttonDiv.appendChild(copyButton);
        buttonDiv.appendChild(randomizeButton);
        faceCodeDiv.appendChild(buttonDiv);
        faceCodeDiv.appendChild(testCodesDiv);
        
        container.appendChild(faceCodeDiv);
    }
    
    addSkinToneSection(container) {
        // Separator
        const separator = document.createElement('hr');
        separator.style.cssText = 'margin: 20px 0; border: none; border-top: 1px solid #444;';
        container.appendChild(separator);
        
        const skinDiv = document.createElement('div');
        
        const skinLabel = document.createElement('div');
        skinLabel.textContent = 'Skin Type:';
        skinLabel.style.cssText = 'font-size: 12px; margin-bottom: 10px; font-weight: bold;';
        
        // Create dropdown for skin selection
        const skinSelect = document.createElement('select');
        skinSelect.style.cssText = `
            width: 100%;
            padding: 8px;
            background: rgba(255,255,255,0.1);
            border: 1px solid #555;
            color: white;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            margin-bottom: 10px;
        `;
        
        // Add styles for option elements and scrollbar
        const optionStyle = document.createElement('style');
        optionStyle.textContent = `
            select option {
                background-color: #333;
                color: white;
                padding: 5px;
            }
            select option:hover {
                background-color: #555;
            }
            /* Custom scrollbar for the controls */
            .morph-controls::-webkit-scrollbar {
                width: 8px;
            }
            .morph-controls::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
            .morph-controls::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
            .morph-controls::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        `;
        document.head.appendChild(optionStyle);
        
        // Add class for styling
        container.className = 'morph-controls';
        
        // Define skin options based on gender
        const skinOptions = {
            male: [
                { name: 'Young', value: 'young' },
                { name: 'Young Tan', value: 'young2' },
                { name: 'Young Dark', value: 'young3' },
                { name: 'Warrior', value: 'warrior' },
                { name: 'Middle Aged', value: 'midage' },
                { name: 'Weathered', value: 'midage2' },
                { name: 'Rugged', value: 'rugged' },
                { name: 'African', value: 'african' }
            ],
            female: [
                { name: 'Young', value: 'young' },
                { name: 'Pretty', value: 'pretty' },
                { name: 'Mature', value: 'mature' },
                { name: 'Brown', value: 'brown' },
                { name: 'African', value: 'african' }
            ]
        };
        
        // Function to update dropdown options based on gender
        this.updateSkinOptions = (gender) => {
            skinSelect.innerHTML = '';
            const options = skinOptions[gender] || skinOptions.male;
            
            options.forEach(option => {
                const opt = document.createElement('option');
                opt.value = option.value;
                opt.textContent = option.name;
                skinSelect.appendChild(opt);
            });
            
            // Set to current skin tone if available
            if (this.faceViewer.currentSkinTone && 
                options.some(opt => opt.value === this.faceViewer.currentSkinTone)) {
                skinSelect.value = this.faceViewer.currentSkinTone;
            } else {
                // Default to first option
                skinSelect.value = options[0].value;
                this.faceViewer.setSkinTone(options[0].value);
            }
        };
        
        // Initial population
        this.updateSkinOptions(this.faceViewer.currentGender);
        
        skinSelect.onchange = (e) => {
            this.faceViewer.setSkinTone(e.target.value);
            const selectedOption = skinSelect.options[skinSelect.selectedIndex];
            this.showMessage(`Skin type: ${selectedOption.textContent}`, 'info');
        };
        
        skinDiv.appendChild(skinLabel);
        skinDiv.appendChild(skinSelect);
        container.appendChild(skinDiv);
        
        // Store reference for gender switching
        this.skinSelect = skinSelect;
    }
    
    updateMorph(index, value) {
        // Use the new applyMorphValue method that handles mapping
        this.faceViewer.applyMorphValue(index, value);
    }
    
    applyMorphs(morphValues) {
        morphValues.forEach((value, index) => {
            if (index < 27) {
                this.morphValues[index] = value;
                this.sliders[index].value = value;
                document.getElementById(`morph-value-${index}`).textContent = value;
                this.updateMorph(index, value / 7);
            }
        });
        this.updateFaceCode();
    }
    
    updateFaceCode() {
        const code = FaceCodeParser.generate(this.morphValues);
        this.faceCodeInput.value = code;
    }
    
    randomizeFace() {
        // Generate random values for all 27 morphs
        const randomMorphs = [];
        for (let i = 0; i < 27; i++) {
            // Use different randomization strategies for different features
            let value;
            
            // For most features, use a bell curve distribution (more likely to get moderate values)
            if (i < 20) {
                // Generate two random numbers and average them for a more natural distribution
                const r1 = Math.random();
                const r2 = Math.random();
                value = Math.round((r1 + r2) / 2 * 7);
            } else {
                // For jaw/chin features, use full range
                value = Math.floor(Math.random() * 8);
            }
            
            randomMorphs.push(value);
        }
        
        // Apply the random morphs
        this.applyMorphs(randomMorphs);
    }
    
    showMessage(text, type = 'info') {
        const message = document.createElement('div');
        message.textContent = text;
        message.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
            color: white;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease-out;
        `;
        
        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-out';
            message.style.animationFillMode = 'forwards';
            setTimeout(() => message.remove(), 300);
        }, 2000);
    }
}