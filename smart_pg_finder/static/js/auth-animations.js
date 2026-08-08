// Animated Background & Floating Particles for Auth Pages
class AuthAnimations {
    constructor() {
        this.particles = [];
        this.mouse = { x: 0, y: 0 };
        this.init();
    }

    init() {
        this.createFloatingBackground();
        this.setupMouseFollower();
        this.createAnimatedGradient();
        this.animateGlassShine();
        this.setupParticleSystem();
        this.startAuthCardFloat();
    }

    createFloatingBackground() {
        const bg = document.querySelector('.min-vh-100');
        if (bg) {
            bg.style.position = 'relative';
            bg.style.overflow = 'hidden';
            this.addFloatingShapes(bg);
        }
    }

    addFloatingShapes(container) {
        for (let i = 0; i < 12; i++) {
            const shape = document.createElement('div');
            shape.className = 'floating-shape';
            shape.style.cssText = `
                position: absolute;
                width: ${Math.random() * 80 + 20}px;
                height: ${Math.random() * 80 + 20}px;
                background: radial-gradient(circle, rgba(0,210,255,0.1), transparent);
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: float ${10 + Math.random() * 10}s infinite linear;
                animation-delay: ${Math.random() * -10}s;
                filter: blur(1px);
                z-index: -1;
            `;
            shape.style.animationDuration = (8 + Math.random() * 8) + 's';
            container.appendChild(shape);
        }
    }

    setupMouseFollower() {
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX / window.innerWidth;
            this.mouse.y = e.clientY / window.innerHeight;
            this.updateMouseParallax();
        });
    }

    updateMouseParallax() {
        const cards = document.querySelectorAll('.auth-card-modern');
        cards.forEach((card, index) => {
            const speed = 0.03 + index * 0.01;
            const x = (this.mouse.x - 0.5) * speed * 20;
            const y = (this.mouse.y - 0.5) * speed * 20;
            card.style.transform = `translate(${x}px, ${y}px) rotateY(${(this.mouse.x - 0.5) * 5}deg) rotateX(${-(this.mouse.y - 0.5) * 5}deg)`;
        });
    }

    createAnimatedGradient() {
        const gradient = document.querySelector('.min-vh-100');
        if (gradient) {
            gradient.style.background = `
                radial-gradient(circle at 20% 80%, rgba(120,119,198,0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255,119,198,0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120,219,255,0.3) 0%, transparent 50%),
                linear-gradient(-45deg, #0b1121 0%, #1e293b 50%, #0f172a 100%);
            `;
            gradient.style.backgroundSize = '400% 400%';
            gradient.style.animation = 'gradientShift 15s ease infinite';
        }
    }

    animateGlassShine() {
        const cards = document.querySelectorAll('.auth-card-modern');
        cards.forEach((card, index) => {
            const shine = document.createElement('div');
            shine.className = 'glass-shine';
            shine.style.cssText = `
                position: absolute;
                top: -50%; left: -50%;
                width: 200%; height: 200%;
                background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
                transform: rotate(45deg);
                animation: shine ${4 + index}s infinite linear;
                pointer-events: none;
                z-index: 1;
            `;
            card.appendChild(shine);
        });
    }

    setupParticleSystem() {
        for (let i = 0; i < 50; i++) {
            this.particles.push({
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 3 + 1,
                opacity: Math.random() * 0.5 + 0.2
            });
        }
        this.animateParticles();
    }

    animateParticles() {
        const canvas = document.createElement('canvas');
        canvas.style.cssText = 'position: fixed; top: 0; left: 0; pointer-events: none; z-index: -2;';
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        document.body.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            this.particles.forEach(p => {
                p.x += p.vx + (this.mouse.x * 0.02);
                p.y += p.vy + (this.mouse.y * 0.02);
                
                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
                
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(0,210,255,${p.opacity})`;
                ctx.fill();
            });
            
            requestAnimationFrame(() => animate.call(this));
        }
        animate.call(this);
    }

    startAuthCardFloat() {
        const cards = document.querySelectorAll('.auth-card-modern');
        cards.forEach((card, index) => {
            card.style.animation = `float ${6 + index * 0.5}s ease-in-out infinite`;
        });
    }
}

// CSS Keyframes (injected)
const style = document.createElement('style');
style.textContent = `
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(2deg); }
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .floating-shape {
        animation: float 20s infinite linear;
    }
    
    [data-theme="light"] {
        --glass-shine: rgba(0,0,0,0.1);
    }
`;
document.head.appendChild(style);

// Init on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.min-vh-100')) {
        new AuthAnimations();
    }
});
