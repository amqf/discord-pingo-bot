# Discord Multi-Channel Alert Sound Bot

## Resumo
Bot Discord que toca **sons diferentes para canais específicos**, configurável via `.env`.

---

## Requisitos
- Python 3.10 ou 3.11 (3.12 funciona com fallback de sistema)  
- Linux/macOS/Windows  
- Player de áudio do sistema:
  - Linux: `ffplay` (ffmpeg), `paplay` ou `aplay`  
  - macOS: `afplay` (já incluso)  
  - Windows: PowerShell ou `playsound` Python  

---

## Configuração do Bot
1. Crie ou selecione sua aplicação no [Discord Developer Portal](https://discord.com/developers/applications)  
2. Adicione o Bot → **Add Bot**  
3. Ative **MESSAGE CONTENT INTENT**  
4. Gere URL OAuth2 com permissões:
   - `Read Messages/View Channels`
   - `Read Message History`  
5. Copie o token do Bot e coloque no `.env`:

```env
TOKEN="SEU_BOT_TOKEN_AQUI"
````

---

## Configuração do `.env`

```env
TOKEN="SEU_BOT_TOKEN_AQUI"

TARGET_CHANNEL_NOME_1=AlertasN8N
TARGET_CHANNEL_ID_1=123456789012345678
TARGET_CHANNEL_SOUND_FILE_1="alert.wav"

TARGET_CHANNEL_NOME_2=OutroCanal
TARGET_CHANNEL_ID_2=123456589012345678
TARGET_CHANNEL_SOUND_FILE_2="alert2.wav"

DEBOUNCE_SECONDS=10
```

> `_N` permite adicionar múltiplos canais.
> `DEBOUNCE_SECONDS` evita spam de sons repetidos.

---

## Preparação do ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate      # Linux/macOS
source .venv/Scripts/Activate  # Windows Bash
.venv\Scripts\Activate.ps1     # Windows PowerShell
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## Teste rápido

Use o script `test.py` para validar `.env` e tocar sons sem precisar do Discord:

```bash
python test.py
```

---

## Licença

MIT License

```
