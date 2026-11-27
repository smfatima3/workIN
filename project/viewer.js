(() => {
  const selector = document.querySelector("#scene");
  const player = document.querySelector("#viewer");
  const hero = document.querySelector("#hero-video");
  const clips = new Map(window.robotMemoryReplays.map(clip => [clip.id, clip]));
  function select(id) {
    const clip = clips.get(id);
    if (!clip) return;
    selector.value = id;
    player.pause();
    const base = "media/" + id;
    player.poster = base + ".jpg";
    player.querySelector("source").src = base + ".mp4";
    player.querySelector("track").src = base + ".vtt";
    player.querySelector("a").href = base + ".mp4";
    player.setAttribute("aria-label", clip.title + " with " + clip.model);
    player.load();
    document.querySelector("#clip-title").textContent = clip.title;
    document.querySelector("#clip-caption").textContent = clip.caption;
    document.querySelector("#clip-id").textContent = clip.model + " · " + clip.scene;
    document.querySelector("#clip-file").href = base + ".mp4";
  }
  selector.addEventListener("change", () => {
    select(selector.value);
    const url = new URL(location.href);
    url.searchParams.set("replay", selector.value);
    if (location.protocol === "http:" || location.protocol === "https:") {
      history.replaceState(null, "", url);
    }
  });
  player.addEventListener("play", () => hero.pause());
  hero.addEventListener("play", () => player.pause());
  const initial = new URLSearchParams(location.search).get("replay");
  if (clips.has(initial)) select(initial);
})();
