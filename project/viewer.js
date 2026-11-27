(() => {
  const selector = document.querySelector("#scene");
  const player = document.querySelector("#viewer");
  const hero = document.querySelector("#hero-video");
  const clips = new Map(window.robotMemoryReplays.map(clip => [clip.id, clip]));
  const native = window.robotMemoryNativeViews;
  const view3d = document.querySelector('input[name="view"][value="3d"]');
  const view2d = document.querySelector('input[name="view"][value="2d"]');
  const initial = new URLSearchParams(location.search);
  let preferred = initial.get("view") === "2d" ? "2d" : "3d";
  function geometryNote(id, use3d) {
    if (id.startsWith("conveyor")) {
      return use3d ? "The original gripper was a fixed weld. The visible geometry is the parcel, carrier and floor."
                   : "Side-view reconstruction of recorded parcel and carrier positions. The illustrated jaws represent the fixed grasp constraint.";
    }
    if (id === "pedestrian") {
      return use3d ? "The original mobile base is a box and the pedestrian is a capsule. These two native views show the retained and corrected route decisions."
                   : "Top-down schematic of the five archived memory conditions. The mobile base and pedestrian are represented by simple shapes.";
    }
    if (id.includes("tray")) return "The original Godot gantry used 2D physics. This replay draws the logged tray and parcel positions.";
    return "The liquid simulator computes water volumes. This schematic draws its recorded measurements; the study did not define a 3D liquid scene.";
  }
  function select(id, writeUrl = false) {
    const clip = clips.get(id);
    if (!clip) return;
    selector.value = id;
    player.pause();
    const use3d = Boolean(native[id]) && preferred === "3d";
    view3d.disabled = !native[id];
    view3d.checked = use3d;
    view2d.checked = !use3d;
    const base = "media/" + (use3d ? native[id].mp4.replace(/\.mp4$/, "") : id);
    player.poster = base + ".jpg";
    player.querySelector("source").src = base + ".mp4";
    player.querySelector("track").src = base + ".vtt";
    player.querySelector("a").href = base + ".mp4";
    player.setAttribute("aria-label", clip.title + " with " + clip.model + (use3d ? ", original 3D geometry" : ", 2D trace"));
    player.load();
    document.querySelector("#clip-title").textContent = clip.title;
    document.querySelector("#clip-caption").textContent = clip.caption;
    document.querySelector("#clip-id").textContent = clip.model + " · " + clip.scene;
    document.querySelector("#clip-file").href = base + ".mp4";
    document.querySelector("#clip-provenance").href = use3d ? "media/native-manifest.json" : "media/manifest.json";
    document.querySelector("#geometry-note").textContent = geometryNote(id, use3d);
    if (writeUrl && (location.protocol === "http:" || location.protocol === "https:")) {
      const url = new URL(location.href);
      url.searchParams.set("replay", id);
      url.searchParams.set("view", use3d ? "3d" : "2d");
      history.replaceState(null, "", url);
    }
  }
  selector.addEventListener("change", () => select(selector.value, true));
  for (const radio of [view2d, view3d]) {
    radio.addEventListener("change", () => {
      preferred = radio.value;
      select(selector.value, true);
    });
  }
  player.addEventListener("play", () => hero.pause());
  hero.addEventListener("play", () => player.pause());
  select(clips.has(initial.get("replay")) ? initial.get("replay") : "conveyor-14");
})();
