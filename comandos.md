**Modo 1 — Transcrever do zero (Whisper + Groq):**
```bash
python transcrever.py "C:\caminho\da\aula.mp4"
```

**Modo 2 — Organizar transcrição do Whisper (com timestamps):**
```bash
python transcrever.py --groq "nome_da_aula_transcricao.md"
```

**Modo 3 — Organizar transcrição da PM3 (sem timestamps):**
```bash
python transcrever.py --texto "nome_da_aula.md"
```