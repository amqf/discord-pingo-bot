# Discord Multi-Channel Alert Sound Bot

## Resumo
Bot Discord que toca **sons diferentes para canais específicos**.  
Permite monitoramento de múltiplos canais ao mesmo tempo, com configuração via `.env`, sem depender de notificações visuais.

---

## Objetivo
Receber alertas sonoros distintos para cada canal crítico do Discord, ideal para automação, monitoramento de logs ou notificações importantes em tempo real.

---

## Funcionalidades
- Monitoramento de **múltiplos canais simultaneamente**  
- **Sons personalizados** por canal  
- Configuração simples via `.env`  
- Compatível com Linux, macOS e Windows  
- Fallback para tocar som usando **players nativos** (`ffplay`, `paplay`, `afplay`, `powershell`)  
- Evita poluição de pacotes globais, usando **venv isolado**

---

## Requisitos

### Python
- **Python 3.10 ou 3.11** recomendado  
- Python 3.12 funciona **somente com fallback de sistema**, `simpleaudio` pode falhar

### Linux
- Para tocar MP3/WAV via CLI: `ffmpeg` (instala `ffplay`)
```bash
sudo apt update
sudo apt install -y ffmpeg
````

* Para usar `simpleaudio` (opcional, só WAV): `libasound2-dev` + build-essential

```bash
sudo apt install -y libasound2-dev build-essential python3-dev
```

### macOS

* Player nativo: `afplay` (já incluso)

### Windows

* Player nativo: PowerShell (`.PlaySync()`) ou `playsound` Python

---

## Configuração do Token do Bot

Para que o bot funcione corretamente:

1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Crie uma aplicação (**New Application**) ou selecione a existente
3. No menu lateral, vá em **Bot → Add Bot → Yes, do it!**
4. Ative **MESSAGE CONTENT INTENT** no painel do Bot
5. Gere um link OAuth2 em **OAuth2 → URL Generator** com as permissões:

   * `Read Messages/View Channels`
   * `Send Messages` (opcional)
   * `Read Message History`
6. Copie o token do Bot em **Bot → Click to Reveal Token** e coloque no `.env`:

```env
TOKEN="SEU_BOT_TOKEN_AQUI"
```

> ⚠️ Mantenha o token em segredo. Qualquer pessoa com ele pode controlar seu bot.

---

## Configuração do ambiente

### 1. Criar e ativar o venv

```bash
python3.12 -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\Activate.ps1     # Windows PowerShell
```

### 2. Atualizar ferramentas

```bash
pip install --upgrade pip setuptools wheel
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

> Se estiver usando Linux e Python 3.12, recomendamos **remover `simpleaudio`** do `requirements.txt` e usar o fallback via `ffplay` para evitar erros de compilação.

---

## Configuração do .env

Exemplo de `.env`:

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

* `_N` permite configurar múltiplos canais.
* `DEBOUNCE_SECONDS` evita spam de sons repetidos.

---

## Testando o ambiente (opcional)

Você pode usar um script de teste standalone (`test.py`) para validar `.env`, paths de som e execução de players sem precisar do Discord.

```bash
python test.py
```

---

## Tabela de compatibilidade áudio

| Sistema | Player recomendado     | Formato | Observação                             |
| ------- | ---------------------- | ------- | -------------------------------------- |
| Linux   | ffplay / paplay / mpv  | MP3/WAV | `simpleaudio` precisa `libasound2-dev` |
| macOS   | afplay                 | MP3/WAV | nativo, sem libs extras                |
| Windows | PowerShell / playsound | MP3/WAV | playsound é Python puro, compatível    |

---

## Observações

* É recomendado **usar WAV** no Linux com `simpleaudio` para evitar compilação.
* Para MP3, instale `ffmpeg` ou `mpv`.
* Adicione quantos canais desejar no `.env` seguindo o padrão numerado `_N`.
* O bot é isolado no venv, sem poluir pacotes globais.

---

## Licença

MIT License

```
