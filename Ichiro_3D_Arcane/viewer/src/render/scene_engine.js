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
    this.mixer = null;
    this.animations = {};
    this.activeAction = null;
    this.faceMesh = null;
    this.allMeshes = [];

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
    this.renderer.toneMappingExposure = 1.22;

    this.camera = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 0.05, 50);
    const hero = ARCANE_CONFIG.cameras.hero34;
    this.camera.position.set(...hero.pos);

    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.target.set(...hero.target);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.maxDistance = 8.0;
    this.controls.minDistance = 0.40;

    window.addEventListener("resize", () => {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    });
  }

  _initSceneAndLights() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x07090e);
    this.scene.fog = new THREE.FogExp2(0x07090e, 0.08);

    const mode = ARCANE_CONFIG.modes.standard;
    this.ambientLight = new THREE.AmbientLight(0x283044, 1.5);
    this.scene.add(this.ambientLight);

    this.keyLight = new THREE.DirectionalLight(mode.keyColor, 2.5);
    this.keyLight.position.set(1.5, 2.5, 2.8);
    this.scene.add(this.keyLight);

    this.rimCyan = new THREE.PointLight(mode.rimCyan, 5.8, 7.0);
    this.rimCyan.position.set(-1.8, 1.6, -1.2);
    this.scene.add(this.rimCyan);

    this.rimMagenta = new THREE.PointLight(mode.rimMagenta, 5.2, 7.0);
    this.rimMagenta.position.set(1.8, 1.5, -1.2);
    this.scene.add(this.rimMagenta);

    this.magmaLight = new THREE.PointLight(mode.magmaGlow, 4.2, 5.0);
    this.magmaLight.position.set(0.0, 0.70, 1.2);
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
      new THREE.Color(0xff4500),
      new THREE.Color(0xff9900),
      new THREE.Color(0x00f0ff),
      new THREE.Color(0xff2a6d),
    ];

    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const r = 0.15 + Math.random() * ARCANE_CONFIG.particles.ringRadius;
      radii[i] = r;
      positions[i * 3 + 0] = Math.cos(theta) * r;
      positions[i * 3 + 1] = Math.random() * ARCANE_CONFIG.particles.maxHeight;
      positions[i * 3 + 2] = Math.sin(theta) * r;
      phases[i] = Math.random() * Math.PI * 2;
      speeds[i] = 0.4 + Math.random() * 0.8;

      const c = palette[Math.floor(Math.random() * palette.length)];
      colors[i * 3 + 0] = c.r;
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
      uSpeed: { value: 1.0 },
      uPulse: { value: 1.0 },
      uMaxHeight: { value: ARCANE_CONFIG.particles.maxHeight },
    };

    const mat = new THREE.ShaderMaterial({
      vertexShader: EMBER_SHOCKWAVE_VERTEX_SHADER,
      fragmentShader: EMBER_SHOCKWAVE_FRAGMENT_SHADER,
      uniforms: this.particleUniforms,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    this.particleSystem = new THREE.Points(geom, mat);
    this.scene.add(this.particleSystem);
  }

  _initPedestalHoloRing() {
    const geom = new THREE.RingGeometry(0.55, 0.95, 64);
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
        this.allMeshes = [];
        let totalVerts = 0;
        let totalFaces = 0;

        // Setup Animation Mixer
        if (gltf.animations && gltf.animations.length > 0) {
          this.mixer = new THREE.AnimationMixer(this.characterRoot);
          gltf.animations.forEach((clip) => {
            this.animations[clip.name] = this.mixer.clipAction(clip);
          });
          // Play Idle by default
          if (this.animations["Anim_Idle_Breathing"]) {
            this.playAnimation("Anim_Idle_Breathing");
          }
        }

        this.characterRoot.traverse((child) => {
          if (child.isMesh && child.geometry) {
            this.allMeshes.push(child);
            const pos = child.geometry.attributes.position;
            if (pos) totalVerts += pos.count;
            if (child.geometry.index) totalFaces += child.geometry.index.count / 3;

            // Detect Face Mesh with Morph Targets
            if (child.morphTargetDictionary && child.morphTargetInfluences) {
              this.faceMesh = child;
              console.log("Found ARKit Face Mesh:", child.name, "with", Object.keys(child.morphTargetDictionary).length, "keys");
            }
          }
        });

        this.scene.add(this.characterRoot);

        if (this.onTelemetryUpdate) {
          this.onTelemetryUpdate({
            loaded: true,
            vertices: totalVerts,
            polygons: Math.round(totalFaces),
            morphCount: this.faceMesh ? Object.keys(this.faceMesh.morphTargetDictionary).length : 0,
            hasRig: !!this.mixer,
          });
        }
      },
      undefined,
      (err) => {
        console.warn("GLB load notice:", err);
      }
    );
  }

  playAnimation(name) {
    if (!this.mixer) return;
    if (name === "Rest_Pose") {
      if (this.activeAction) this.activeAction.stop();
      this.activeAction = null;
      return;
    }
    const action = this.animations[name];
    if (action) {
      if (this.activeAction && this.activeAction !== action) {
        this.activeAction.fadeOut(0.35);
      }
      action.reset().fadeIn(0.35).play();
      this.activeAction = action;
    }
  }

  setMorphWeight(keyName, weight) {
    if (!this.faceMesh || !this.faceMesh.morphTargetDictionary) return;
    const idx = this.faceMesh.morphTargetDictionary[keyName];
    if (idx !== undefined) {
      this.faceMesh.morphTargetInfluences[idx] = Math.max(0.0, Math.min(1.0, weight));
    }
  }

  setShadingMode(mode) {
    this.allMeshes.forEach((mesh) => {
      if (!mesh.material) return;
      if (mode === "wireframe") {
        mesh.material.wireframe = true;
      } else {
        mesh.material.wireframe = false;
      }
    });
  }

  setMode(modeKey) {
    const cfg = ARCANE_CONFIG.modes[modeKey];
    if (!cfg) return;
    this.currentMode = modeKey;
    if (modeKey === "wireframe") {
      this.setShadingMode("wireframe");
    } else {
      this.setShadingMode("pbr");
    }
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

      // Update Animation Mixer
      if (this.mixer) {
        this.mixer.update(dt);
      }

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

      this.shockwavePulse = Math.max(1.0, this.shockwavePulse - dt * 2.2);
      this.particleUniforms.uTime.value = elapsed;
      this.particleUniforms.uPulse.value = this.shockwavePulse;
      this.ringUniforms.uTime.value = elapsed;

      if (this.autoRotate) {
        this.characterRoot?.rotateY(dt * 0.45);
      }

      this.controls.update();
      this.renderer.render(this.scene, this.camera);
    };
    loop();
  }
}
