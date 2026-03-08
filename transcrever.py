import streamlit as st
import os
import re
import json
import tempfile
from pathlib import Path
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Transcriber PM3",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:        #0a0a0f;
    --surface:   #111118;
    --border:    #1e1e2e;
    --accent:    #7c6af7;
    --accent2:   #4fd9a0;
    --accent3:   #f76c8f;
    --text:      #e2e2f0;
    --muted:     #555570;
    --mono:      'JetBrains Mono', monospace;
    --sans:      'Syne', sans-serif;
}
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(124,106,247,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 110%, rgba(79,217,160,0.08) 0%, transparent 55%),
        var(--bg) !important;
}
#MainMenu, footer, header { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
.stDeployButton { display: none !important; }
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
.hero { text-align: center; padding: 3.5rem 1rem 2rem; }
.hero-badge {
    display: inline-block; font-family: var(--mono); font-size: 0.65rem;
    letter-spacing: 0.2em; text-transform: uppercase; color: var(--accent2);
    border: 1px solid rgba(79,217,160,0.3); border-radius: 100px;
    padding: 0.3rem 1rem; margin-bottom: 1.2rem; background: rgba(79,217,160,0.06);
}
.hero-title {
    font-family: var(--sans); font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 800; line-height: 1.1; letter-spacing: -0.03em; margin: 0 0 0.8rem;
    background: linear-gradient(135deg, #fff 30%, var(--accent) 70%, var(--accent2) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub { font-family: var(--mono); font-size: 0.82rem; color: var(--muted); letter-spacing: 0.03em; }
.panel-label {
    font-family: var(--mono); font-size: 0.65rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 1rem;
}
.terminal {
    background: #070710; border: 1px solid var(--border); border-radius: 12px;
    padding: 1.2rem 1.4rem; font-family: var(--mono); font-size: 0.75rem;
    line-height: 1.8; min-height: 180px; max-height: 420px; overflow-y: auto; color: #a0a0c0;
}
.terminal .line-ok   { color: var(--accent2); }
.terminal .line-err  { color: var(--accent3); }
.terminal .line-info { color: var(--accent); }
.terminal .line-warn { color: #f7c06c; }
.terminal .prompt    { color: var(--muted); margin-right: 0.5rem; }
.result-box {
    background: #070710; border: 1px solid rgba(79,217,160,0.25); border-radius: 12px;
    padding: 1.2rem 1.4rem; font-family: var(--mono); font-size: 0.72rem;
    color: var(--accent2); max-height: 340px; overflow-y: auto;
}
.stats-row { display: flex; gap: 1rem; margin: 1rem 0; }
.stat-card {
    flex: 1; background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem; text-align: center;
}
.stat-val { font-family: var(--mono); font-size: 1.4rem; font-weight: 600; color: var(--text); display: block; }
.stat-label { font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-top: 0.2rem; }
.info-box {
    background: rgba(124,106,247,0.07); border: 1px solid rgba(124,106,247,0.2);
    border-radius: 10px; padding: 0.8rem 1rem; font-family: var(--mono);
    font-size: 0.7rem; color: #a0a0d0; line-height: 1.7;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #0d0d18 !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text) !important;
    font-family: var(--mono) !important; font-size: 0.8rem !important;
}
.stTextInput > div > div > input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(124,106,247,0.15) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label {
    font-family: var(--mono) !important; font-size: 0.7rem !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important; color: var(--muted) !important;
}
.stButton > button {
    background: var(--accent) !important; color: #fff !important; border: none !important;
    border-radius: 10px !important; font-family: var(--sans) !important;
    font-weight: 700 !important; font-size: 0.85rem !important;
    padding: 0.6rem 1.8rem !important; transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #9d8ffa !important; transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(124,106,247,0.35) !important;
}
.stDownloadButton > button {
    background: transparent !important; color: var(--accent2) !important;
    border: 1px solid rgba(79,217,160,0.35) !important; border-radius: 10px !important;
    font-family: var(--mono) !important; font-size: 0.75rem !important;
}
.stDownloadButton > button:hover { background: rgba(79,217,160,0.08) !important; border-color: var(--accent2) !important; }
[data-testid="stFileUploader"] { background: #0d0d18 !important; border: 1px dashed var(--border) !important; border-radius: 12px !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, var(--accent), var(--accent2)) !important; border-radius: 100px !important; }
.stProgress > div > div { background: var(--border) !important; border-radius: 100px !important; }
hr { border-color: var(--border) !important; }
.stAlert { background: rgba(124,106,247,0.08) !important; border: 1px solid rgba(124,106,247,0.25) !important; border-radius: 10px !important; font-family: var(--mono) !important; font-size: 0.75rem !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 100px; }
[data-testid="column"] { padding: 0 0.4rem !important; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────
def render_log(lines):
    if not lines: return ""
    html = '<div class="terminal">'
    for line in lines:
        cls = "line-ok" if "✅" in line else "line-err" if "❌" in line else "line-info" if any(x in line for x in ["🤖","🌐","🎙️","⏳"]) else "line-warn" if "⚠" in line else ""
        html += f'<div class="{cls}"><span class="prompt">›</span>{line}</div>'
    html += "</div>"
    return html

def slug(texto):
    texto = texto.lower()
    texto = re.sub(r"[^\w\s-]", "", texto)
    texto = re.sub(r"\s+", "-", texto.strip())
    return texto

def formatar_tempo(segundos):
    m = int(segundos) // 60
    s = int(segundos) % 60
    return f"{m:02d}:{s:02d}"

def limpar_json(resposta):
    resposta = resposta.strip()
    if resposta.startswith("```"):
        resposta = "\n".join(resposta.split("\n")[1:])
    if resposta.endswith("```"):
        resposta = "\n".join(resposta.split("\n")[:-1])
    resposta = re.sub(r"\\\n\s*", " ", resposta)
    return resposta.strip()

# ── GROQ API ──────────────────────────────────────────────────────────
def chamar_groq_chat(prompt, system, api_key):
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=0.3, max_tokens=4096
    )
    return response.choices[0].message.content.strip()

def transcrever_com_groq_whisper(audio_path, api_key, log_fn=None):
    """Usa a API Whisper do Groq para transcrever — funciona local e no cloud."""
    from groq import Groq
    client = Groq(api_key=api_key)
    if log_fn: log_fn("🎙️ Enviando áudio para Groq Whisper API...")
    with open(audio_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=(Path(audio_path).name, f.read()),
            model="whisper-large-v3",
            language="pt",
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )
    segmentos = []
    for seg in transcription.segments:
        texto = seg.text.strip()
        if not texto: continue
        ts = formatar_tempo(seg.start)
        segmentos.append((ts, seg.start, texto))
    if log_fn: log_fn(f"✅ {len(segmentos)} segmentos transcritos.")
    return segmentos

def comprimir_audio(input_path, log_fn=None):
    """Comprime para mp3 mono 64kbps — reduz vídeo de 600MB para ~7MB."""
    import subprocess
    if log_fn: log_fn("🔧 Comprimindo áudio (mp3 64kbps)...")
    out_path = input_path.replace(Path(input_path).suffix, "_compressed.mp3")
    cmd = ["ffmpeg", "-y", "-i", input_path, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", out_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr}")
    size_mb = os.path.getsize(out_path) / 1024 / 1024
    if log_fn: log_fn(f"✅ Áudio comprimido: {size_mb:.1f} MB")
    return out_path

# ── LÓGICA DE ESTRUTURAÇÃO ────────────────────────────────────────────
def estruturar_com_ia(segmentos_texto, api_key, log_fn=None):
    if log_fn: log_fn("🤖 Enviando para Groq (llama-3.3-70b) estruturar...")
    texto_com_ts = "\n".join([f"[{ts}] {texto}" for ts, texto in segmentos_texto])
    system = """Você é um especialista em Product Management e educação.
Receberá a transcrição de uma aula com timestamps no formato [MM:SS].
Retorne um JSON com:
1. "resumo": resumo inteligente sobre o CONTEÚDO da aula. Use markdown. Seja denso e útil como material de estudo.
2. "blocos": lista de objetos com:
   - "timestamp_inicio": o [MM:SS] exato de um dos timestamps recebidos
   - "titulo": título do bloco
   - "subtitulo": subtítulo descritivo (ou null)
   - "conceitos_chave": lista de 2 a 4 strings com os conceitos mais importantes
Retorne APENAS o JSON puro, sem markdown ao redor."""
    resposta = chamar_groq_chat(f"Transcrição:\n\n{texto_com_ts}", system, api_key)
    return json.loads(limpar_json(resposta))

def estruturar_texto_sem_ts(paragrafos, api_key, log_fn=None):
    if log_fn: log_fn("🤖 Enviando para Groq (llama-3.3-70b) estruturar...")
    system = """Você é um especialista em Product Management e educação.
Receberá a transcrição de uma aula SEM timestamps, dividida em parágrafos numerados como [P1], [P2], etc.
Retorne um JSON com:
1. "resumo": resumo inteligente sobre o CONTEÚDO da aula. Use markdown. Seja denso e útil como material de estudo.
2. "blocos": lista de objetos com:
   - "paragrafo_inicio": número inteiro do parágrafo onde o bloco começa
   - "titulo": título do bloco
   - "subtitulo": subtítulo descritivo (ou null)
   - "conceitos_chave": lista de 2 a 4 strings com os conceitos mais importantes
Retorne APENAS o JSON puro, sem markdown ao redor."""
    texto_num = "\n\n".join([f"[P{i+1}] {p}" for i, p in enumerate(paragrafos)])
    resposta = chamar_groq_chat(f"Transcrição:\n\n{texto_num}", system, api_key)
    return json.loads(limpar_json(resposta))

# ── MONTAGEM DE MARKDOWN ──────────────────────────────────────────────
def montar_markdown_ts(nome_base, segmentos, resumo, mapa_blocos, modelo=None):
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    linhas = [f"# {nome_base}\n"]
    if modelo:
        linhas.append(f"> 📅 {data_hoje} · 🎙️ Groq Whisper `{modelo}` · 🤖 Groq `llama-3.3-70b`\n")
    else:
        linhas.append(f"> 📅 {data_hoje} · 🤖 Groq `llama-3.3-70b`\n")
    linhas.append("\n---\n")
    if mapa_blocos:
        linhas.append("## 🗂️ Índice\n")
        if resumo: linhas.append("- [📋 Resumo da Aula](#-resumo-da-aula)")
        linhas.append("- [📝 Transcrição](#-transcrição)")
        for bloco in sorted(mapa_blocos.values(), key=lambda b: b["timestamp_inicio"]):
            linhas.append(f"  - [{bloco['titulo']}](#{slug(bloco['titulo'])})")
        linhas.append("\n---\n")
    if resumo:
        linhas.append("## 📋 Resumo da Aula\n")
        linhas.append(resumo + "\n")
        linhas.append("\n---\n")
    linhas.append("## 📝 Transcrição\n")
    segmento_atual, ultimo_minuto = [], -1
    for ts, inicio, texto in segmentos:
        minuto = int(inicio) // 60
        if ts in mapa_blocos:
            if segmento_atual: linhas.append(" ".join(segmento_atual) + "\n"); segmento_atual = []
            bloco = mapa_blocos[ts]
            linhas.append(f"\n### {bloco['titulo']}\n")
            if bloco.get("subtitulo"): linhas.append(f"*{bloco['subtitulo']}*\n")
            conceitos = bloco.get("conceitos_chave", [])
            if conceitos: linhas.append(f"\n> 💡 **Conceitos-chave:** {' · '.join([f'`{c}`' for c in conceitos])}\n")
            ultimo_minuto = minuto
        if minuto != ultimo_minuto:
            if segmento_atual: linhas.append(" ".join(segmento_atual) + "\n"); segmento_atual = []
            linhas.append(f"\n`{ts}` ")
            ultimo_minuto = minuto
        segmento_atual.append(texto)
    if segmento_atual: linhas.append(" ".join(segmento_atual) + "\n")
    return "\n".join(linhas)

def montar_markdown_sem_ts(nome_base, paragrafos, resumo, blocos):
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    linhas = [f"# {nome_base}\n", f"> 📅 {data_hoje} · 🤖 Groq `llama-3.3-70b` · Transcrição PM3\n", "\n---\n"]
    if blocos:
        linhas.append("## 🗂️ Índice\n")
        if resumo: linhas.append("- [📋 Resumo da Aula](#-resumo-da-aula)")
        linhas.append("- [📝 Transcrição](#-transcrição)")
        for bloco in blocos: linhas.append(f"  - [{bloco['titulo']}](#{slug(bloco['titulo'])})")
        linhas.append("\n---\n")
    if resumo:
        linhas.append("## 📋 Resumo da Aula\n")
        linhas.append(resumo + "\n")
        linhas.append("\n---\n")
    linhas.append("## 📝 Transcrição\n")
    mapa = {b["paragrafo_inicio"]: b for b in blocos}
    for i, paragrafo in enumerate(paragrafos):
        num = i + 1
        if num in mapa:
            bloco = mapa[num]
            linhas.append(f"\n### {bloco['titulo']}\n")
            if bloco.get("subtitulo"): linhas.append(f"*{bloco['subtitulo']}*\n")
            conceitos = bloco.get("conceitos_chave", [])
            if conceitos: linhas.append(f"\n> 💡 **Conceitos-chave:** {' · '.join([f'`{c}`' for c in conceitos])}\n")
        linhas.append(paragrafo + "\n")
    return "\n".join(linhas)

# ── SESSION STATE ─────────────────────────────────────────────────────
for k, v in [("modo", 1), ("log_lines", []), ("resultado_md", ""), ("concluido", False)]:
    if k not in st.session_state: st.session_state[k] = v

def add_log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.log_lines.append(f"[{ts}] {msg}")

# ── HERO ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ Groq Whisper · LLaMA 3.3 · Funciona em qualquer lugar</div>
    <h1 class="hero-title">Transcriber PM3</h1>
    <p class="hero-sub">Transcrição · Organização · Resumo inteligente</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="panel-label">⚙ Configurações</p>', unsafe_allow_html=True)
    groq_key = st.text_input("Groq API Key", value="", type="password",
                              placeholder="gsk_...")
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#555570;line-height:2.2">
    <span style="color:#7c6af7">●</span> Modo 1 — Upload vídeo/áudio<br>
    <span style="color:#4fd9a0">●</span> Modo 2 — .md com timestamps<br>
    <span style="color:#f76c8f">●</span> Modo 3 — Texto PM3<br><br>
    <span style="color:#555570;font-size:0.6rem">
    Transcrição via Groq Whisper API<br>
    Sem limite de tamanho · 100% cloud
    </span>
    </div>
    """, unsafe_allow_html=True)

# ── MODE SELECTOR ─────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
mode_data = [
    (1, col1, "🎙️", "Modo 1 — Transcrever", "Upload de vídeo ou áudio. Transcrição via Groq Whisper + organização com LLaMA.", "#7c6af7", "Vídeo / Áudio"),
    (2, col2, "⚡", "Modo 2 — Reorganizar",  "Aplica Groq em transcrição já gerada com timestamps pelo Whisper local.",           "#4fd9a0", "Com timestamps"),
    (3, col3, "📄", "Modo 3 — Texto PM3",    "Organiza transcrição copiada da plataforma PM3, sem timestamps.",                  "#f76c8f", "Sem timestamps"),
]
for num, col, icon, name, desc, cor, tag in mode_data:
    with col:
        if st.button(f"{icon} {name}", key=f"btn_mode_{num}", use_container_width=True):
            st.session_state.modo = num
            st.session_state.log_lines = []
            st.session_state.resultado_md = ""
            st.session_state.concluido = False
            st.rerun()
        ativo = "border:1px solid " + cor + ";background:rgba(124,106,247,0.06)" if st.session_state.modo == num else "border:1px solid #1e1e2e"
        st.markdown(f"""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.67rem;color:#555570;
                    padding:0.5rem 0.3rem;border-radius:8px;margin-top:0.3rem;{ativo}
                    padding:0.6rem 0.8rem;line-height:1.7">
            {desc}<br>
            <span style="color:{cor};font-size:0.58rem;text-transform:uppercase;letter-spacing:0.1em">◆ {tag}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── INPUT + RUN ───────────────────────────────────────────────────────
modo = st.session_state.modo
input_col, _, run_col = st.columns([5, 0.2, 1.8])

arquivo_video_bytes = None
arquivo_video_nome  = None
arquivo_md_content  = None
arquivo_md_nome     = None

with input_col:
    if modo == 1:
        st.markdown('<p class="panel-label">📁 Arquivo de vídeo ou áudio</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
        ✦ Upload direto — sem limite de tamanho via Groq Whisper API<br>
        ✦ O áudio é comprimido automaticamente antes do envio (~7 MB para 14 min)<br>
        ✦ Formatos: mp4 · mp3 · wav · m4a · webm · mkv
        </div>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["mp4","mp3","wav","m4a","webm","mkv"],
                                    label_visibility="collapsed")
        if uploaded:
            arquivo_video_bytes = uploaded.read()
            arquivo_video_nome  = uploaded.name
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                        color:#4fd9a0;padding:0.5rem 0">
                ✓ <strong>{uploaded.name}</strong>
                <span style="color:#555570">— {len(arquivo_video_bytes)/1024/1024:.1f} MB</span>
            </div>
            """, unsafe_allow_html=True)

    elif modo == 2:
        st.markdown('<p class="panel-label">📄 Transcrição com timestamps (.md)</p>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["md","txt"], label_visibility="collapsed")
        if uploaded:
            arquivo_md_content = uploaded.read().decode("utf-8")
            arquivo_md_nome    = Path(uploaded.name).stem
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#4fd9a0;padding:0.4rem 0">
                ✓ <strong>{uploaded.name}</strong>
                <span style="color:#555570">— {len(arquivo_md_content.split())} palavras</span>
            </div>
            """, unsafe_allow_html=True)

    elif modo == 3:
        st.markdown('<p class="panel-label">📄 Transcrição da PM3 (.md)</p>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["md","txt"], label_visibility="collapsed")
        if uploaded:
            arquivo_md_content = uploaded.read().decode("utf-8")
            arquivo_md_nome    = Path(uploaded.name).stem
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#4fd9a0;padding:0.4rem 0">
                ✓ <strong>{uploaded.name}</strong>
                <span style="color:#555570">— {len(arquivo_md_content.split())} palavras</span>
            </div>
            """, unsafe_allow_html=True)

with run_col:
    st.markdown('<p class="panel-label">▶ Executar</p>', unsafe_allow_html=True)
    nome_saida = st.text_input("Nome do arquivo de saída", value="", placeholder="auto")
    run_btn = st.button("🚀  Iniciar", use_container_width=True, type="primary")

# ── EXECUÇÃO ──────────────────────────────────────────────────────────
if run_btn:
    st.session_state.log_lines   = []
    st.session_state.resultado_md = ""
    st.session_state.concluido   = False

    if not groq_key:
        st.error("Configure sua Groq API Key na barra lateral.")
        st.stop()

    log_ph = st.empty()
    prog   = st.progress(0)

    # ── MODO 1 ─────────────────────────────────────────────────────
    if modo == 1:
        if not arquivo_video_bytes:
            st.error("Faça o upload de um arquivo de vídeo ou áudio.")
            st.stop()

        add_log(f"📂 Arquivo recebido: {arquivo_video_nome}")
        log_ph.markdown(render_log(st.session_state.log_lines), unsafe_allow_html=True)
        prog.progress(5)

        try:
            suffix = Path(arquivo_video_nome).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(arquivo_video_bytes)
                tmp_path = tmp.name

            # Comprime para mp3 mono 64kbps via ffmpeg
            mp3_path = comprimir_audio(tmp_path, add_log)
            log_ph.markdown(render_log(st.session_state.log_lines), unsafe_allow_html=True)
            prog.progress(30)

            # Transcreve com Groq Whisper
            segmentos = transcrever_com_groq_whisper(mp3_path, groq_key, add_log)
            log_ph.markdown(render_log(st.session_state.log_lines), unsafe_allow_html=True)
            prog.progress(60)

            # Estrutura com LLaMA
            segs_txt  = [(ts, txt) for ts, _, txt in segmentos]
            estrutura = estruturar_com_ia(segs_txt, groq_key, add_log)
            resumo    = estrutura.get("resumo", "")
            blocos    = estrutura.get("blocos", [])
            mapa      = {b["timestamp_inicio"]: b for b in blocos}
            prog.progress(90)

            nome_base = nome_saida if nome_saida else Path(arquivo_video_nome).stem
            md = montar_markdown_ts(nome_base, segmentos, resumo, mapa, "whisper-large-v3")
            st.session_state.resultado_md = md
            st.session_state.concluido    = True
            add_log(f"✅ Concluído! {len(blocos)} blocos temáticos gerados.")
            prog.progress(100)

        except Exception as e:
            add_log(f"❌ Erro: {str(e)}")
        finally:
            try: os.unlink(tmp_path)
            except: pass
            try: os.unlink(mp3_path)
            except: pass

        log_ph.markdown(render_log(st.session_state.log_lines), unsafe_allow_html=True)

    # ── MODO 2 ─────────────────────────────────────────────────────
    elif modo == 2:
        if not arquivo_md_content:
            st.error("Selecione um arquivo .md com timestamps.")
            st.stop()

        add_log(f"📂 Lendo: {arquivo_md_nome}")
        prog.progress(15)

        segmentos_texto, ts_atual = [], "00:00"
        for linha in arquivo_md_content.splitlines():
            m = re.search(r"`?(\d{2}:\d{2})`?", linha)
            if m: ts_atual = m.group(1)
            texto = re.sub(r"`\d{2}:\d{2}`", "", linha).strip()
            texto = re.sub(r"#+\s.*", "", texto).strip()
            texto = re.sub(r">.*",    "", texto).strip()
            texto = re.sub(r"---",    "", texto).strip()
            if texto: segmentos_texto.append((ts_atual, texto))

        add_log(f"✅ {len(segmentos_texto)} segmentos encontrados.")
        prog.progress(40)
        log_ph.markdown(render_log(st.session_state.log_lines), unsafe_allow_html=True)

        try:
            estrutura = estruturar_com_ia(segmentos_texto, groq_key, add_log)
            resumo = estrutura.get("resumo", "")
            blocos = estrutura.get("blocos", [])
            mapa   = {b["timestamp_inicio"]: b for b in blocos}

            def ts_s(ts):
                p = ts.split(":"); return int(p[0])*60 + int(p[1])

            segs      = [(ts, ts_s(ts), txt) for ts, txt in segmentos_texto]
            nome_base = nome_saida if nome_saida else arquivo_md_nome
            md = montar_markdown_ts(nome_base, segs, resumo, mapa)
            st.session_state.resultado_md = md
            st.session_state.concluido    = True
            add_log(f"✅ Concluído! {len(blocos)} blocos temáticos gerados.")
            prog.progress(100)
        except Exception as e:
            add_log(f"❌ Erro: {str(e)}")

        log_ph.markdown(render_log(st.session_state.log_lines), unsafe_allow_html=True)

    # ── MODO 3 ─────────────────────────────────────────────────────
    elif modo == 3:
        if not arquivo_md_content:
            st.error("Selecione um arquivo .md da PM3.")
            st.stop()

        add_log(f"📂 Lendo: {arquivo_md_nome}")
        prog.progress(15)

        paragrafos, bloco_atual = [], []
        for linha in arquivo_md_content.splitlines():
            ls = linha.strip()
            if not ls:
                if bloco_atual: paragrafos.append(" ".join(bloco_atual)); bloco_atual = []
            else:
                bloco_atual.append(ls)
        if bloco_atual: paragrafos.append(" ".join(bloco_atual))
        paragrafos = [p for p in paragrafos if len(p) > 20]

        add_log(f"✅ {len(paragrafos)} parágrafos encontrados.")
        prog.progress(40)
        log_ph.markdown(render_log(st.session_state.log_lines), unsafe_allow_html=True)

        try:
            estrutura = estruturar_texto_sem_ts(paragrafos, groq_key, add_log)
            resumo    = estrutura.get("resumo", "")
            blocos    = estrutura.get("blocos", [])
            nome_base = nome_saida if nome_saida else arquivo_md_nome
            md = montar_markdown_sem_ts(nome_base, paragrafos, resumo, blocos)
            st.session_state.resultado_md = md
            st.session_state.concluido    = True
            add_log(f"✅ Concluído! {len(blocos)} blocos temáticos gerados.")
            prog.progress(100)
        except Exception as e:
            add_log(f"❌ Erro: {str(e)}")

        log_ph.markdown(render_log(st.session_state.log_lines), unsafe_allow_html=True)

# ── RESULTADO ─────────────────────────────────────────────────────────
if st.session_state.log_lines:
    st.markdown("---")
    log_col, result_col = st.columns([1, 1])
    with log_col:
        st.markdown('<p class="panel-label">📟 Log de execução</p>', unsafe_allow_html=True)
        st.markdown(render_log(st.session_state.log_lines), unsafe_allow_html=True)
    with result_col:
        if st.session_state.concluido and st.session_state.resultado_md:
            st.markdown('<p class="panel-label">📄 Resultado</p>', unsafe_allow_html=True)
            md = st.session_state.resultado_md
            linhas_md    = md.splitlines()
            blocos_count = sum(1 for l in linhas_md if l.startswith("### "))
            palavras     = len(md.split())
            st.markdown(f"""
            <div class="stats-row">
                <div class="stat-card"><span class="stat-val">{blocos_count}</span><span class="stat-label">Blocos</span></div>
                <div class="stat-card"><span class="stat-val">{palavras:,}</span><span class="stat-label">Palavras</span></div>
                <div class="stat-card"><span class="stat-val">{len(linhas_md)}</span><span class="stat-label">Linhas</span></div>
            </div>
            """, unsafe_allow_html=True)
            nome_dl = (nome_saida if nome_saida else "transcricao") + "_organizado.md"
            st.download_button("⬇  Baixar .md", data=md.encode("utf-8"),
                               file_name=nome_dl, mime="text/markdown", use_container_width=True)
            with st.expander("👁 Preview do markdown"):
                st.markdown(f'<div class="result-box">{md[:3000].replace("<","&lt;").replace(">","&gt;")}</div>',
                            unsafe_allow_html=True)
