let slides = [];
let index = 0;
let timer = null;
let progressTimer = null;
let playlistSignature = "";

async function loadSlides(restart=false) {
  try {
    const res = await fetch(`/api/player/${window.PLAYER_CODE}?t=${Date.now()}`, { cache: "no-store" });
    const data = await res.json();
    const incoming = data.slides || [];
    const sig = JSON.stringify(incoming.map(s => [s.url, s.duracao, s.tipo]));
    if (sig !== playlistSignature || restart) {
      slides = incoming;
      playlistSignature = sig;
      preload();
      if (!slides.length) showEmpty();
      else showSlide(0);
    }
  } catch (e) {
    console.log("Falha ao atualizar playlist", e);
  }
}

function showEmpty() {
  clearTimeout(timer);
  clearInterval(progressTimer);
  document.getElementById("screen").innerHTML = `<div id="empty">Aguardando conteúdo...</div>`;
  document.getElementById("progress").style.width = "0%";
}

function preload() {
  slides.forEach(s => {
    if (s.tipo === "imagem") {
      const img = new Image();
      img.src = s.url;
    }
  });
}

function showSlide(i) {
  clearTimeout(timer);
  clearInterval(progressTimer);
  if (!slides.length) return showEmpty();

  index = i % slides.length;
  const slide = slides[index];
  const seconds = Number(slide.duracao || 10);
  const screen = document.getElementById("screen");
  screen.innerHTML = "";

  if (slide.tipo === "video") {
    const video = document.createElement("video");
    video.src = slide.url;
    video.autoplay = true;
    video.muted = true;
    video.playsInline = true;
    video.loop = false;
    video.className = "slide-media";
    video.onended = () => showSlide(index + 1);
    screen.appendChild(video);
  } else {
    const img = document.createElement("img");
    img.src = slide.url;
    img.className = "slide-media";
    screen.appendChild(img);
  }

  runProgress(seconds);
  timer = setTimeout(() => showSlide(index + 1), seconds * 1000);
}

function runProgress(seconds) {
  const bar = document.getElementById("progress");
  const start = Date.now();
  bar.style.width = "0%";
  progressTimer = setInterval(() => {
    const pct = Math.min(100, ((Date.now() - start) / (seconds * 1000)) * 100);
    bar.style.width = pct + "%";
    if (pct >= 100) clearInterval(progressTimer);
  }, 100);
}

loadSlides(true);
// Verifica alterações no servidor a cada 5 segundos para atualizar o app mais rápido.
setInterval(() => loadSlides(false), 5000);
