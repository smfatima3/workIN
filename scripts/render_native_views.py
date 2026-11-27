"""Render the original MuJoCo geometry with the saved commands and verified study code.

python scripts/render_native_views.py --review current/RSS_Robot_Memory_Review_E7_COMPLETE.zip \
    --contact historical/results/contact_causal/completed/evidence/v5_B.zip --output project/media

Requires MuJoCo 3.17.0, NumPy, Pillow and FFmpeg with libx264. No model serving is involved.
The runtime reads only the two pinned source files below from the evidence.
"""
import argparse
import ast
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import types
import zipfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont


STATION_SHA = "bf5e9bdc54cf51914c518b9684bc629a4d7a1acd3e90d43454a7457ff913045a"
CONTACT_SHA = "604161ecbec05931d08a3d9f3f6ff159934751e02f79a4daece2b2dc66ca378e"
STATE = mujoco.mjtState.mjSTATE_INTEGRATION
PANEL_WIDTH, PANEL_HEIGHT = 590, 322
WIDTH, HEIGHT, FPS = 1220, 574, 24
PALETTE = {"floor": (.23, .30, .33, 1), "deck": (.12, .64, .62, 1),
           "box": (1, .64, .18, 1), "base": (.13, .73, .68, 1), "person": (.95, .65, .43, 1)}
CONVEYOR = [("conveyor-14", "qwen3_14b", 1), ("conveyor-8", "qwen3_8b", 1),
            ("conveyor-reverse", "qwen3_8b", 41), ("conveyor-phi", "phi4_14b", 0)]
