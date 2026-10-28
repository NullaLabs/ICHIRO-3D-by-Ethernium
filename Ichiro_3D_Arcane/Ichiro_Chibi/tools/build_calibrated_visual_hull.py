"""Build an aspect-preserving, Z-up visual-hull blockout from four references.

The OBJ is a coarse silhouette candidate, never the finished sculpt or a rig
mesh. Outputs are isolated under exports/visual_hull_v02 by default.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references"
DEFAULT_OUT = ROOT / "exports" / "visual_hull_v02"
GRID_X, GRID_HEIGHT, GRID_DEPTH = 80, 120, 80
TARGET_HEIGHT_M = 1.0
MASK_THRESHOLD = 24

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
    mask = (d > MASK_THRESHOLD).astype(np.uint8) * 255
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
                    ny,nx=yy+dy,xx+dx
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

def load_masks(out):
    result={}; report={}
    for name,path in VIEWS.items():
        img=Image.open(path)
        raw,bg=background_mask(img)
        mask=fill_enclosed_holes(largest_component(raw))
        ys,xs=np.where(mask)
        bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
        result[name]=(mask,bbox,img.size)
        debug=Image.fromarray((mask*255).astype(np.uint8))
        debug.save(out / f"mask_{name}.png")
        report[name]={"image_size":list(img.size),"background_rgb":[round(float(x),1) for x in bg],"bbox_xyxy":bbox}
    return result,report

def resample_crop(mask,bbox,grid_w,grid_h):
    """Fit silhouette to a shared canvas without changing its aspect ratio."""
    x0,y0,x1,y1=bbox
    crop=Image.fromarray((mask[y0:y1,x0:x1]*255).astype(np.uint8))
    scale=min(grid_w/(x1-x0),grid_h/(y1-y0))
    out_w=max(1,round((x1-x0)*scale))
    out_h=max(1,round((y1-y0)*scale))
    fitted=crop.resize((out_w,out_h),Image.Resampling.NEAREST)
    canvas=Image.new("L",(grid_w,grid_h),0)
    canvas.paste(fitted,((grid_w-out_w)//2,(grid_h-out_h)//2))
    return np.asarray(canvas)>0

def write_voxel_surface(occ, path, unit):
    """Write exposed faces in Blender coordinates: X width, Y depth, Z up."""
    nz, ny, nx = occ.shape
    vertices=[]; faces=[]; vmap={}
    def vertex(c):
        if c not in vmap:
            vmap[c]=len(vertices)+1
            # Source scene convention: Ichiro faces +X; width is Y; Z is up.
            # Map (image_x, image_y, profile_depth) -> (front_depth, width, up).
            vertices.append((-(c[2]-nz/2)*unit,
                             (c[0]-nx/2)*unit,
                             (ny/2-c[1])*unit))
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
            faces.append(list(reversed([vertex((x+a,y+b,z+c)) for a,b,c in quad])))
    with path.open("w",encoding="utf8") as f:
        f.write("# Ichiro Chibi calibrated visual hull — locked source\n")
        for x,y,z in vertices: f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
        for q in faces: f.write("f " + " ".join(map(str,q)) + "\n")
    edge_uses={}
    adjacency=[set() for _ in vertices]
    degenerate_faces=0
    signed_volume=0.0
    for face in faces:
        points=[np.asarray(vertices[i-1],dtype=np.float64) for i in face]
        area=(np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))+
              np.linalg.norm(np.cross(points[2]-points[0],points[3]-points[0])))*0.5
        if not math.isfinite(float(area)) or area<=1e-14:
            degenerate_faces+=1
        signed_volume+=float(np.dot(points[0],np.cross(points[1],points[2]))+
                             np.dot(points[0],np.cross(points[2],points[3])))/6.0
        for a,b in zip(face,face[1:]+face[:1]):
            edge=tuple(sorted((a,b)))
            edge_uses[edge]=edge_uses.get(edge,0)+1
            adjacency[a-1].add(b-1); adjacency[b-1].add(a-1)
    seen=set(); components=0
    for start in range(len(vertices)):
        if start in seen: continue
        components+=1; seen.add(start); stack=[start]
        while stack:
            current=stack.pop()
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor); stack.append(neighbor)
    edge_counts=list(edge_uses.values())
    audit={
        "unique_edges":len(edge_uses),
        "boundary_edges":sum(count==1 for count in edge_counts),
        "non_manifold_edges":sum(count>2 for count in edge_counts),
        "loose_vertices":sum(not neighbors for neighbors in adjacency),
        "degenerate_faces":degenerate_faces,
        "connected_components":components,
        "signed_volume_m3":signed_volume,
        "edge_watertight":bool(edge_counts) and all(count==2 for count in edge_counts),
        "self_intersection_test":"not performed",
    }
    audit["blockout_gate"]="PASS" if (
        audit["edge_watertight"] and audit["non_manifold_edges"]==0 and
        audit["loose_vertices"]==0 and audit["degenerate_faces"]==0 and
        audit["connected_components"]==1 and audit["signed_volume_m3"]>0
    ) else "BLOCKED"
    return len(vertices),len(faces),audit

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=DEFAULT_OUT)
    parser.add_argument("--target-height-m",type=float,default=TARGET_HEIGHT_M)
    args=parser.parse_args()
    if not np.isfinite(args.target_height_m) or args.target_height_m<=0:
        parser.error("--target-height-m must be finite and positive")
    out=args.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    masks,report=load_masks(out)
    nx,ny,nz=GRID_X,GRID_HEIGHT,GRID_DEPTH
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
    obj_path=out/"Ichiro_Chibi_VisualHull_BLOCKOUT_V02.obj"
    voxel_size=args.target_height_m/ny
    vcount,fcount,mesh_audit=write_voxel_surface(occ,obj_path,unit=voxel_size)
    if mesh_audit["blockout_gate"]!="PASS":
        raise RuntimeError(f"visual hull geometry gate blocked: {mesh_audit}")
    report.update({
        "schema":"ethernium.visual_hull_report.v2",
        "grid_xyz":[nx,ny,nz],"occupied_voxels":int(occ.sum()),
        "vertices":vcount,"quad_faces":fcount,
        "mesh_audit":mesh_audit,
        "target_height_m":args.target_height_m,"voxel_size_m":voxel_size,
        "axes":{"X":"front/back depth; face toward +X","Y":"character width","Z":"character height"},
        "source_hashes_sha256":{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in VIEWS.items()},
        "method":"aspect-preserving silhouette intersection; four primary views; orthographic approximation",
        "limitations":["coarse voxel surface; not sculpt or rig topology","camera perspective and view registration are not solved","8-view turnaround and pipeline board remain review evidence, not geometric constraints"],
        "output_obj":obj_path.relative_to(ROOT).as_posix() if obj_path.is_relative_to(ROOT) else str(obj_path),
    })
    (out/"visual_hull_report_v02.json").write_text(json.dumps(report,indent=2),encoding="utf8")
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
