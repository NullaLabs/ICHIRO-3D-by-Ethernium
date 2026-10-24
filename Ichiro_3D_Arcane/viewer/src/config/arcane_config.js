/**
 * Ethernium Sovereign Web - Ichiro // 2390 Arcane 2.3D Configuration
 * Module: /src/config/arcane_config.js
 */
export const ARCANE_CONFIG = {
  character: {
    id: "KPR-2390",
    name: "ICHIRO (HYANGAKU-SHA)",
    title: "THE SILENT SENTINEL // BLADEWALKER",
    origin: "SOLIS",
    faction: "WANDERER",
    heightMeters: 1.810,
    widthMeters: 0.878,
    depthMeters: 0.365,
    quads: 46650,
    restDeltaMicrons: 0.12,
    companion: "LUMEN RECON DRONE // DUAL CRIMSON OPTICS",
    modelUrl: "./models/Ichiro_2390_Arcane_GameReady.glb",
  },
  modes: {
    standard: {
      label: "BLADEWALKER // STANDARD",
      keyColor: 0xffeedd,
      rimCyan: 0x00f0ff,
      rimMagenta: 0xff2a6d,
      magmaGlow: 0xff5500,
      bloomIntensity: 1.35,
      shockwaveSpeed: 1.2,
    },
    aberrant: {
      label: "KAI EXPOSURE // ABERRANT OVERDRIVE",
      keyColor: 0xd8b4ff,
      rimCyan: 0x9d00ff,
      rimMagenta: 0xff0055,
      magmaGlow: 0xff1166,
      bloomIntensity: 2.25,
      shockwaveSpeed: 2.6,
    },
    wireframe: {
      label: "MANIFOLD TOPOLOGY // WIREFRAME",
      keyColor: 0x88bbff,
      rimCyan: 0x00f0ff,
      rimMagenta: 0x00aaff,
      magmaGlow: 0x00f0ff,
      bloomIntensity: 1.0,
      shockwaveSpeed: 0.5,
    }
  },
  particles: {
    count: 2400,
    ringRadius: 0.72,
    maxHeight: 2.1,
  },
  cameras: {
    hero34:    { pos: [0.82, 0.96, 2.75], target: [0.0, 0.90, 0.0], fov: 38 },
    portrait:  { pos: [0.12, 1.58, 0.82], target: [0.0, 1.58, 0.0], fov: 28 },
    frontOrtho:{ pos: [0.00, 0.92, 2.90], target: [0.0, 0.90, 0.0], fov: 35 },
    sideOrtho: { pos: [-2.90, 0.92, 0.00], target: [0.0, 0.90, 0.0], fov: 35 },
    backOrtho: { pos: [0.00, 0.92, -2.90], target: [0.0, 0.90, 0.0], fov: 35 },
  },
};
