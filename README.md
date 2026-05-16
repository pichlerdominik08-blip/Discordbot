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
discord-panel/
├── bot/                  # Discord Bot
│   ├── bot.py            # Bot-Skript
│   ├── requirements.txt  # Python-Abhängigkeiten
│   └── .env.example      # Beispiel-Umgebungsvariablen
├── discord-panel-backend/ # FastAPI Backend (API)
│   ├── app/
│   │   ├── main.py       # API-Endpunkte
│   │   └── database.py   # Datenbank-Schema
│   └── pyproject.toml    # Python-Abhängigkeiten
├── discord-panel-frontend/ # React Frontend (Webseite)
│   ├── src/
│   │   ├── pages/        # Dashboard, GuildView, EntryDetail
│   │   ├── lib/api.ts    # API-Client
│   │   └── App.tsx       # Router
│   └── .env              # API-URL Konfiguration
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

### 2. Backend starten

```bash
cd discord-panel-backend

# Abhaengigkeiten installieren
pip install poetry
poetry install

# Umgebungsvariable setzen (Pfad zur Datenbank)
export DB_PATH=./data/app.db

# Server starten
mkdir -p data
poetry run fastapi dev app/main.py --port 8000
```

Das Backend laeuft jetzt auf `http://localhost:8000`

### 3. Discord Bot starten

```bash
cd bot

# Abhaengigkeiten installieren
pip install -r requirements.txt

# .env Datei erstellen
cp .env.example .env
# Bearbeite .env und setze deinen DISCORD_TOKEN und API_URL

# Bot starten
python bot.py
```

### 4. Frontend starten

```bash
cd discord-panel-frontend

# Abhaengigkeiten installieren
npm install

# .env anpassen (API URL setzen)
# Datei: .env
# VITE_API_URL=http://localhost:8000   (lokal)
# VITE_API_URL=https://deine-api.fly.dev  (deployed)

# Entwicklungsserver starten
npm run dev
```

Das Frontend laeuft auf `http://localhost:5173`

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

## Hosting / Deployment

### Backend (z.B. auf Fly.io, Railway, etc.)
- FastAPI App deployen
- `DB_PATH` Environment Variable auf persistenten Speicher setzen (z.B. `/data/app.db`)

### Frontend
- `npm run build` ausfuehren
- Den `dist` Ordner als statische Webseite hosten (z.B. Vercel, Netlify, etc.)
- `VITE_API_URL` auf die deployed Backend URL setzen

### Bot
- Auf einem Server laufen lassen (z.B. VPS, Raspberry Pi, etc.)
- `DISCORD_TOKEN` und `API_URL` in der `.env` Datei setzen
- Am besten mit `screen` oder `systemd` dauerhaft laufen lassen
