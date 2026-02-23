## Adatfolyam diagram

```mermaid
sequenceDiagram
    participant U as Felhasználó
    participant F as Frontend
    participant B as FastAPI
    participant AI as AI Model
    participant S as Supabase
    
    U->>F: Kép feltöltése
    F->>B: POST /api/predict
    B->>AI: Kép feldolgozás
    AI-->>B: Állatfaj + confidence
    B->>S: Mentés (adatbázis + storage)
    S-->>B: Siker
    B-->>F: Eredmény + URL
    F-->>U: Térképes megjelenítés