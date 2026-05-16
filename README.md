# Discord Panel - Verstoesse & Infos mit Webseite

Ein Discord Bot mit Web-Dashboard zum Verwalten von Verstoessen und Informationen.

## Funktionen

- **Discord Bot**: Erstellt Verstoesse und Infos als Kanaele auf dem Discord Server
- **Transcript-System**: Speichert alle Nachrichten aus Verstoess-/Info-Kanaelen automatisch
- **Web-Dashboard**: Zeigt alle Verstoesse und Infos mit Transcript/Kanalinhalt an
- **Filter**: Nach Typ (Verstoss/Info), Status (Offen/Geschlossen) filtern
- **Setup via Discord**: Einfaches Setup direkt im Discord mit `!setup_order`
- **Log-System**: Optionale Logs fuer alle Aktionen

---

## Projektstruktur

```
Discordbot/
├── bot.py               # Discord Bot
├── requirements.txt     # Bot Python-Abhaengigkeiten
├── .env.example         # Beispiel-Umgebungsvariablen
├── discloud.config      # DisCloud Konfiguration
├── backend/             # FastAPI Backend (API)
│   ├── app/
│   │   ├── main.py      # API-Endpunkte
│   │   └── database.py  # Datenbank-Schema
│   ├── pyproject.toml   # Backend-Abhaengigkeiten
│   ├── Dockerfile       # Fuer Render Deployment
│   └── render.yaml      # Render Konfiguration
├── frontend/            # React Frontend (Webseite)
│   ├── src/
│   │   ├── pages/       # Dashboard, GuildView, EntryDetail
│   │   ├── lib/api.ts   # API-Client
│   │   └── App.tsx      # Router
│   ├── .env.example     # API-URL Konfiguration
│   └── vercel.json      # Vercel Konfiguration
└── README.md
```

---

## Setup-Anleitung

### 1. Discord Bot erstellen

1. Gehe zu https://discord.com/developers/applications
2. Klicke auf "New Application" und gib einen Namen ein
3. Gehe zu "Bot" und klicke "Reset Token" → **Token kopieren**
4. Aktiviere unter "Privileged Gateway Intents":
   - `SERVER MEMBERS INTENT`
   - `MESSAGE CONTENT INTENT`
5. Gehe zu "OAuth2" → "URL Generator":
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Administrator`
6. Generierte URL oeffnen und Bot zum Server einladen

### 2. Backend auf Render deployen (kostenlos)

1. Gehe zu https://render.com und erstelle einen Account
2. Klicke "New" → "Web Service"
3. Verbinde dein GitHub Repository `Discordbot`
4. Einstellungen:
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Plan**: `Free`
5. Fuege unter "Environment" hinzu:
   - `DB_PATH` = `/data/app.db`
6. Klicke "Create Web Service"
7. Warte bis deployed → **Kopiere die URL** (z.B. `https://discordbot-xxxx.onrender.com`)

### 3. Frontend auf Vercel deployen (kostenlos)

1. Gehe zu https://vercel.com und erstelle einen Account
2. Klicke "Import Project" und waehle dein `Discordbot` Repository
3. Einstellungen:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
4. Fuege unter "Environment Variables" hinzu:
   - `VITE_API_URL` = `https://deine-render-url.onrender.com` (die URL von Schritt 2.7)
5. Klicke "Deploy"
6. Warte bis deployed → Das ist deine **Webseiten-URL**!

### 4. Bot auf DisCloud deployen

1. Bearbeite die `.env` Datei:
   ```
   DISCORD_TOKEN=dein-bot-token
   API_URL=https://deine-render-url.onrender.com
   ```
2. Bearbeite `discloud.config` und setze deine Bot-ID
3. Lade auf DisCloud hoch: `bot.py`, `requirements.txt`, `.env`, `discloud.config`
4. Bot starten

### Lokal testen (optional)

```bash
# Backend
cd backend && pip install poetry && poetry install
export DB_PATH=./data/app.db && mkdir -p data
poetry run fastapi dev app/main.py --port 8000

# Bot (neues Terminal)
cp .env.example .env  # Token + API_URL eintragen
pip install -r requirements.txt && python bot.py

# Frontend (neues Terminal)
cd frontend && npm install && npm run dev
```

### 5. Discord Setup

1. Erstelle auf deinem Discord Server:
   - Einen **Text-Kanal** fuer das Panel (z.B. `#bestellungen`)
   - Eine **Kategorie** fuer Infos (z.B. `INFORMATIONEN`)
   - Eine **Rolle** die Zugriff haben soll
   - Optional: Einen **Text-Kanal** fuer Logs

2. Schreibe `!setup_order` in einen beliebigen Kanal
3. Klicke "Start Setup" und folge den Schritten:
   - Panel Channel waehlen
   - Info Kategorie waehlen
   - Rolle waehlen
   - Logs aktivieren (optional)
4. Das Panel wird automatisch erstellt

---

## Benutzung

### Discord
- Klicke im Panel auf "Neuer Eintrag"
- Gib Name und Beschreibung ein
- Waehle Typ: **Verstoss** oder **Information**
- Bei Verstoss: Schwere waehlen (Leicht/Mittel/Schwer)
- Ein Kanal wird erstellt wo man reinschreiben kann
- Mit "Schliessen" wird der Kanal geloescht und das Transcript gespeichert

### Webseite
- Startseite zeigt alle Server mit Statistiken
- Klick auf Server zeigt alle Verstoesse und Infos
- Filter nach Typ und Status (Offen/Geschlossen)
- Klick auf Eintrag zeigt Details + das komplette Transcript

### Slash-Befehle
- `/repair` - Repariert das Panel falls es fehlt

---

## API-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/api/guilds` | Alle Server auflisten |
| POST | `/api/guilds` | Server erstellen/aktualisieren |
| GET | `/api/guilds/{id}` | Server Details |
| GET | `/api/guilds/{id}/stats` | Server Statistiken |
| GET | `/api/entries` | Eintraege auflisten (filter: guild_id, entry_type, is_open) |
| POST | `/api/entries` | Eintrag erstellen |
| GET | `/api/entries/{id}` | Eintrag Details |
| PATCH | `/api/entries/{id}/close` | Eintrag schliessen |
| GET | `/api/entries/{id}/messages` | Transcript abrufen |
| POST | `/api/messages` | Nachricht speichern |
| POST | `/api/messages/bulk` | Nachrichten bulk speichern |

---

## Hosting

| Komponente | Service | Kosten |
|------------|---------|--------|
| Backend | [Render.com](https://render.com) | Kostenlos |
| Frontend | [Vercel.com](https://vercel.com) | Kostenlos |
| Bot | [DisCloud](https://discloud.com) | Dein bestehender Plan |
