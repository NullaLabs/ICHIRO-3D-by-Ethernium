# ETHERNIUM SOVEREIGN // ICHIRO (KPR-2390) MODULAR TRUE 360 PIPELINE

Pipeline de producción 3D de alta fidelidad para **Ichiro (KPR-2390 // Bladewalker)** y el satélite de reconocimiento **Lumen Recon Drone** en Blender 5.2 LTS, siguiendo los estándares de Fortiche (*Arcane*) y Unreal Engine 5 MetaHuman.

---

## 🌟 Arquitectura de Capas No Destructiva (Colecciones de Blender 5.2)

La escena maestra (`blend/Ichiro_2390_Arcane_Master.blend`) está construida siguiendo una rigurosa jerarquía no destructiva por capas modulares:

1. **`00_STUDIO_LIGHTING`**:
   - Rig de iluminación de 4 puntos estilo estudio cinematográfico:
     - `Key_Warm_Piltover` (Área frontal-superior 350W, tinte cálido `1.0, 0.95, 0.88`).
     - `Rim_Zaun_Cyan` (Área de contra-luz lateral 400W, cian puro `0.0, 0.94, 1.0`).
     - `Rim_Arcane_Magenta` (Área de contra-luz opuesta 380W, magenta eléctrico `1.0, 0.20, 0.55`).
     - `Fill_Front_Neutral` (Luz de relleno difusa 200W, neutral suave).
   - Entorno de mundo `Arcane_World` con emisión de fondo AgX High Contrast.

2. **`01_REFERENCE_CANON`**:
   - Vistas ortográficas canónicas 2D del arte original de Ichiro (`references/full_top_row.png`, `bust_front.png`, `bust_back.png`, `bust_left.png`, `bust_right.png`).
   - `BASE_360_LOCKED`: Casco volumétrico original (109.202 vértices, 218.400 triángulos, 100% watertight, 0 bordes abiertos, 0 geometría no-manifold). Intocable, bloqueado contra transformaciones accidentales, visualizado como wireframe/fantasma para guiar la anatomía sin alteración destructiva.

3. **`02_SCULPT_CORRECTIONS` (Cuerpo Anatómico Base)**:
   - Malla de cuerpo cuadrilátera hermética (`Ichiro_2390_Character`, 15.814 quads, simetría X estricta).
   - Relieve físico anatómico esculpido directamente en la musculatura pectoral y abdominal.
   - **8 Blendshapes faciales estándar ARKit FACS / MetaHuman** (`EyeBlink_L/R`, `BrowDown_L/R`, `BrowInnerUp`, `JawOpen`, `MouthSmile_L/R`), calibradas con valor neutro `0.0` para verificación cinemática.
   - Modificador `Multiresolution` no destructivo (Nivel 1 Viewport / Nivel 2 Render) para micro-escultura sin alterar la retopología base.

4. **`03_COSTUME_MODULES` (Módulos de Vestimenta Separados)**:
   - `Ichiro_Jacket_Lapels_3D`: Chaqueta corta bolero con solapas abiertas y proyección UV subpixel de camuflaje.
   - `Ichiro_Cyber_Collar_3D` + `Ichiro_Collar_Clasp_Badge`: Gargantilla cibernética con hebilla de oro.
   - `Ichiro_Clavicle_Harness_3D`: Arnés clavicular de oro con dije chevron en el esternón.
   - `Ichiro_Back_Harness_3D` + `Ichiro_Dorsal_Buckle`: Arnés dorsal táctico en 'X' con hebilla central.
   - `Ichiro_Tactical_Belts_3D` + Hebillas metálicas dobles + `Ichiro_Hip_Pouch`: Cinturones cruzados conformados anatómicamente a la cintura ($cx=0, cy=0.008, rx=0.188, ry=0.114$), mapeados con textura táctica de correas y relieve de normales.
   - `Ichiro_Cargo_Pocket_L/R` + `Ichiro_Cargo_Flap_L/R`: Bolsillos utilitarios en los muslos integrados a ras del pantalón.
   - `Ichiro_Gauntlet_Cuff_L/R` + `Ichiro_Gauntlet_LED_L/R`: Brazaletes cibernéticos con ribetes LED carmesí.
   - `Ichiro_Sneaker_Pods_L/R` + `Ichiro_KPR_Emblem_L/R`: Cápsulas luminosas de media suela e insignias en talones.

5. **`04_HAIR_AND_ACCESSORIES`**:
   - `Ichiro_Hair_Bangs_3D`: Mechón asimétrico largo en la mejilla derecha con bisel facetado para reflejos de borde.
   - `Ichiro_Hair_Crest_3D`: Cresta superior peinada hacia atrás con volumen físico 3D.
   - `Ichiro_Forehead_Lock_3D`: Mechón flotante frontal sobre la frente.
   - `Ichiro_Earring_L`, `Ichiro_Earring_R`: Aretes dorados circulares en ambas orejas.
   - `Ichiro_Magma_Blade_L`, `Ichiro_Magma_Blade_R`: Katanas dobles auténticas de magma extraídas de `ENERGY BLADE.blend` (25.535 vértices, 6 materiales PBR, núcleos incandescentes con fuerza de emisión 3.4), en postura de guardia baja.
   - `Ichiro_Scabbard`: Vaina táctica dorsal montada diagonalmente en la espalda.
   - **Lumen Recon Drone**: Satélite compañero optimizado (15.440 vértices, casco de titanio anodizado satinado, ojos dobles carmesí con brillo AgX calibrado y anillo orbital exterior).

6. **`05_HIGH_POLY_DETAILS`**:
   - Shader procedural triplanar con registro por scanline (`Mat_Ichiro_Arcane_Triplanar`).
   - Atlas universal PBR 4K horneado (`Ichiro_Body_Albedo_4K.png`, `Ichiro_Body_Emission_4K.png`, `Ichiro_Body_Normal_4K.png`).
   - Doble etapa de normales tangentes y micro-relieve táctil con máscara de atenuación facial gaussiana para eliminar el grano en la piel del rostro.

---

## 🦾 Rig Cinemático de Producción (`blend/Ichiro_2390_Arcane_Rigged.blend`)

- **Estructura Ósea:** 31 huesos (19 deformantes `DEF-*` para la anatomía, 12 controladores `CTRL-*`).
- **Cinemática:** IK desacoplable con pole targets para brazos y piernas mediante propiedades custom (`ik_arms`, `ik_legs`).
- **Skinning Matemático:** Pesos espaciales por distancia a cápsula ósea con reparto normalizado. 0 vértices huérfanos.
- **Auditoría de Rest Pose:** `NEUTRAL_CHECK_OK max_delta = 1.23e-07 m` (0.12 micras de desviación, garantizando que el rig en reposo coincide al 100.000% con la silueta canónica).

---

## 📂 Estructura del Directorio

```
Ichiro_3D_Arcane/
├── blend/
│   ├── Ichiro_2390_Arcane_Master.blend     # Escena maestra modular con 6 capas organizadas
│   └── Ichiro_2390_Arcane_Rigged.blend     # Versión animable con rig de 31 huesos (FK/IK)
├── models/
│   ├── Ichiro_360_Locked_Base_Mesh.npz     # Casco volumétrico 360 bloqueado (109.202 verts)
│   ├── Ichiro_2390_Arcane.glb              # GLB modular optimizado para WebGL/Three.js
│   └── Ichiro_2390_Arcane_Rigged.glb       # GLB rigged con morph targets faciales ARKit
├── references/                             # Arte conceptual canónico 2D y 360
│   ├── full_top_row.png                    # Hoja canónica completa de vistas ortográficas
│   ├── bust_front.png, bust_back.png...    # Vistas de busto calibradas
│   └── view_front_rgba.png...              # Vistas segmentadas limpias
├── renders/                                # Renders de producción de alta fidelidad
│   ├── 01_Ichiro_Arcane_Hero_Beauty.png    # Render hero beauty cuerpo entero
│   ├── 02_Ichiro_Arcane_Portrait_CloseUp.png # Primer plano cinematográfico rostro y undercut
│   └── 03_Ichiro_Arcane_Turnaround_4Views.png # Hoja de turnaround 4 vistas con telemetría HUD
├── textures/                               # Atlas PBR 4K horneados y normales táctiles
│   ├── Ichiro_Body_Albedo_4K.png
│   ├── Ichiro_Body_Emission_4K.png
│   ├── Ichiro_Body_Normal_4K.png
│   └── ...
├── mcp/
│   ├── audit_ichiro_true360.py             # Auditoría de solo lectura para el volumen 360
│   ├── build_modular_true360_scene.py      # Generador de la escena modular no destructiva
│   ├── rig_ichiro_production.py            # Generador y verificador del rig cinemático
│   ├── blender_mcp_addon.py                # Add-on socket TCP para control remoto MCP
│   └── blender_mcp_server.py               # Servidor MCP stdio para agentes de IA
├── viewer/                                 # Visor Web3D interactivo Local-First (Three.js)
├── START_ICHIRO_VIEWER.bat                 # Lanzador del visor web (localhost:8080)
└── START_BLENDER_MCP.bat                   # Lanzador del daemon MCP de Blender 5.2
```

---

## 🚀 Comandos de Generación y Verificación

Para regenerar la escena maestra modular:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --factory-startup -b -P "Ichiro_3D_Arcane\mcp\build_modular_true360_scene.py"
```

Para aplicar y validar el rig cinemático:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --factory-startup -b "Ichiro_3D_Arcane\blend\Ichiro_2390_Arcane_Master.blend" --python "Ichiro_3D_Arcane\mcp\rig_ichiro_production.py"
```

Para lanzar el visor WebGL interactivo a 60 FPS:
```powershell
.\Ichiro_3D_Arcane\START_ICHIRO_VIEWER.bat
```
