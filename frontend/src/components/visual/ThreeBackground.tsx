import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export const ThreeBackground: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check user preference for reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion || !mountRef.current) return;

    const container = mountRef.current;
    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
    camera.position.z = 24;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    container.appendChild(renderer.domElement);

    // Subtle floating geometric nodes
    const group = new THREE.Group();
    scene.add(group);

    // Geometry 1: Soft Violet Icosahedron wireframe
    const geomIso = new THREE.IcosahedronGeometry(4.5, 1);
    const matIso = new THREE.MeshBasicMaterial({
      color: 0x7555D9,
      wireframe: true,
      transparent: true,
      opacity: 0.12,
    });
    const meshIso = new THREE.Mesh(geomIso, matIso);
    meshIso.position.set(10, 4, -4);
    group.add(meshIso);

    // Geometry 2: Cyan Dodecahedron wireframe
    const geomDod = new THREE.DodecahedronGeometry(3.5, 0);
    const matDod = new THREE.MeshBasicMaterial({
      color: 0x45BFD0,
      wireframe: true,
      transparent: true,
      opacity: 0.10,
    });
    const meshDod = new THREE.Mesh(geomDod, matDod);
    meshDod.position.set(-11, -5, -2);
    group.add(meshDod);

    // Geometry 3: Central subtle particle sphere (Knowledge constellation)
    const particleCount = 45;
    const particleGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 36;
      positions[i + 1] = (Math.random() - 0.5) * 24;
      positions[i + 2] = (Math.random() - 0.5) * 12;
    }
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMaterial = new THREE.PointsMaterial({
      color: 0x6242C5,
      size: 0.18,
      transparent: true,
      opacity: 0.25,
    });
    const particleSystem = new THREE.Points(particleGeometry, particleMaterial);
    group.add(particleSystem);

    // Parallax mouse movement
    let mouseX = 0;
    let mouseY = 0;
    const onMouseMove = (e: MouseEvent) => {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    window.addEventListener('mousemove', onMouseMove, { passive: true });

    // Handle resize
    const onResize = () => {
      if (!container) return;
      const w = container.clientWidth || window.innerWidth;
      const h = container.clientHeight || window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', onResize);

    // Animation Loop
    let animationId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      // Gentle continuous rotation
      meshIso.rotation.x = elapsed * 0.08;
      meshIso.rotation.y = elapsed * 0.1;

      meshDod.rotation.x = -elapsed * 0.06;
      meshDod.rotation.y = elapsed * 0.09;

      particleSystem.rotation.y = elapsed * 0.02;

      // Smooth mouse parallax interpolation
      camera.position.x += (mouseX * 1.5 - camera.position.x) * 0.04;
      camera.position.y += (-mouseY * 1.5 - camera.position.y) * 0.04;
      camera.lookAt(scene.position);

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('resize', onResize);
      if (container && renderer.domElement && container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      geomIso.dispose();
      matIso.dispose();
      geomDod.dispose();
      matDod.dispose();
      particleGeometry.dispose();
      particleMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="fixed inset-0 pointer-events-none z-0 overflow-hidden"
      aria-hidden="true"
      style={{ opacity: 0.85 }}
    />
  );
};

