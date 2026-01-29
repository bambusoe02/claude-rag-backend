# Railway Volume Setup - Zmniejszenie rozmiaru projektu

## Problem
Projekt przekracza limit 4GB na Railway (obecnie ~7.7GB). Główną przyczyną jest baza danych `chroma_db/`, która rośnie wraz z dodawanymi dokumentami.

## Rozwiązanie: Railway Volume

Użyj Railway Volume do przechowywania `chroma_db/` poza kontenerem. To:
- ✅ Zmniejsza rozmiar kontenera (nie liczy się do limitu 4GB)
- ✅ Dane są trwałe (nie znikają przy redeploy)
- ✅ Można łatwo zarządzać rozmiarem

## Instrukcje konfiguracji

### 1. W Railway Dashboard:

1. Przejdź do swojego projektu
2. Kliknij **"New"** → **"Volume"**
3. Nazwij volume: `chroma-db-storage`
4. Wybierz mount path: `/app/chroma_db`
5. Kliknij **"Add"**

### 2. Ustaw zmienną środowiskową:

W Railway Dashboard → Variables, dodaj:
```
CHROMA_DB_PATH=/app/chroma_db
```

### 3. Alternatywnie - użyj Railway Volume w railway.toml:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
```

**Uwaga:** Railway Volume musi być skonfigurowany w dashboardzie, nie w pliku toml.

## Sprawdzenie rozmiaru

Po konfiguracji volume:
- Kontener: ~500MB-1GB (bez chroma_db)
- Volume: osobna przestrzeń (nie liczy się do limitu 4GB kontenera)
- **Całkowity rozmiar projektu: < 4GB** ✅

## Czyszczenie danych (jeśli potrzebne)

Jeśli `chroma_db/` jest za duży, możesz go wyczyścić:

1. W Railway Dashboard → Volume → `chroma-db-storage`
2. Kliknij **"Delete"** (ostrożnie - usuwa wszystkie dane!)
3. Utwórz nowy volume
4. Aplikacja utworzy nową pustą bazę przy starcie

## Monitoring rozmiaru

Sprawdź rozmiar volume w Railway Dashboard:
- Volume → `chroma-db-storage` → pokazuje użycie przestrzeni

