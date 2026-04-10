# Architecture & Flux de Données

## 📐 Diagramme d'Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     NAVIGATEUR WEB                          │
│            http://localhost:8000/dashboard                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI SERVER                           │
│                 (uvicorn:8000)                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Routes API (/api/*)                        │   │
│  │  • /data/fiche-consommation                          │   │
│  │  • /data/calcul-viande                               │   │
│  │  • /data/emballage-synthese                          │   │
│  │  • /upload/*                                          │   │
│  │  • /refresh                                           │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─────────────────────────────┬──────────┐
                     │                             │          │
                     ▼                             ▼          ▼
      ┌──────────────────────┐     ┌──────────────────────┐  │
      │  Cache Manager       │     │  Memory Storage      │  │
      │  (JSON files)        │     │  (Python dict)       │  │
      └──────────────────────┘     └──────────────────────┘  │
             │                                               │
             ▼                                               │
      ┌──────────────────────┐                               │
      │  cache/*.json        │                               │
      │ • fiche...cache.json │                               │
      │ • calcul...cache.json│                               │
      │ • emballage...json   │                               │
      └──────────────────────┘                               │
                                                              │
      ┌──────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────┐
│        Excel Reader Service                  │
│  • read_excel_sheet()                        │
│  • get_fiche_consommation()                  │
│  • get_calcul_viande()                       │
│  • get_emballage_synthese()                  │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │   Files Excel        │
        │  (Desktop/Bouarfa)   │
        │  • Fiche_Complète... │
        │  • Calculateur...    │
        │  • Calculateur...    │
        └──────────────────────┘
```

## 🔄 Flux de données - Lecture

### Première visite (pas de cache):

```
1. Navigateur → http://localhost:8000/dashboard
2. FastAPI sert dashboard.html
3. dashboard → GET /api/data/all
4. API vérifie le cache → cache vide
5. API → ExcelReader.get_all_data()
6. ExcelReader → Lit fichiers .xlsx
7. Sauvegarde → cache/*.json
8. Retour → Données JSON au dashboard
9. Dashboard affiche les tableaux & stats
```

### Visite suivante (avec cache):

```
1. Navigateur → GET /api/data/fiche-consommation
2. CacheManager check cache → trouvé
3. Cache pas expiré (< 24h)
4. Retour immédiat → Données JSON
   (90% plus rapide ! ⚡)
```

## 📤 Flux de données - Mise à jour

### Upload via Dashboard:

```
1. Utilisateur → Clic "Télécharger"
2. Select file + type
3. POST /api/upload/fiche-consommation
4. FastAPI reçoit multipart/form-data
5. Sauvegarde → uploads/
6. Copy → remplace fichier original
7. ExcelReader → Relit le fichier
8. CacheManager → Sauvegarde en cache
9. Dashboard recharge → Nouvelles données visibles
```

### Upload via API:

```bash
curl -X POST -F "file=@nouveau.xlsx" \
  http://localhost:8000/api/upload/calcul-viande
```

## 🔄 Flux - Actualisation manuelle

```
1. Utilisateur → Clic "Actualiser"
2. POST /api/refresh
3. CacheManager.clear_cache()
   → Supprime tous les fichiers JSON
4. ExcelReader → Relit tous les fichiers
5. CacheManager → Sauvegarde nouveau cache
6. Dashboard → GET /api/data/all (cache vide, recharge depuis Excel)
7. Dashboard affiche les nouvelles données
```

## 📊 Structure des données

### Format JSON en cache:

```json
{
  "fiche_consommation": {
    "name": "Fiche Consommation Journalière",
    "data": [
      { "col1": val1, "col2": val2, ... },
      { "col1": val1, "col2": val2, ... },
      ...
    ],
    "columns": ["col1", "col2", ...],
    "row_count": 35,
    "last_updated": "2026-04-10T10:30:45.123456"
  },
  "timestamp": "2026-04-10T10:30:45.123456"
}
```

## ⚙️ Configuration du Cache

### Durée de vie du cache

**Fichier**: `app/config.py`

```python
# Cache expires after 24 hours
# Modifier pour ajuster:
REFRESH_INTERVAL = 3600  # secondes (1 heure)
```

### Localisation du cache

```
fastapi_app/
├── cache/
│   ├── fiche_consommation_cache.json
│   ├── calcul_viande_cache.json
│   └── emballage_synthese_cache.json
```

## 🛡️ Sans Base de Données - Avantages

| Aspect | Sans DB (JSON) | Avec DB (MySQL) |
|--------|---|---|
| **Setup** | ⚡ Instant | ⏳ 30min+ |
| **Performance** | ⚡⚡ 50-100ms | ⏳ 100-200ms |
| **Stockage** | 💾 5-20MB | 💾 100MB+ |
| **Maintenance** | ✅ Aucune | ⚠️ Backups, migrations |
| **Déploiement** | ✅ Fichiers seuls | ⚠️ Services externes |
| **Coût** | 💰 Gratuit | 💰 €€/mois |
| **Complexité** | ✅ Simple | ⚠️ Complexe |

## 📈 Plans d'évolution

### Phase 2 (Prochaines améliorations):

1. **Graphiques en temps réel**
   - Chart.js pour visualiser les tendances
   - Comparaison jour/mois

2. **Export de données**
   - Export PDF
   - Export CSV

3. **Alertes**
   - Notifications si données manquantes
   - Email de mise à jour quotidienne

4. **Multi-utilisateurs**
   - Authentification
   - Permissions

5. **Optionnel: Migrer à DB**
   - Si volume > 1GB
   - Si besoin requêtes complexes
   - Si multi-instances

## 🔐 Sécurité

- ✅ Pas d'exposition directe des fichiers Excel
- ✅ Les uploads remplacent les fichiers locaux (pas d'accumulation)
- ✅ API endpoints accessibles localement (localhost:8000)
- ⚠️ Pour production: ajouter authentication

---

**Vue d'ensemble**: Simple, rapide, sans infrastructure complexe! 🚀
