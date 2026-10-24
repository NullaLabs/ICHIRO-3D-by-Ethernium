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
    document.querySelectorAll("[data-cam]").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("[data-cam]").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        this.engine.setCameraPreset(btn.getAttribute("data-cam"));
      });
    });

    document.querySelectorAll("[data-mode]").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("[data-mode]").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const mode = btn.getAttribute("data-mode");
        this.engine.setMode(mode);
        const badge = document.getElementById("hud-mode-label");
        if (badge) badge.textContent = ARCANE_CONFIG.modes[mode].label;
      });
    });

    const rotBtn = document.getElementById("btn-auto-rotate") || document.getElementById("btn-turntable");
    if (rotBtn) {
      rotBtn.addEventListener("click", () => {
        this.engine.autoRotate = !this.engine.autoRotate;
        rotBtn.classList.toggle("active", this.engine.autoRotate);
      });
    }

    const shockBtn = document.getElementById("btn-shockwave");
    if (shockBtn) {
      shockBtn.addEventListener("click", () => {
        this.engine.triggerShockwave();
      });
    }

    const lumenBtn = document.getElementById("btn-toggle-lumen");
    if (lumenBtn) {
      let lumenVisible = true;
      lumenBtn.addEventListener("click", () => {
        lumenVisible = !lumenVisible;
        this.engine.toggleLumen(lumenVisible);
        lumenBtn.classList.toggle("active", lumenVisible);
        const stat = document.getElementById("stat-lumen-status");
        if (stat) {
          stat.textContent = lumenVisible ? "ONLINE" : "STANDBY";
          stat.className = lumenVisible ? "stat-value text-cyan" : "stat-value text-dim";
        }
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
    if (stats.lumenActive !== undefined) {
      const el = document.getElementById("stat-lumen-status");
      if (el) {
        el.textContent = stats.lumenActive ? "ONLINE" : "STANDBY";
        el.className = stats.lumenActive ? "stat-value text-cyan" : "stat-value text-dim";
      }
    }
  }
}
