/**
 * Ethernium Sovereign Web - GPU Custom GLSL Shaders (60 FPS BufferGeometry Physics & 2.3D Arcane Rim)
 * Module: /src/render/arcane_shaders.js
 */

export const EMBER_SHOCKWAVE_VERTEX_SHADER = /* glsl */ `
  uniform float uTime;
  uniform float uSpeed;
  uniform float uShockwave;

  attribute float aPhase;
  attribute float aRadius;
  attribute float aSpeed;
  attribute vec3 aColor;

  varying vec3 vColor;
  varying float vAlpha;

  void main() {
    vColor = aColor;
    float t = mod(uTime * uSpeed * aSpeed + aPhase, 6.2831853);
    float progress = t / 6.2831853;

    // Helical Bladewalker vortex + radial shockwave turbulence on GPU
    float angle = aPhase * 6.0 + uTime * uSpeed * (0.8 + 0.4 * sin(aPhase));
    float wave = sin(progress * 12.566 - uTime * 3.0) * 0.08 * uShockwave;
    float r = aRadius * (0.65 + 0.55 * sin(progress * 3.14159)) + wave;

    vec3 pos = vec3(
      cos(angle) * r,
      progress * 2.05 - 0.05 + 0.04 * cos(angle * 2.0),
      sin(angle) * r
    );

    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * mvPosition;

    float sizePulse = 1.0 + 0.45 * sin(uTime * 5.0 + aPhase * 10.0);
    gl_PointSize = clamp((26.0 * sizePulse) / -mvPosition.z, 1.5, 18.0);
    vAlpha = sin(progress * 3.1415926) * 0.88;
  }
`;

export const EMBER_SHOCKWAVE_FRAGMENT_SHADER = /* glsl */ `
  varying vec3 vColor;
  varying float vAlpha;

  void main() {
    vec2 uv = gl_PointCoord - vec2(0.5);
    float d = length(uv);
    if (d > 0.5) discard;
    float core = smoothstep(0.5, 0.05, d);
    gl_FragColor = vec4(vColor * (1.2 + core * 0.8), core * vAlpha);
  }
`;

export const PEDESTAL_RING_VERTEX_SHADER = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

export const PEDESTAL_RING_FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec3 uColorPrimary;
  uniform vec3 uColorSecondary;
  varying vec2 vUv;

  void main() {
    vec2 p = vUv * 2.0 - 1.0;
    float r = length(p);
    float ang = atan(p.y, p.x);

    float ring1 = smoothstep(0.035, 0.0, abs(r - 0.88));
    float ring2 = smoothstep(0.02, 0.0, abs(r - 0.72));
    float ticks = step(0.65, sin(ang * 24.0 + uTime * 1.5)) * smoothstep(0.04, 0.0, abs(r - 0.80));
    float pulse = smoothstep(0.06, 0.0, abs(r - mod(uTime * 0.35, 0.95))) * (1.0 - r);

    vec3 col = mix(uColorPrimary, uColorSecondary, 0.5 + 0.5 * sin(ang * 2.0 - uTime));
    float alpha = clamp(ring1 * 0.9 + ring2 * 0.6 + ticks * 0.75 + pulse * 0.5, 0.0, 1.0);
    gl_FragColor = vec4(col * 1.6, alpha);
  }
`;
