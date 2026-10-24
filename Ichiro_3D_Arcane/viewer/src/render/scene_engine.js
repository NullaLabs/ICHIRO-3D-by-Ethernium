/**
 * Ethernium Sovereign Web - 3D Scene & GPU BufferGeometry Particle Engine
 * Module: /src/render/scene_engine.js
 */
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { ARCANE_CONFIG } from "../config/arcane_config.js";
import {
  EMBER_SHOCKWAVE_VERTEX_SHADER,
  EMBER_SHOCKWAVE_FRAGMENT_SHADER,
  PEDESTAL_RING_VERTEX_SHADER,
  PEDESTAL_RING_FRAGMENT_SHADER,
} from "./arcane_shaders.js";

export class ArcaneSceneEngine {
  constructor(canvas, onTelemetryUpdate) {
    this.canvas = canvas;
    this.onTelemetryUpdate = onTelemetryUpdate;
    this.clock = new THREE.Clock();
    this.currentMode = "standard";
    this.autoRotate = false;
    this.shockwavePulse = 1.0;
    this.frameCount = 0;
    this.fpsAccum = 0;
    this.currentFps = 60;

    this._initRenderer();
    this._initSceneAndLights();
    this._initGpuParticles();
    this._initPedestalHoloRing();
    this._loadIchiroModel();
  }

  _initRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      powerPreference: "high-performance",
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.18;

