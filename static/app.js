const SESSION_ID = crypto.randomUUID();
const chat = document.getElementById("chat");
const form = document.getElementById("form");
const input = document.getElementById("input");
const micBtn = document.getElementById("micBtn");
const player = document.getElementById("player");
const statusEl = document.getElementById("status");
const resetBtn = document.getElementById("resetBtn");

let mediaRecorder = null;
let chunks = [];
let recording = false;

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function bubble(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `flex ${role === "user" ? "justify-end" : "justify-start"}`;
  const b = document.createElement("div");
  b.className =
    `${role === "user" ? "bubble-user text-white" : "bubble-bot text-slate-100"} ` +
    "max-w-[80%] px-4 py-2.5 rounded-2xl whitespace-pre-wrap leading-relaxed";
  b.innerHTML = escapeHtml(text);
  wrap.appendChild(b);
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return b;
}

function typingIndicator() {
  const wrap = document.createElement("div");
  wrap.className = "flex justify-start";
  wrap.innerHTML = `
    <div class="bubble-bot rounded-2xl px-4 py-3 typing flex items-center gap-1">
      <span></span><span></span><span></span>
    </div>`;
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return wrap;
}

function setStatus(msg) { statusEl.textContent = msg || ""; }

async function send(text) {
  bubble("user", text);
  const tip = typingIndicator();
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ message: text, session_id: SESSION_ID }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    tip.remove();
    bubble("assistant", data.reply);
  } catch (err) {
    tip.remove();
    bubble("assistant", `Error: ${err.message}`);
  }
}

form.addEventListener("submit", e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  send(text);
});

resetBtn.addEventListener("click", async () => {
  await fetch("/api/reset", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message: "_", session_id: SESSION_ID }),
  });
  chat.innerHTML = "";
  setStatus("New chat started");
  setTimeout(() => setStatus(""), 1500);
});

function pickMime() {
  const opts = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/ogg;codecs=opus",
  ];
  for (const m of opts) {
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(m)) return m;
  }
  return "";
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = pickMime();
    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
    chunks = [];
    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) chunks.push(e.data);
    };
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(chunks, {
        type: mediaRecorder.mimeType || "audio/webm",
      });
      await sendVoice(blob);
    };
    mediaRecorder.start();
    recording = true;
    micBtn.classList.add("recording");
    setStatus("Listening ...");
  } catch (err) {
    setStatus(`Mic error: ${err.message}`);
  }
}

function stopRecording() {
  if (mediaRecorder && recording) {
    mediaRecorder.stop();
    recording = false;
    micBtn.classList.remove("recording");
    setStatus("Transcribing ...");
  }
}

micBtn.addEventListener("click", () => {
  if (recording) stopRecording();
  else startRecording();
});

async function sendVoice(blob) {
  const tip = typingIndicator();
  try {
    const fd = new FormData();
    fd.append("audio_file", blob, "input.webm");
    fd.append("session_id", SESSION_ID);
    const res = await fetch("/api/voice", { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    tip.remove();
    bubble("user", data.transcript);
    bubble("assistant", data.reply);

    const audioBlob = b64ToBlob(data.audio_b64, "audio/wav");
    player.src = URL.createObjectURL(audioBlob);
    player.play().catch(() => {});
    setStatus("");
  } catch (err) {
    tip.remove();
    bubble("assistant", `Voice error: ${err.message}`);
    setStatus("");
  }
}

function b64ToBlob(b64, type) {
  const bin = atob(b64);
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return new Blob([arr], { type });
}

// Greeting
bubble(
  "assistant",
  "Hi! I'm your Nova Finance assistant. Ask me about company policies, your team, the org chart, or onboarding. You can type or tap the mic to talk."
);
