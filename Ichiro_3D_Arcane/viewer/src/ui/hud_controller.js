/**
 * Ethernium Sovereign Web - Cyberpunk/Glassmorphic HUD Controller
 * Module: /src/ui/hud_controller.js
 */
import { ARCANE_CONFIG } from "../config/arcane_config.js";

export class HudController {
  constructor(engine, telemetryClient) {
    this.engine = engine;
    this.telemetryClient = telemetryClient;
    this._bindControls();
  }

  _bindControls() {
    // Camera Presets
    document.querySelectorAll("[data-cam]").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("[data-cam]").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        this.engine.setCameraPreset(btn.getAttribute("data-cam"));
      });
    });

    // Shading / Visual Modes
    document.querySelectorAll("[data-mode]").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("[data-mode]").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const mode = btn.getAttribute("data-mode");
        this.engine.setMode(mode);
        const badge = document.getElementById("hud-mode-label");
        if (badge && ARCANE_CONFIG.modes[mode]) {
          badge.textContent = ARCANE_CONFIG.modes[mode].label;
        }
      });
    });

    // Turntable Auto-rotate
    const rotBtn = document.getElementById("btn-auto-rotate") || document.getElementById("btn-turntable");
    if (rotBtn) {
      rotBtn.addEventListener("click", () => {
        this.engine.autoRotate = !this.engine.autoRotate;
        rotBtn.classList.toggle("active", this.engine.autoRotate);
      });
    }

    // Shockwave FX
    const shockBtn = document.getElementById("btn-shockwave");
    if (shockBtn) {
      shockBtn.addEventListener("click", () => {
        this.engine.triggerShockwave();
      });
    }

    // Animation Pose Switcher
    document.querySelectorAll("[data-anim]").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("[data-anim]").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const animName = btn.getAttribute("data-anim");
        this.engine.playAnimation(animName);
      });
    });

    // ARKit 52 Morph Target Sliders
    const morphs = [
      { id: "slider-morph-smile", key: "mouthSmileRight" },
      { id: "slider-morph-blink", key: "eyeBlinkLeft", dual: "eyeBlinkRight" },
      { id: "slider-morph-jaw", key: "jawOpen" },
      { id: "slider-morph-brow", key: "browDownRight", dual: "browDownLeft" },
      { id: "slider-morph-pucker", key: "mouthPucker" }
    ];

    morphs.forEach(({ id, key, dual }) => {
      const slider = document.getElementById(id);
      if (slider) {
        slider.addEventListener("input", (e) => {
          const val = parseFloat(e.target.value);
          this.engine.setMorphWeight(key, val);
          if (dual) {
            this.engine.setMorphWeight(dual, val);
          }
          const valLabel = document.getElementById(`${id}-val`);
          if (valLabel) valLabel.textContent = val.toFixed(2);
        });
      }
    });

    // Reset Facial Expression
    const resetFacialBtn = document.getElementById("btn-reset-facial");
    if (resetFacialBtn) {
      resetFacialBtn.addEventListener("click", () => {
        morphs.forEach(({ id, key, dual }) => {
          this.engine.setMorphWeight(key, 0.0);
          if (dual) this.engine.setMorphWeight(dual, 0.0);
          const slider = document.getElementById(id);
          if (slider) slider.value = 0.0;
          const valLabel = document.getElementById(`${id}-val`);
          if (valLabel) valLabel.textContent = "0.00";
        });
      });
    }
  }

  updateStats(stats) {
    if (stats.fps !== undefined) {
      const el = document.getElementById("stat-fps");
      if (el) el.textContent = `${stats.fps} FPS`;
    }
    if (stats.vertices !== undefined) {
      const el = document.getElementById("stat-verts");
      if (el) el.textContent = stats.vertices.toLocaleString();
    }
    if (stats.polygons !== undefined) {
      const el = document.getElementById("stat-polys");
      if (el) el.textContent = stats.polygons.toLocaleString();
    }
    if (stats.morphCount !== undefined) {
      const el = document.getElementById("stat-morphs");
      if (el) el.textContent = `${stats.morphCount} ARKit Keys`;
    }
  }
}