    this.camera = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 0.05, 50);
    const hero = ARCANE_CONFIG.cameras.hero34;
    this.camera.position.set(...hero.pos);

    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.target.set(...hero.target);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.maxDistance = 8.0;
    this.controls.minDistance = 0.45;

    window.addEventListener("resize", () => {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    });
  }

  _initSceneAndLights() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x07090e);
    this.scene.fog = new THREE.FogExp2(0x07090e, 0.09);

    const mode = ARCANE_CONFIG.modes.standard;
    this.ambientLight = new THREE.AmbientLight(0x283044, 1.4);
    this.scene.add(this.ambientLight);

    this.keyLight = new THREE.DirectionalLight(mode.keyColor, 2.4);
    this.keyLight.position.set(1.5, 2.5, 2.8);
    this.scene.add(this.keyLight);

    this.rimCyan = new THREE.PointLight(mode.rimCyan, 5.5, 6.0);
    this.rimCyan.position.set(-1.8, 1.6, -1.2);
    this.scene.add(this.rimCyan);

    this.rimMagenta = new THREE.PointLight(mode.rimMagenta, 5.0, 6.0);
    this.rimMagenta.position.set(1.8, 1.5, -1.2);
    this.scene.add(this.rimMagenta);

    this.magmaLight = new THREE.PointLight(mode.magmaGlow, 3.8, 4.0);
    this.magmaLight.position.set(0.0, 0.65, 1.2);
    this.scene.add(this.magmaLight);
  }

  _initGpuParticles() {
    const count = ARCANE_CONFIG.particles.count;
    const geom = new THREE.BufferGeometry();

    const positions = new Float32Array(count * 3);
    const phases = new Float32Array(count);
    const radii = new Float32Array(count);
    const speeds = new Float32Array(count);
    const colors = new Float32Array(count * 3);

    const palette = [
      new THREE.Color(0xff5500), // Magma Blade Orange
      new THREE.Color(0x00f0ff), // Zaun Cyan Rim
      new THREE.Color(0xff2a6d), // Arcane Neon Magenta
      new THREE.Color(0xffaa00), // Gold Circuit Ember
    ];

    for (let i = 0; i < count; i++) {
      positions[i * 3] = 0;
      positions[i * 3 + 1] = 0;
      positions[i * 3 + 2] = 0;
      phases[i] = Math.random() * Math.PI * 2;
      radii[i] = 0.42 + Math.random() * 0.85;
      speeds[i] = 0.45 + Math.random() * 0.95;

      const c = palette[i % palette.length];
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }

    geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geom.setAttribute("aPhase", new THREE.BufferAttribute(phases, 1));
    geom.setAttribute("aRadius", new THREE.BufferAttribute(radii, 1));
    geom.setAttribute("aSpeed", new THREE.BufferAttribute(speeds, 1));
    geom.setAttribute("aColor", new THREE.BufferAttribute(colors, 3));

    this.particleUniforms = {
      uTime: { value: 0 },
      uSpeed: { value: ARCANE_CONFIG.modes.standard.shockwaveSpeed },
      uShockwave: { value: 1.0 },
    };

    const mat = new THREE.ShaderMaterial({
      vertexShader: EMBER_SHOCKWAVE_VERTEX_SHADER,
      fragmentShader: EMBER_SHOCKWAVE_FRAGMENT_SHADER,
      uniforms: this.particleUniforms,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    this.particles = new THREE.Points(geom, mat);
    this.scene.add(this.particles);
  }

  _initPedestalHoloRing() {
    const geom = new THREE.PlaneGeometry(1.75, 1.75);
    geom.rotateX(-Math.PI / 2);
    this.ringUniforms = {
      uTime: { value: 0 },
      uColorPrimary: { value: new THREE.Color(0x00f0ff) },
      uColorSecondary: { value: new THREE.Color(0xff5500) },
    };
    const mat = new THREE.ShaderMaterial({
      vertexShader: PEDESTAL_RING_VERTEX_SHADER,
      fragmentShader: PEDESTAL_RING_FRAGMENT_SHADER,
      uniforms: this.ringUniforms,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(geom, mat);
    mesh.position.y = 0.004;
    this.scene.add(mesh);
  }

  _loadIchiroModel() {
    const loader = new GLTFLoader();
    loader.load(
      ARCANE_CONFIG.character.modelUrl,
      (gltf) => {
        this.characterRoot = gltf.scene;
        this.lumenParts = [];
        let totalVerts = 0;
        let totalFaces = 0;
        this.characterRoot.traverse((child) => {
          if (child.name && child.name.startsWith("Lumen_")) {
            this.lumenParts.push(child);
          }
          if (child.isMesh && child.geometry) {
            const pos = child.geometry.attributes.position;
            if (pos) totalVerts += pos.count;
            if (child.geometry.index) totalFaces += child.geometry.index.count / 3;
          }
        });
        this.scene.add(this.characterRoot);
        if (this.onTelemetryUpdate) {
          this.onTelemetryUpdate({
            loaded: true,
            vertices: totalVerts,
            polygons: Math.round(totalFaces),
            lumenActive: this.lumenParts.length > 0,
          });
        }
      },
      undefined,
      (err) => {
        console.warn("GLB load notice:", err);
      }
    );
  }

  toggleLumen(visible) {
    if (!this.lumenParts) return;
    this.lumenParts.forEach((part) => {
      part.visible = visible;
    });
  }

  setMode(modeKey) {
    const cfg = ARCANE_CONFIG.modes[modeKey];
    if (!cfg) return;
    this.currentMode = modeKey;
    this.keyLight.color.setHex(cfg.keyColor);
    this.rimCyan.color.setHex(cfg.rimCyan);
    this.rimMagenta.color.setHex(cfg.rimMagenta);
    this.magmaLight.color.setHex(cfg.magmaGlow);
    this.particleUniforms.uSpeed.value = cfg.shockwaveSpeed;
    this.ringUniforms.uColorPrimary.value.setHex(cfg.rimCyan);
    this.ringUniforms.uColorSecondary.value.setHex(cfg.magmaGlow);
  }

  setCameraPreset(presetName) {
    const p = ARCANE_CONFIG.cameras[presetName];
    if (!p) return;
    this.camera.position.set(...p.pos);
    this.camera.fov = p.fov;
    this.camera.updateProjectionMatrix();
    this.controls.target.set(...p.target);
    this.controls.update();
  }

  triggerShockwave() {
    this.shockwavePulse = 3.5;
  }

  start() {
    const loop = () => {
      requestAnimationFrame(loop);
      const dt = this.clock.getDelta();
      const elapsed = this.clock.getElapsedTime();

      this.frameCount++;
      this.fpsAccum += dt;
      if (this.fpsAccum >= 0.5) {
        this.currentFps = Math.min(60, Math.round(this.frameCount / this.fpsAccum));
        this.frameCount = 0;
        this.fpsAccum = 0;
        if (this.onTelemetryUpdate) {
          this.onTelemetryUpdate({ fps: this.currentFps });
        }
      }

      this.shockwavePulse += (1.0 - this.shockwavePulse) * 0.06;
      this.particleUniforms.uTime.value = elapsed;
      this.particleUniforms.uShockwave.value = this.shockwavePulse;
      this.ringUniforms.uTime.value = elapsed;

      if (this.lumenParts && this.lumenParts.length > 0) {
        const hoverOffset = Math.sin(elapsed * 2.4) * 0.022;
        for (const part of this.lumenParts) {
          if (part._baseY === undefined) part._baseY = part.position.y;
          part.position.y = part._baseY + hoverOffset;
          if (part.name === "Lumen_Orbital_Ring") {
            part.rotation.z += dt * 1.6;
          }
        }
      }

      if (this.autoRotate && this.characterRoot) {
        this.characterRoot.rotation.y += dt * 0.55;
      }

      this.controls.update();
      this.renderer.render(this.scene, this.camera);
    };
    loop();
  }
}
