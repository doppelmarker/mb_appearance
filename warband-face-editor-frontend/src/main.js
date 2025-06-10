import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FaceViewer } from './FaceViewer.js';
import { MorphControls } from './MorphControls.js';

// Get canvas element
const canvas = document.getElementById('canvas');

// Basic Three.js setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2a2a2a);

// Camera setup
const camera = new THREE.PerspectiveCamera(
    45, 
    window.innerWidth / window.innerHeight, 
    0.1, 
    1000
);
camera.position.set(0, 0, 2); // Position camera at good distance for face view

// Renderer setup
const renderer = new THREE.WebGLRenderer({ 
    canvas: canvas,
    antialias: true 
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.outputColorSpace = THREE.SRGBColorSpace;

// Lighting setup
const ambientLight = new THREE.AmbientLight(0x606060, 1.5); // Moderate ambient light
scene.add(ambientLight);

// Main front light - strong light on the face (flipped to negative Z)
const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
directionalLight.position.set(0, 1, -4); // Now from behind camera to light the face
scene.add(directionalLight);

// Left fill light (flipped)
const fillLight = new THREE.DirectionalLight(0xaaaaff, 0.8);
fillLight.position.set(3, 0.5, -2); // From right-back to illuminate left face
scene.add(fillLight);

// Right fill light (flipped)
const fillLight2 = new THREE.DirectionalLight(0xffaaaa, 0.8);
fillLight2.position.set(-3, 0.5, -2); // From left-back to illuminate right face
scene.add(fillLight2);

// Reduced back light - now actually lighting the back (flipped)
const backLight = new THREE.DirectionalLight(0xffffff, 0.1);
backLight.position.set(0, 0, 8); // Now in front, very dim
scene.add(backLight);

// Camera controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.target.set(0, 0, 0); // Look at center

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Initialize face viewer
const faceViewer = new FaceViewer(scene);
let currentGender = 'male';

// Update info panel
function updateInfo(message) {
    document.getElementById('info').innerHTML = `
        <strong>M&B Face Editor MVP</strong><br>
        ${message}<br>
        <small>Mouse: Rotate | Scroll: Zoom</small>
    `;
}

// Gender switching functionality
function setupGenderControls() {
    const maleBtn = document.getElementById('male-btn');
    const femaleBtn = document.getElementById('female-btn');
    
    maleBtn.addEventListener('click', () => {
        if (currentGender !== 'male') {
            currentGender = 'male';
            maleBtn.classList.add('active');
            femaleBtn.classList.remove('active');
            updateInfo('Loading male head...');
            faceViewer.switchGender('male').then(() => {
                updateInfo('Male head loaded!');
                // Update skin dropdown for male options
                if (morphControls) {
                    morphControls.updateSkinOptions('male');
                }
            }).catch(() => {
                updateInfo('Error loading male head');
            });
        }
    });
    
    femaleBtn.addEventListener('click', () => {
        if (currentGender !== 'female') {
            currentGender = 'female';
            femaleBtn.classList.add('active');
            maleBtn.classList.remove('active');
            updateInfo('Loading female head...');
            faceViewer.switchGender('female').then(() => {
                updateInfo('Female head loaded!');
                // Update skin dropdown for female options
                if (morphControls) {
                    morphControls.updateSkinOptions('female');
                }
            }).catch(() => {
                updateInfo('Error loading female head');
            });
        }
    });
}

// Initialize the app
let morphControls = null; // Store reference to morph controls

async function init() {
    updateInfo('Loading face model...');
    
    try {
        // Setup gender controls first
        setupGenderControls();
        
        // Load textures first (they may not exist yet)
        await faceViewer.loadTextures();
        
        // Load default male head
        const success = await faceViewer.loadHead('male');
        
        if (success) {
            updateInfo('Male head loaded successfully!');
            // Apply default young skin tone
            faceViewer.setSkinTone('young');
        } else {
            updateInfo('Using fallback head model');
        }
        
        // Initialize morph controls after model is loaded
        morphControls = new MorphControls(faceViewer);
        
    } catch (error) {
        console.error('Initialization error:', error);
        updateInfo('Error loading model - check console');
    }
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// Start the app
init();
animate();