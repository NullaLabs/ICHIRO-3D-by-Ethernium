/**
 * Ethernium Sovereign Web - Bootloader
 * Module: /src/boot/main.js
 */
import { ArcaneSceneEngine } from "../render/scene_engine.js";
import { HudController } from "../ui/hud_controller.js";
import { McpTelemetryClient } from "../api/mcp_telemetry.js";

window.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("arcane-viewport") || document.getElementById("arcane-canvas");
  const telemetry = new McpTelemetryClient();
  let hud = null;

  const engine = new ArcaneSceneEngine(canvas, (stats) => {
    if (hud) hud.updateStats(stats);
  });

  hud = new HudController(engine, telemetry);
  engine.start();
});
