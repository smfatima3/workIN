"""Render illustrative pairs from saved model decisions and measured simulation traces.

python scripts/render_publication_replays.py review.zip --output project/media
Requires Pillow and FFmpeg with libx264. Never calls a model or chooses an action.
"""
import argparse
import bisect
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import zipfile
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W,H,FPS=1200,568,20
BG="#0c1e29"; PANEL="#132b38"; GRID="#23424f"; INK="#ecf7f8"; SOFT="#afc7ce"
WATER="#62dfdc"; DROP="#ffab78"; PARCEL="#f8c36e"; RAIL="#6c9da5"
TYPEFACE=Path(__file__).resolve().parents[1]/"project/assets/InstrumentSans.ttf"


@lru_cache(None)
def font(size,bold=False):
    f=ImageFont.truetype(str(TYPEFACE),size)
    if bold:
        try:
            axes=f.get_variation_axes()
            f.set_variation_by_axes([min(a["maximum"],700) if a["name"]==b"Weight" else a["default"] for a in axes])
        except (ValueError,OSError):
            pass
    return f


def text(d,x,y,s,size=18,color=INK,bold=False):
    d.text((x,y),str(s),font=font(size,bold),fill=color)


def read(z,n):
    return json.loads(z.read(n))


def file_hash(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()


def sample(rows,t):
    i=bisect.bisect_right([r[0] for r in rows],t)
    if i==0:return rows[0]
    if i>=len(rows):return rows[-1]
    a,b=rows[i-1],rows[i]
    f=(t-a[0])/(b[0]-a[0])
    return [t,*[v+(w-v)*f for v,w in zip(a[1:],b[1:])]]


def chart_frame(title,model,scene,t):
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    text(d,30,17,title,27,bold=True)
    text(d,30,55,model+"   /   "+scene,17,SOFT)
    d.text((W-30,32),f"{t:0.2f} s",anchor="ra",font=font(19),fill=SOFT)
    for j,label in enumerate(("Retained memory","Corrected memory")):
        x=20+590*j
        d.rounded_rectangle((x,94,x+568,545),radius=12,fill=PANEL,outline=GRID,width=2)
        text(d,x+23,114,label,25,bold=True)
        for i in range(1,9):
            xx=x+13+i*61
            d.line((xx,185,xx,423),fill=GRID)
        for yy in range(205,424,45):d.line((x+17,yy,x+551,yy),fill=GRID)
        d.line((x+20,445,x+548,445),fill=GRID,width=2)
    return im,d


def glass_frame(s,t):
    w=s["world"];im,d=chart_frame("Glass pouring","Qwen3-14B",w["id"],t)
    ports=w["ports_mm"];center=w["current"];mid=(min(ports)+max(ports))/2
    for j,arm in enumerate(("retained","corrected")):
        x=20+590*j;r=s["rows"][arm];p=r["physics"]
        elapsed=max(0,t-(2 if r["inspection"] else 0))
        _,sup,inside,caught,escaped=sample(p["trace"],t)
        gx=x+282+(center-mid)*6;half=w["rim_half_width_mm"]*6
        text(d,x+23,149,f"Saved glass center  {r['retrieved']['value']:+d} mm",18,SOFT)
        sel=0 if r["command"]=="pour_port_L" else 1
        for k,v in enumerate(ports):
            px=x+282+(v-mid)*6
            col=WATER if sel==k else RAIL
            d.rounded_rectangle((px-20,190,px+20,211),radius=4,fill=col)
            text(d,px-6,166,"L" if k==0 else "R",15,SOFT)
            if sel==k and 0<elapsed<=4:
                for dx in (-4,0,4):
                    d.line((px+dx,213,px+dx,374 if abs(v-center)>w["rim_half_width_mm"] else 350),
                           fill=WATER,width=2)
        top=252;bottom=373
        water_top=bottom-3-min(1,inside/w["capacity_ml"])*(bottom-top-3)
        if inside>0:d.rectangle((gx-half+5,water_top,gx+half-5,bottom-3),fill="#2c8796")
        d.line(((gx-half,top),(gx-half,bottom),(gx+half,bottom),(gx+half,top)),fill=INK,width=4)
        d.line(((gx-half-16,bottom+7),(gx-half-16,bottom+20),(gx+half+18,bottom+20),(gx+half+18,bottom+7)),fill=RAIL,width=4)
        if escaped>0:
            px=x+282+(ports[sel]-mid)*6
            span=min(50,8+escaped/4)
            d.ellipse((px-span,399,px+span,405),fill=DROP)
        text(d,x+22,412,f"Glass center  {center:+d} mm     /     Dispensed  {sup:.0f} mL",16,SOFT)
        text(d,x+23,459,f"{escaped:.0f} mL escaped",26,DROP if escaped>0 else WATER,True)
        text(d,x+24,501,f"Glass  {inside:.0f} mL     Catch tray  {caught:.0f} mL",17,SOFT)
    return im


def tray_frame(s,t):
    w=s["world"];im,d=chart_frame("Moving-tray placement","Qwen3-14B",w["id"],t)
    for j,arm in enumerate(("retained","corrected")):
        x=20+590*j;r=s["rows"][arm];p=r["physics"];log=p["trace"];tick=t*p["hz"]
        k=max(0,min(len(log)-1,bisect.bisect_right([row[0] for row in log],tick)-1))
        pose=sample([u[:7] for u in log],tick);_,px,py,x0,x1,b0,b1=pose
        text(d,x+23,149,f"Saved load on {r['retrieved']['bay']}  {r['retrieved']['supported_kg']:.2f} kg",18,SOFT)
        xx=lambda u:x+45+u*1.18
        yy=lambda v:163+v*.76
        for i,(cx,bx) in enumerate(((x0,b0),(x1,b1))):
            d.rounded_rectangle((xx(cx)-60,yy(245),xx(cx)+60,yy(245)+8),radius=3,fill=RAIL)
            d.rectangle((xx(bx)-9,yy(245)-13,xx(bx)+9,yy(245)-1),fill="#a6b7b9")
            text(d,xx(cx)-33,yy(245)+15,w["labels"][i],18,SOFT)
        d.rounded_rectangle((xx(px)-10,yy(py)-9,xx(px)+10,yy(py)+9),radius=2,fill=PARCEL)
        ended=tick>=p["settled_tick"];result=max(p["peak_settled"])
        status=f"Settled load  {result:.2f} kg" if ended else "Parcel in motion"
        text(d,x+23,459,status,26,(DROP if p["unsafe"] else WATER) if ended else INK,True)
        text(d,x+23,501,f"Command  {r['command']}     /     Rating  {w['capacity']:.1f} kg",17,SOFT)
    return im


def conveyor_frame(s,t):
    w=s["world"];names={"qwen3:14b":"Qwen3-14B","qwen3:8b":"Qwen3-8B","phi4:14b":"Phi-4 14B"}
    im,d=chart_frame("Conveyor handoff",names[s["model"]],w["scene"],t)
    rows=[s["rows"][a] for a in ("retained","corrected")]
    coords=[r[1] for a in rows for r in a["physics"]["trace"]]
    lo=min(-.54,min(coords)-.13);hi=max(.54,max(coords)+.13);scale=min(505/(hi-lo),245/.72)
    for j,r in enumerate(rows):
        x=20+590*j;p=r["physics"];_,cx,px,pz=sample(p["trace"],min(t,p["cycle_s"]))
        def point(u,v):return round(x+284+(u-(lo+hi)/2)*scale),round(416-v*scale)
        rec=r["retrieved"];txt=f"Saved speed  {rec['value']} mm/s" if rec else "No speed stored"
        text(d,x+23,149,txt,18,SOFT)
        d.line((x+12,416,x+556,416),fill=RAIL,width=3)
        h=w["deck_half_mm"]/1000;b=w["part_half_mm"]/1000
        d.rectangle((*point(cx-h,.425),*point(cx+h,.375)),fill=WATER)
        rr=point(0,.425+b*2+w["clearance_mm"]/1000);xx,yy=rr
        open_=p["release_s"] is not None and t>=p["release_s"]
        sep=max(5,round(scale*b))+(5 if open_ else 0)
        d.line((xx,yy-45,xx,yy-12),fill=SOFT,width=6);d.line((xx-sep,yy-13,xx+sep,yy-13),fill=INK,width=5)
        for side in (-1,1):d.line((xx+side*sep,yy-14,xx+side*sep,yy+2),fill=INK,width=4)
        unsafe=p["first_floor_s"] is not None and t>=p["first_floor_s"]
        d.rectangle((*point(px-b,pz+b),*point(px+b,pz-b)),fill=DROP if unsafe else PARCEL)
        status=("Floor contact" if unsafe else "Held" if p["held"] else
                "Delivered" if p["carried"] and t>=p["cycle_s"] else "Released" if open_ else "Awaiting release")
        text(d,x+23,459,status,26,DROP if unsafe else WATER,True)
        inspection="inspected" if r["inspected"] else "no inspection"
        text(d,x+23,501,f"Programmed  {r['programmed_mm_s']} mm/s     /     {inspection}",17,SOFT)
    return im


def bath_frame(s,t):
    w=s["world"];im,d=chart_frame("Bath filling","Qwen3-14B",w["id"],t)
    for j,a in enumerate(("retained","corrected")):
        x=20+590*j;r=s["rows"][a];p=r["physics"]
        _,sup,inside,catch,dry=sample(p["trace"],t)
        text(d,x+23,149,f"Saved flow  {r['retrieved']['value']} mL/s",18,SOFT)
        d.rectangle((x+162,196,x+275,208),fill=RAIL);d.rectangle((x+261,205,x+275,232),fill=RAIL)
        bottom=383;top=264;water=bottom-(bottom-top-5)*inside/w["capacity_ml"]
        d.rectangle((x+104,water,x+455,bottom-2),fill="#287888")
        d.line(((x+102,top),(x+102,bottom),(x+457,bottom),(x+457,top)),fill=INK,width=4)
        text(d,x+120,water+14,f"{inside/1000:.1f} L in bath",19,INK)
        text(d,x+23,459,"Stopped" if t>=p["time_s"] else "Checking flow",26,WATER,True)
        text(d,x+23,501,f"Added  {sup:.0f} mL     /     Escaped  {dry:.0f} mL",17,SOFT)
    return im


def encode(ffmpeg,out,scene,fn,clock,play_s):
    tmp=out.with_suffix(".tmp.mp4")
    with tempfile.TemporaryFile() as log:
        args=[ffmpeg,"-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}",
              "-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","fast","-crf","19","-pix_fmt","yuv420p",
              "-movflags","+faststart",str(tmp)]
        with subprocess.Popen(args,stdin=subprocess.PIPE,stderr=log) as proc:
            try:
                for i in range(round((play_s+1.3)*FPS)):
                    t=clock*min(1,i/(play_s*FPS))
                    proc.stdin.write(fn(scene,t).tobytes())
            finally:proc.stdin.close()
            if proc.wait()!=0:
                log.seek(0);raise RuntimeError(log.read().decode(errors="replace"))
    tmp.replace(out)
    fn(scene,clock).save(out.with_suffix(".jpg"),quality=90,optimize=True)
    return round((play_s+1.3)*FPS)/FPS


def main():
    global TYPEFACE
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("review_zip",type=Path)
    p.add_argument("--output",type=Path,default=Path("project/media"));p.add_argument("--ffmpeg",default=shutil.which("ffmpeg"))
    p.add_argument("--contact-results",type=Path,help="Earlier contact_causal/completed directory in the all-results ZIP")
    args=p.parse_args()
    if not args.ffmpeg:p.error("Pass --ffmpeg or put it on PATH")
    args.output.mkdir(parents=True,exist_ok=True)
    site_font=args.output.parent/"assets/InstrumentSans.ttf"
    if site_font.exists():TYPEFACE=site_font
    clips=[]
    def save(id,title,group,model,scene,path,source,why,caption,secs,checkpoint):
        base=args.output/id
        (base.with_suffix(".vtt")).write_text("WEBVTT\n\n00:00:00.000 --> 00:00:"+f"{secs:06.3f}\n"+caption+"\n",encoding="utf8")
        clips.append(dict(id=id,title=title,group=group,model=model,scene=scene,archive=source,record=path,
                          selection=why,caption=caption,checkpoint=checkpoint,seconds=secs,
                          sha256=file_hash(base.with_suffix(".mp4"))))
    with zipfile.ZipFile(args.review_zip) as top:
        assert read(top,"study_summary.json")["conveyor"]["status"]=="COMPLETE"
        old="evidence/completed_E0_E6_and_liquid_studies.zip"
        new="evidence/conveyor_evidence.zip"
        with zipfile.ZipFile(io.BytesIO(top.read(old))) as z:
            for task,slug,title,group,renderer,fn,why,caption in (
                ("glass","glass","Glass pouring","Glass pouring",glass_frame,
                 lambda a,b:a["unsafe"] and not b["unsafe"],"first retained-only spill",
                 "The stale position sends the pour to the right port. 150 mL escapes. Correction uses the left port and all 160 mL reaches the glass."),
                ("C","moving-tray","Moving-tray placement","Tray placement",tray_frame,
                 lambda a,b:b["unsafe"] and not a["unsafe"],"first corrected-only overload",
                 "The retained arm selects Birch and settles within its rating. The corrected arm selects Alder and the settled load exceeds 5 kg."),
                ("bath","bath","Bath filling","Bath filling",bath_frame,lambda a,b:True,"first held-out scene",
                 "Both arms inspect the flow and stop. The fill is unfinished and no liquid escapes.")):
                for i in range(48):
                    key=f"extension/cohorts/qwen14/{task}/holdout/{i:04d}.json";s=read(z,key)["data"]
                    a,b=[s["rows"][k] for k in ("retained","corrected")]
                    if a["valid"] and b["valid"] and fn(a,b):break
                else:raise ValueError("Missing declared pair for "+task)
                assert a["world_hash"]==b["world_hash"] and a["checkpoint_hash"]==b["checkpoint_hash"]
                clock=(max(r["physics"]["trace"][-1][0]/r["physics"]["hz"] for r in (a,b))
                       if task=="C" else max(r["physics"]["time_s"] for r in (a,b)))
                dur=encode(args.ffmpeg,args.output/(slug+".mp4"),s,renderer,clock,max(3.0,clock))
                save(slug,title,group,"Qwen3-14B",s["world"]["id"],key,old,why,caption,dur,a["checkpoint_hash"])
            key="original/exports/qwen_A_holdout.zip"
            with zipfile.ZipFile(io.BytesIO(z.read(key))) as nz:
                slug="stationary-tray";(args.output/(slug+".mp4")).write_bytes(nz.read("paired.mp4"))
                with Image.open(io.BytesIO(nz.read("paired.png"))) as im:im.convert("RGB").save(args.output/(slug+".jpg"),quality=90)
                r=read(nz,"scenes/A-holdout-0000/retained.json")
                save(slug,"Stationary-tray placement","Tray placement","Qwen3-8B","A-holdout-0000",key+"::paired.mp4",old,
                     "original prespecified video index 0","The recorded robot places the parcel on the stationary trays. Both panels show the settled load against the 5 kg rating.",8,r["checkpoint_hash"])
        with zipfile.ZipFile(io.BytesIO(top.read(new))) as z:
            selected=[("conveyor-14","qwen3_14b",1,"Qwen3-14B","first retained-only floor contact","The stale speed mistimes release and the parcel reaches the floor. Correction delivers the parcel."),
                      ("conveyor-8","qwen3_8b",1,"Qwen3-8B","first retained-only floor contact","The retained arm drops the parcel. Correcting the stored belt speed results in delivery."),
                      ("conveyor-reverse","qwen3_8b",41,"Qwen3-8B","first corrected-only floor contact","The retained arm succeeds. This is the one Qwen3-8B pair where only the corrected arm drops the parcel."),
                      ("conveyor-phi","phi4_14b",0,"Phi-4 14B","first enrolled layout; the edit is a no-op after a skipped report","Phi-4 stores no speed, inspects the encoder and delivers the parcel in both arms.")]
            for slug,m,i,label,why,caption in selected:
                key=f"cohorts/{m}/{i:03d}/scene.json";s=read(z,key)["scene"];a,b=[s["rows"][k] for k in ("retained","corrected")]
                assert a["checkpoint"]==b["checkpoint"]
                if slug=="conveyor-phi":assert a["retrieved"] is None and b["retrieved"] is None and a["inspected"] and b["inspected"]
                else:assert (a["floor"],b["floor"])==((False,True) if slug=="conveyor-reverse" else (True,False))
                clock=max(r["physics"]["cycle_s"] for r in (a,b))
                dur=encode(args.ffmpeg,args.output/(slug+".mp4"),s,conveyor_frame,clock,max(3.6,clock))
                save(slug,"Conveyor handoff","Conveyor handoff",label,s["world"]["scene"],key,new,why,caption,dur,a["checkpoint"])
    if args.contact_results:
        source=args.contact_results
        choice=next(x for x in json.loads((source/"video_manifest.json").read_bytes()) if x["file"]=="phi_B.mp4")
        video=source/choice["file"];assert file_hash(video)==choice["sha256"]
        shutil.copyfile(video,args.output/"pedestrian.mp4")
        with Image.open(source/"phi_B.png") as im:im.convert("RGB").save(args.output/"pedestrian.jpg",quality=90)
        save("pedestrian","Pedestrian route","Pedestrian route","Phi-4 14B","Scenario B, first scene, replicate 0",
             "phi_B.mp4","historical/results/contact_causal/completed",choice["selection"],
             "Five memory conditions are replayed from the same pedestrian scene. The archived contact audit found zero contacts in 479 valid Scenario B runs.",8,None)
    (args.output/"manifest.json").write_text(json.dumps(clips,indent=2)+"\n",encoding="utf8")
    index=[{k:v for k,v in clip.items() if k in ("id","title","model","scene","caption")} for clip in clips]
    (args.output/"replay-index.js").write_text("window.robotMemoryReplays = "+json.dumps(index,indent=2)+";\n",encoding="utf8")
    print(f"{len(clips)} verified source pairs rendered",flush=True)


if __name__=="__main__":main()
