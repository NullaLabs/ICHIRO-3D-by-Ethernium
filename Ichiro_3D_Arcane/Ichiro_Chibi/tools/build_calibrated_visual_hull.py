"""Build a reproducible orthographic visual-hull source from Ichiro Chibi references.

Run with the Chibi venv Python.  Outputs only into E:/WORKSPACE/Ichiro_Chibi.
The OBJ is a locked source for Blender; it is not the finished sculpt.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(r"E:/WORKSPACE/Ichiro_Chibi")
REF = ROOT / "references"
OUT = ROOT / "exports" / "visual_hull"
OUT.mkdir(parents=True, exist_ok=True)

VIEWS = {
    "front": REF / "ichiro_chibi_front.png",
    "back": REF / "ichiro_chibi_back.png",
    "left": REF / "ichiro_chibi_left.png",
    "right": REF / "ichiro_chibi_right.png",
}

def background_mask(img):
    """Neutral studio background is inferred from four image corners."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    h, w, _ = a.shape
    n = max(12, min(h, w) // 12)
    corners = np.concatenate((a[:n,:n].reshape(-1,3), a[:n,-n:].reshape(-1,3),
                              a[-n:,:n].reshape(-1,3), a[-n:,-n:].reshape(-1,3)))
    bg = np.median(corners, axis=0)
    # Chibi palette differs strongly from the desaturated studio background.
    d = np.linalg.norm(a - bg, axis=2)
    mask = (d > 24).astype(np.uint8) * 255
    m = Image.fromarray(mask).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    return np.asarray(m) > 0, bg

def largest_component(mask):
    """Small dependency-free flood fill; removes isolated background artefacts."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    best = []
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if not mask[y,x] or seen[y,x]:
                continue
            stack=[(y,x)]; seen[y,x]=True; group=[]
            while stack:
                yy,xx=stack.pop(); group.append((yy,xx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=yy+dy,nx if False else xx+dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx]=True; stack.append((ny,nx))
            if len(group)>len(best): best=group
    out=np.zeros_like(mask)
    for y,x in best:
        out[max(0,y-1):min(h,y+2), max(0,x-1):min(w,x+2)] = True
    return out

def fill_enclosed_holes(mask):
    """Turn dark armour/shadow islands inside the silhouette into solid volume."""
    h,w=mask.shape
    exterior=np.zeros_like(mask,dtype=bool)
    stack=[]
    for x in range(w):
        if not mask[0,x]: stack.append((0,x))
        if not mask[h-1,x]: stack.append((h-1,x))
    for y in range(h):
        if not mask[y,0]: stack.append((y,0))
        if not mask[y,w-1]: stack.append((y,w-1))
    while stack:
        y,x=stack.pop()
        if not (0<=y<h and 0<=x<w) or mask[y,x] or exterior[y,x]: continue
        exterior[y,x]=True
        stack.extend(((y+1,x),(y-1,x),(y,x+1),(y,x-1)))
    return ~exterior

def load_masks():
    result={}; report={}
    for name,path in VIEWS.items():
        img=Image.open(path)
        raw,bg=background_mask(img)
        mask=fill_enclosed_holes(largest_component(raw))
        ys,xs=np.where(mask)
        bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
        result[name]=(mask,bbox,img.size)
        debug=Image.fromarray((mask*255).astype(np.uint8))
        debug.save(OUT / f"mask_{name}.png")
        report[name]={"image_size":list(img.size),"background_rgb":[round(float(x),1) for x in bg],"bbox_xyxy":bbox}
    return result,report

def resample_crop(mask,bbox,grid_w,grid_h):
    x0,y0,x1,y1=bbox
    crop=Image.fromarray((mask[y0:y1,x0:x1]*255).astype(np.uint8))
    # preserve comparable figure occupancy while each reference stays an anchor
    return np.asarray(crop.resize((grid_w,grid_h), Image.Resampling.NEAREST)) > 0

def write_voxel_surface(occ, path, unit=1.0):
    """Write only exposed voxel faces; deterministic portable OBJ source."""
    nz, ny, nx = occ.shape
    vertices=[]; faces=[]; vmap={}
    def vertex(c):
        if c not in vmap:
            vmap[c]=len(vertices)+1
            # Image rows grow downward; Blender's character up axis must grow upward.
            # The former formulation retained image-row direction and produced an
            # upside-down 360 volume during the front-view validation gate.
            vertices.append(((c[0]-nx/2)*unit,
                             (ny/2-c[1])*unit,
                             (c[2]-nz/2)*unit))
        return vmap[c]
    directions=[((-1,0,0),((0,0,0),(0,1,0),(0,1,1),(0,0,1))),
                ((1,0,0),((1,0,0),(1,0,1),(1,1,1),(1,1,0))),
                ((0,-1,0),((0,0,0),(0,0,1),(1,0,1),(1,0,0))),
                ((0,1,0),((0,1,0),(1,1,0),(1,1,1),(0,1,1))),
                ((0,0,-1),((0,0,0),(1,0,0),(1,1,0),(0,1,0))),
                ((0,0,1),((0,0,1),(0,1,1),(1,1,1),(1,0,1)))]
    for z,y,x in np.argwhere(occ):
        for (dx,dy,dz),quad in directions:
            xx,yy,zz=x+dx,y+dy,z+dz
            if 0<=xx<nx and 0<=yy<ny and 0<=zz<nz and occ[zz,yy,xx]: continue
            faces.append([vertex((x+a,y+b,z+c)) for a,b,c in quad])
    with path.open("w",encoding="utf8") as f:
        f.write("# Ichiro Chibi calibrated visual hull — locked source\n")
        for x,y,z in vertices: f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
        for q in faces: f.write("f " + " ".join(map(str,q)) + "\n")
    return len(vertices),len(faces)

def main():
    masks,report=load_masks()
    # 96 vertical slices, chibi proportions; x=width, y=height, z=depth.
    nx,ny,nz=80,120,80
    f=resample_crop(*masks["front"][:2],nx,ny)
    b=resample_crop(*masks["back"][:2],nx,ny)
    l=resample_crop(*masks["left"][:2],nz,ny)
    r=resample_crop(*masks["right"][:2],nz,ny)
    # Conservative support: front/back controls width per height, profiles control depth.
    width=np.logical_or(f,b)
    depth=np.logical_or(l,r)
    occ=np.zeros((nz,ny,nx),dtype=bool)
    for z in range(nz):
        occ[z]=width & depth[:,z][:,None]
    vcount,fcount=write_voxel_surface(occ,OUT/"Ichiro_Chibi_VisualHull_LOCKED.obj",unit=0.025)
    report.update({"grid_xyz":[nx,ny,nz],"occupied_voxels":int(occ.sum()),"vertices":vcount,"quad_faces":fcount,
                   "method":"orthographic silhouette intersection; all four primary views; 8-view and Kimi board retained as validation/process references"})
    (OUT/"visual_hull_report.json").write_text(json.dumps(report,indent=2),encoding="utf8")
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
