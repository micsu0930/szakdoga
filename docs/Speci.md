# Szakdolgozat Specifikáció

## Automatikus Vadállat-felismerő Dashboard Docker-alapú Deploymenttel

---

## 1. Bevezetés és Motiváció

A vadon élő állatok monitorozása és dokumentálása fontos feladat a természetvédelemben és az ökológiai kutatásokban. A mesterséges intelligencia és a modern webtechnológiák lehetővé teszik olyan automatizált rendszerek építését, amelyek egyszerűsítik ezt a folyamatot. A projekt célja egy olyan webes dashboard létrehozása, amely neurális hálózat segítségével azonosítja a feltöltött állatfotókat, és interaktív térképen jeleníti meg a megfigyelési adatokat.

---

## 2. Problémafelvetés

Jelenleg a természetfotósok és kutatók számára nehézkes a nagy mennyiségű fotó kézi kategorizálása és geolokációs adatok kezelése. Egy automatizált rendszer, amely kombinálja a mélytanulást a térinformatikával, jelentősen felgyorsíthatja ezt a munkát és adatbázist építhet a vadállat-előfordulásokról.

---

## 3. Célkitűzések

### Főcél
Full-stack webalkalmazás fejlesztése vadállat-felismerő AI modellel, térképes vizualizációval és konténerizált deploymenttel.

### Részcélok
- Meglévő neurális háló modell integrálása a backendbe
- Felhasználói autentikációs rendszer (regisztráció, bejelentkezés)
- Képfeltöltési funkció előnézettel
- AI-alapú állatfaj-azonosítás valószínűségi pontszámmal
- Geolokációs adatok kinyerése (EXIF/metadata) vagy manuális megadás
- Interaktív térkép (Leaflet/OpenStreetMap) a megfigyelések megjelenítésére
- Supabase adatbázis és tárhely kezelése (állatfaj, helyszín, időpont, felhasználó, képek)
- Docker konténerizáció és egyetemi szerveren történő deployment

---

## 4. Felhasznált Technológiák és Módszertan

### Backend
- **Python (FastAPI)** – REST API
- **Supabase** – PostgreSQL adatbázis, autentikáció, tárhely (Storage)
- **Supabase-py** – Python kliens könyvtár
- **Pillow, NumPy** – képfeldolgozás
- **TensorFlow/PyTorch** – AI model betöltése és inferencia

### Frontend
- **HTML5, CSS3, JavaScript** (vagy React/Vue.js egyszerűsített verzió)
- **Supabase JavaScript kliens** – auth és adatbázis műveletek
- **Leaflet.js** – interaktív térkép

### DevOps/Deployment
- **Docker + Docker Compose**
- **Nginx reverse proxy**
- **Egyetemi szerver (Linux VM)** – production környezet

### Fejlesztési módszertan
- Agilis iteráció (2-3 hetes sprintek)
- Verziókezelés: Git + GitHub/GitLab
- Tesztelés: unit tesztek (pytest), manuális UI tesztek

---

## 5. Várható Eredmények

- Működő webalkalmazás forráskódja (Git repository)
- Dockerizált alkalmazás, amely `docker-compose up` paranccsal futtatható
- Dokumentáció: telepítési útmutató, API dokumentáció, felhasználói kézikönyv
- Élő demo az egyetemi szerveren
- Szakdolgozat írás (40-60 oldal): bevezetés, irodalmi áttekintés, rendszerterv, implementáció, tesztelés, összegzés

---

## 6. Ütemezés (12-14 hét)

| Hét | Feladat |
|-----|---------|
| 1-2 | Irodalomkutatás, technológiai döntések, specifikáció véglegesítése |
| 3-4 | Supabase projekt beállítása, adatbázis-séma tervezése, backend alapok |
| 5-6 | AI modell integrálása, képfeltöltés implementálása (Supabase Storage) |
| 7-8 | Frontend fejlesztés (UI, térkép, Supabase auth integráció) |
| 9-10 | Dockerizáció, tesztelés, hibajavítás |
| 11-12 | Deployment egyetemi szerverre, dokumentáció írása |
| 13-14 | Szakdolgozat írása, véglegesítés, beadás |

---

## 7. Kockázatok és Kezelésük

| Kockázat | Megoldás |
|----------|----------|
| AI modell pontatlansága | Confidence threshold beállítása, manuális korrekció lehetősége |
| Nagy képfájlok kezelése | Képkompresszió, Supabase Storage méretkorlátok kezelése |
| Supabase rate limiting | Caching stratégia, batch műveletek |
| Egyetemi szerver korlátai | Korai tesztelés a cél környezetben, resource monitoring |

---

## 8. Irodalomjegyzék (kezdeti)

- Supabase dokumentáció (supabase.com/docs)
- FastAPI dokumentáció (fastapi.tiangolo.com)
- Docker dokumentáció (docs.docker.com)
- Leaflet.js dokumentáció (leafletjs.com)
- Keras dokumentáció