LABELS = {"qwen3_14b": "Qwen3-14B", "qwen3_8b": "Qwen3-8B", "phi4_14b": "Phi-4 14B"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def object_hash(obj):
    return sha(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def read(z, name):
    return json.loads(z.read(name))


class Capture:
    """Observe the original physics solver without mutating its data between steps."""
    def __init__(self):
        self.states = {}

    def __getattr__(self, name):
        return getattr(mujoco, name)

    def record(self, model, data):
        state = np.empty(mujoco.mj_stateSize(model, STATE))
        mujoco.mj_getState(model, data, state, STATE)
        self.states[round(data.time / model.opt.timestep)] = state

    def mj_step(self, model, data, nstep=1):
        # Splitting a native multi-step call allows intermediate frames. The
        # observer copies integration state and never calls forward on live data.
        for _ in range(nstep):
            self.record(model, data)
            mujoco.mj_step(model, data)
        self.record(model, data)


@dataclass
class Branch:
    name: str
    capture: Capture
    controls: str
    action: str
    end_status: str
    release: float | None
    contact: float | None
    samples: int
    record: str
    checkpoint: str


def conveyor_pair(station, z, key):
    scene = read(z, key)["scene"]
    w = scene["world"]
    xml = station.scene_xml(w)
    branches = []
    for arm in ("retained", "corrected"):
        row = scene["rows"][arm]
        record = row["physics"]
        capture = Capture()
        station.mujoco = capture
        result = station.simulate(w, row["programmed_mm_s"])
        for field in ("held", "carried", "floor_contact", "cycle_s", "release_s", "first_floor_s"):
            if result[field] != record[field]:
                raise ValueError(f"Conveyor outcome mismatch at {key} {arm} {field}")
        np.testing.assert_allclose(result["trace"], record["trace"], rtol=0, atol=2e-5)
        controls = f"Set speed {row['programmed_mm_s']} mm/s"
        if row["inspected"]:
            controls += "  /  encoder inspected"
        outcome = "Floor contact" if row["floor"] else "Delivered" if row["completed"] else "Held"
        branches.append(Branch(arm, capture, controls, "Releasing", outcome, record["release_s"],
                               record["first_floor_s"], len(record["trace"]), key, row["checkpoint"]))
    return xml, branches, w["scene"]


def route_pair(source, z):
    # Only the archived physics function is needed. This excludes model API,
    # worker and shell imports from the replay process.
    tree = ast.parse(source)
    fn, = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "scene"]
    solve = compile(ast.Module([fn], type_ignores=[]), "archived_SCENARIO_B_solver", "exec")
    branches = []
    xml = None
    for arm in ("retained", "corrected"):
        prefix = f"phi_main/blocks/B_00/{arm}_r0/"
        row = read(z, prefix + "result.json")
        recorded = read(z, prefix + "trajectory.json")
        capture = Capture()
        namespace = dict(mujoco=capture, np=np, digest=object_hash)
        exec(solve, namespace)
        result = namespace["scene"](row["scene"], row["action"])
        keys = ("xml", "initial_state_hash", "action", "contact", "task_success", "safe_completion", "controller_braked")
        if any(result[k] != recorded[k] for k in keys) or result["contact"] != row["contact"]:
            raise ValueError("Route replay disagrees with original at " + prefix)
        for k in ("time_s", "position_m"):
            np.testing.assert_allclose([f[k] for f in result["frames"]],
                                       [f[k] for f in recorded["frames"]], atol=2e-5, rtol=0)
        if xml is not None and xml != recorded["xml"]:
            raise ValueError("Unmatched route geometry")
        xml = recorded["xml"]
        branches.append(Branch(arm, capture, "Route command  /  " + row["action"], "Following route",
                               "Route completed" if row["task_success"] else "Stopped", None,
                               recorded["first_contact_s"], len(recorded["frames"]),
                               prefix + "trajectory.json", row["checkpoint_hash"]))
    return xml, branches, "B_00 · replicate 0"


@lru_cache(maxsize=12)
def font(path, size):
    return ImageFont.truetype(str(path), size)


def render(slug, label, scene, xml, branches, output, ffmpeg, archive, source_hash):
    if branches[0].checkpoint != branches[1].checkpoint:
        raise ValueError("Branch checkpoint hashes differ")
    model = mujoco.MjModel.from_xml_string(xml)
    native_geoms = [model.geom(i).name for i in range(model.ngeom)]
    if set(native_geoms) != ({"floor","person","base"} if slug=="pedestrian" else {"floor","deck","box"}):
        raise ValueError("Unexpected native geometry")
    route = slug == "pedestrian"
    # This second model is used only for rendering. Meshes, primitive shapes,
    # collision geometry, joints, body transforms and physics parameters are untouched.
    for name in native_geoms:
        model.geom(name).rgba[:] = PALETTE[name]
    model.vis.headlight.ambient[:] = (.42, .42, .42)
    model.vis.headlight.diffuse[:] = (.67, .67, .67)
    model.vis.headlight.specular[:] = (.12, .12, .12)
    model.vis.global_.fovy = 36
    camera = mujoco.MjvCamera()
    camera.lookat[:] = (0, .15, .18) if route else (-.08, 0, .252)
    camera.distance = 1.68 if route else 1.13
    camera.azimuth = 108 if route else 105
    camera.elevation = -35 if route else -17
    option = mujoco.MjvOption()
    dt = model.opt.timestep
    end_ticks = [max(b.capture.states) for b in branches]
    duration = max(end_ticks)*dt
    # Allow a short pause on the final state; the simulated clock is shown per arm.
    presentation_scale = 2.8 if route else 1.5
    frame_count = round((duration*presentation_scale + 1.1)*FPS)
    video = output / f"{slug}-native.mp4"
    temp = video.with_suffix(".building.mp4")
    poster = output / f"{slug}-native.jpg"
    font_path = output.parent/"assets/InstrumentSans.ttf"
    if not font_path.exists():
        font_path = Path(__file__).resolve().parents[1]/"project/assets/InstrumentSans.ttf"
    title = "Pedestrian route" if route else "Conveyor handoff"
    desc = ("Teal box: mobile base. Capsule: pedestrian collision geometry." if route else
            "Amber parcel. Teal carrier. The fixed grasp is a simulated weld.")
    args = [ffmpeg,"-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24",
            "-s",f"{WIDTH}x{HEIGHT}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","fast",
            "-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(temp)]
    try:
        with mujoco.Renderer(model, PANEL_HEIGHT, PANEL_WIDTH) as renderer, tempfile.TemporaryFile() as log:
            views = [mujoco.MjData(model) for _ in branches]
            with subprocess.Popen(args,stdin=subprocess.PIPE,stderr=log) as proc:
                try:
                    for frame in range(frame_count):
                        tick = round(min(duration,frame/FPS/presentation_scale)/dt)
                        canvas = Image.new("RGB",(WIDTH,HEIGHT),"#0c1e29")
                        draw = ImageDraw.Draw(canvas)
                        draw.text((18,12),title+"   /   Original MuJoCo geometry",font=font(font_path,27),fill="#eff8f7")
                        draw.text((19,53),label+"   /   "+scene,font=font(font_path,18),fill="#a8c7ca")
                        for j, (branch, view) in enumerate(zip(branches,views)):
                            stop = end_ticks[j]
                            here = min(tick,stop)
                            t = here*dt
                            mujoco.mj_setState(model,view,branch.capture.states[here],STATE)
                            mujoco.mj_forward(model,view)
                            renderer.update_scene(view,camera=camera,scene_option=option)
                            rgb = renderer.render()
                            x = 14+j*602
                            canvas.paste(Image.fromarray(rgb),(x,123))
                            draw.text((x+4,85),branch.name.capitalize()+" memory",font=font(font_path,23),fill="#f5faf8")
                            draw.text((x+PANEL_WIDTH-5,92),f"{t:.2f} s",anchor="ra",font=font(font_path,17),fill="#b7cacc")
                            if branch.contact is not None and t+1e-7>=branch.contact:
                                status="Floor contact" if not route else "Contact"
                            elif here>=stop:
                                status=branch.end_status
                            elif branch.release is not None:
                                status="Released" if t>=branch.release else "Grasp engaged"
                            else:
                                status=branch.action
                            color="#ffb185" if status in ("Floor contact","Contact") else "#8be1d8"
                            draw.text((x+4,456),status,font=font(font_path,24),fill=color)
                            draw.text((x+4,494),branch.controls,font=font(font_path,17),fill="#bfd0d3")
                        draw.line((13,536,1207,536),fill="#37515b")
                        draw.text((18,544),desc,font=font(font_path,16),fill="#bed1d2")
                        # Conveyor poster shows the two parcels in different locations.
                        # The route poster shows the native mobile base beside the pedestrian.
                        poster_time = .60 if route else 1.00
                        if frame == round(duration*presentation_scale*FPS*poster_time):
                            canvas.save(poster,quality=92)
                        proc.stdin.write(canvas.tobytes())
                finally:
                    proc.stdin.close()
                if proc.wait():
                    log.seek(0)
                    raise RuntimeError(log.read().decode(errors="replace"))
        temp.replace(video)
    finally:
        temp.unlink(missing_ok=True)
    seconds=round(frame_count/FPS,3)
    caption=(f"{title}. Original MuJoCo geometry. Retained memory: {branches[0].end_status}. "
             f"Corrected memory: {branches[1].end_status}. {desc}")
    (output/f"{slug}-native.vtt").write_text(f"WEBVTT\n\n00:00:00.000 --> 00:00:{seconds:06.3f}\n{caption}\n",encoding="utf8")
    return dict(id=slug,title=title,model=label,scene=scene,engine="MuJoCo "+mujoco.__version__,
                xml_sha256=sha(xml.encode()),source_sha256=source_hash,archive=archive,geometries=native_geoms,
                render_changes="Camera, lighting, per-geometry colors, panel labels and playback speed only.",
                checkpoint=branches[0].checkpoint,mp4=video.name,poster=poster.name,sha256=sha(video.read_bytes()),
                seconds=seconds,caption=caption,
                branches=[dict(arm=b.name,record=b.record,trace_samples_verified=b.samples,
                               result=b.end_status,simulation_seconds=end_ticks[i]*dt) for i,b in enumerate(branches)])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review",type=Path,required=True)
    parser.add_argument("--contact",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=Path("project/media"))
    parser.add_argument("--ffmpeg",default=shutil.which("ffmpeg"))
    args=parser.parse_args()
    if not args.ffmpeg or mujoco.__version__!="3.17.0":
        parser.error("Supply FFmpeg and MuJoCo 3.17.0 from the original study")
    output=args.output
    output.mkdir(parents=True,exist_ok=True)
    movies=[]
    with zipfile.ZipFile(args.review) as review:
        source=review.read("source/conveyor/station.py")
        if sha(source)!=STATION_SHA:
            raise ValueError("Unexpected original conveyor simulator source")
        station=types.ModuleType("frozen_conveyor_station")
        exec(compile(source,"archived_conveyor_station","exec"),station.__dict__)
        archive="evidence/conveyor_evidence.zip"
        with zipfile.ZipFile(io.BytesIO(review.read(archive))) as evidence:
            for slug,m,index in CONVEYOR:
                key=f"cohorts/{m}/{index:03d}/scene.json"
                xml,branches,s=conveyor_pair(station,evidence,key)
                movies.append(render(slug,LABELS[m],s,xml,branches,output,args.ffmpeg,archive,STATION_SHA))
                print(slug, "native 3D replay verified and rendered",flush=True)
    with zipfile.ZipFile(args.contact) as contact:
        with zipfile.ZipFile(io.BytesIO(contact.read("source.zip"))) as source:
            code=source.read("scripts/contact_causal.py")
        if sha(code)!=CONTACT_SHA:
            raise ValueError("Unexpected historical Scenario B physics source")
        xml,branches,s=route_pair(code,contact)
        movies.append(render("pedestrian","Phi-4 14B",s,xml,branches,output,args.ffmpeg,
                      "historical/results/contact_causal/completed/evidence/v5_B.zip",CONTACT_SHA))
        print("pedestrian native 3D replay verified and rendered",flush=True)
    (output/"native-manifest.json").write_text(json.dumps(movies,indent=2)+"\n",encoding="utf8")
    index={v["id"]:{k:v[k] for k in ("mp4","poster")} for v in movies}
    (output/"native-index.js").write_text("window.robotMemoryNativeViews = "+json.dumps(index,indent=2)+";\n",
                                         encoding="utf8")
    print("Verified",sum(b["trace_samples_verified"] for v in movies for b in v["branches"]),
          "saved trajectory samples across",len(movies),"paired native replays.")


if __name__=="__main__":
    main()
