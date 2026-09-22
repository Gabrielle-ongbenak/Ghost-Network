# Frontend - Ghost Networks

Ce répertoire est réservé pour le développement de l'application frontend (React / Vite ou Next.js).

---

## 🚀 Connexion avec le Backend

Le backend FastAPI tourne localement via Docker sur le port **8000**.

- **URL de base de l'API** : `http://localhost:8000`
- **Documentation interactive Swagger UI** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentation alternative ReDoc** : [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 Principaux Endpoints Disponibles

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Healthcheck de l'API (`{"status": "ok"}`) |
| `GET` | `/api/stats/overview` | Statistiques globales (nombre d'annonces, réseaux détectés, contacts suspects, répartition géographique et plateformes) |
| `GET` | `/api/listings` | Liste paginée et filtrable des annonces (`platform`, `country_code`, `risk_level`, `search`, `limit`, `offset`) |
| `GET` | `/api/listings/{id}` | Détail d'une annonce avec son score de risque, signaux détectés et contacts associés |
| `GET` | `/api/networks` | Liste des réseaux / syndicats de fraude détectés |
| `GET` | `/api/networks/{id}` | Détail d'un réseau de fraude (membres, métriques, contacts partagés) |
| `GET` | `/api/graph` | Données graphe (`nodes` et `edges`) prêtes pour la visualisation (React Flow, Vis.js, Cytoscape, D3) |
| `POST` | `/api/ingest/bulk` | Ingestion en masse de nouvelles annonces |

---

## 🔒 Configuration CORS

Le backend est configuré pour autoriser les requêtes cross-origin en provenance des environnements de dev locaux standards :
- `http://localhost:3000` (ex: Create React App, Next.js)
- `http://localhost:5173` (ex: Vite / React)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

Les méthodes (`GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`) et les headers d'autorisation / credentials sont activés.

---

## 💻 Démarrage recommandé (React + Vite)

Pour initialiser le projet frontend dans ce dossier :

```bash
# Exemple avec Vite + React + TypeScript
npm create vite@latest . -- --template react-ts
npm install
npm run dev
```

Pensez à configurer un fichier `.env` ou `.env.local` :
```env
VITE_API_URL=http://localhost:8000
```
