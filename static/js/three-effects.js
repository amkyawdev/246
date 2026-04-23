/**
 * Burme AI - Three.js Button Effects
 * 3D interactive effects on buttons including tilt and particle effects
 */

(function() {
    'use strict';
    
    // Three.js button effects container
    const ThreeDButtons = [];
    let scene, camera, renderer;
    
    /**
     * Initialize Three.js scene for effects
     */
    function init() {
        // Check if Three.js is available
        if (typeof THREE === 'undefined') {
            console.warn('Three.js not loaded');
            return;
        }
        
        // Create scene
        scene = new THREE.Scene();
        
        // Create camera
        camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
        camera.position.z = 500;
        
        // Create renderer
        renderer = new THREE.WebGLRenderer({ 
            alpha: true, 
            antialias: true 
        });
        renderer.setSize(100, 100);
        renderer.setPixelRatio(window.devicePixelRatio);
        
        // Initialize button effects
        initButtonEffects();
        
        // Start animation loop
        animate();
    }
    
    /**
     * Initialize button effects
     */
    function initButtonEffects() {
        const buttons = document.querySelectorAll('.three-d-btn');
        
        buttons.forEach(function(button) {
            const effect = new Button3DEffect(button);
            ThreeDButtons.push(effect);
        });
    }
    
    /**
     * Button 3D Effect Class
     */
    class Button3DEffect {
        constructor(button) {
            this.button = button;
            this.targetRotationX = 0;
            this.targetRotationY = 0;
            this.currentRotationX = 0;
            this.currentRotationY = 0;
            this.mouseX = 0;
            this.mouseY = 0;
            this.bounding = null;
            this.particles = [];
            
            this.init();
        }
        
        init() {
            if (!this.button) return;
            
            // Get initial bounding box
            this.updateBounding();
            
            // Add event listeners
            this.button.addEventListener('mouseenter', this.onMouseEnter.bind(this));
            this.button.addEventListener('mousemove', this.onMouseMove.bind(this));
            this.button.addEventListener('mouseleave', this.onMouseLeave.bind(this));
            this.button.addEventListener('click', this.onClick.bind(this));
            
            // Initialize particles
            this.initParticles();
            
            // Set initial transform style
            this.button.style.transformStyle = 'preserve-3d';
            this.button.style.perspective = '1000px';
            this.button.style.transition = 'transform 0.1s ease-out';
        }
        
        updateBounding() {
            this.bounding = this.button.getBoundingClientRect();
        }
        
        onMouseEnter(e) {
            this.updateBounding();
            this.targetRotationX = 0;
            this.targetRotationY = 0;
        }
        
        onMouseMove(e) {
            if (!this.bounding) return;
            
            const rect = this.button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Calculate rotation based on mouse position
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            this.targetRotationX = ((y - centerY) / centerY) * 5;
            this.targetRotationY = ((centerX - x) / centerX) * 5;
        }
        
        onMouseLeave(e) {
            this.targetRotationX = 0;
            this.targetRotationY = 0;
        }
        
        onClick(e) {
            // Create particle burst effect
            this.createParticleBurst(e);
        }
        
        initParticles() {
            // Create particle system
            this.particleGeometry = new THREE.BufferGeometry();
            this.particleMaterial = new THREE.PointsMaterial({
                color: 0xE94560,
                size: 8,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending
            });
            
            // Initialize particle positions
            const positions = new Float32Array(30 * 3);
            for (let i = 0; i < 30 * 3; i += 3) {
                positions[i] = 0;
                positions[i + 1] = 0;
                positions[i + 2] = 0;
            }
            
            this.particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            this.particlePoints = new THREE.Points(this.particleGeometry, this.particleMaterial);
            
            // Store particle velocities
            this.particleVelocities = [];
            for (let i = 0; i < 30; i++) {
                this.particleVelocities.push({
                    x: (Math.random() - 0.5) * 10,
                    y: (Math.random() - 0.5) * 10,
                    z: (Math.random() - 0.5) * 10
                });
            }
            
            // Hide initially
            this.particlePoints.visible = false;
        }
        
        createParticleBurst(e) {
            if (!scene || !this.particlePoints) return;
            
            // Position particles at click point
            const rect = this.button.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = -(e.clientY - rect.top - rect.height / 2);
            
            const positions = this.particleGeometry.attributes.position.array;
            for (let i = 0; i < 30; i++) {
                positions[i * 3] = x;
                positions[i * 3 + 1] = y;
                positions[i * 3 + 2] = 0;
            }
            this.particleGeometry.attributes.position.needsUpdate = true;
            
            // Show particles
            this.particlePoints.visible = true;
            this.particleStartTime = Date.now();
            this.activeParticles = true;
        }
        
        update() {
            // Smooth interpolation for 3D tilt
            this.currentRotationX += (this.targetRotationX - this.currentRotationX) * 0.2;
            this.currentRotationY += (this.targetRotationY - this.currentRotationY) * 0.2;
            
            // Apply transform
            if (this.button) {
                const scale = 1 + Math.abs(this.currentRotationX) * 0.005 + Math.abs(this.currentRotationY) * 0.005;
                this.button.style.transform = `perspective(1000px) rotateX(${this.currentRotationX}deg) rotateY(${this.currentRotationY}deg) scale(${Math.min(scale, 1.05)})`;
            }
            
            // Update particles
            if (this.activeParticles && this.particlePoints) {
                const elapsed = (Date.now() - this.particleStartTime) / 1000;
                
                if (elapsed > 0.5) {
                    this.activeParticles = false;
                    this.particlePoints.visible = false;
                } else {
                    const positions = this.particleGeometry.attributes.position.array;
                    for (let i = 0; i < 30; i++) {
                        positions[i * 3] += this.particleVelocities[i].x;
                        positions[i * 3 + 1] += this.particleVelocities[i].y;
                        positions[i * 3 + 2] += this.particleVelocities[i].z;
                    }
                    this.particleGeometry.attributes.position.needsUpdate = true;
                }
            }
        }
    }
    
    /**
     * Animation loop
     */
    function animate() {
        requestAnimationFrame(animate);
        
        // Update all button effects
        ThreeDButtons.forEach(function(effect) {
            effect.update();
        });
        
        // Render
        if (renderer && scene && camera) {
            renderer.render(scene, camera);
        }
    }
    
    /**
     * Add new button effect
     */
    function addButtonEffect(button) {
        const effect = new Button3DEffect(button);
        ThreeDButtons.push(effect);
    }
    
    /**
     * Wait for DOM and Three.js
     */
    function waitForThree() {
        if (typeof THREE !== 'undefined') {
            init();
        } else {
            setTimeout(waitForThree, 100);
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', waitForThree);
    } else {
        waitForThree();
    }
    
    // Export for global use
    window.BurmeAI = window.BurmeAI || {};
    window.BurmeAI.addButtonEffect = addButtonEffect;
    
})();