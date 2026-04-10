# 📊 Tableau de Bord Approvisionnement - FastAPI

Système de gestion et visualisation des données d'approvisionnement avec cache en mémoire et fichiers JSON.

## ✨ Caractéristiques

✅ **Sans base de données** - Utilise le cache en mémoire + JSON  
✅ **Dashboard interactif** - Interface web pour visualiser les données  
✅ **Téléchargement de fichiers** - Mise à jour quotidienne facile  
✅ **Auto-actualisation** - Cache mis à jour automatiquement  
✅ **API REST complète** - Endpoints pour accéder aux données  
✅ **Fast** - Performances optimales sans DB overhead  

## 📁 Structure du Projet

```
fastapi_app/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuration globale
│   ├── main.py                   # Application FastAPI
│   ├── services/
│   │   ├── __init__.py
│   │   ├── excel_reader.py       # Lecture des fichiers Excel
│   │   └── cache_manager.py      # Gestion du cache JSON
│   ├── routes/
│   │   ├── __init__.py
│   │   └── data.py               # Endpoints API
│   ├── templates/
│   │   └── dashboard.html        # Dashboard web
│   ├── models/
│   ├── schemas/
│   └── static/
├── cache/                        # Dossier des fichiers cache JSON
├── uploads/                      # Fichiers téléchargés temporaires
├── requirements.txt              # Dépendances Python
├── run.bat                       # Script de lancement
└── README.md
```

## 🚀 Installation et Lancement

### Méthode 1: Script automatique (Windows)

```bash
cd fastapi_app
double-clic sur run.bat
```

### Méthode 2: Manuel

```bash
cd fastapi_app

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📍 Accès à l'Application

Après le lancement:

- **Dashboard**: http://localhost:8000/dashboard
- **Documentation API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 Fichiers Excel Supportés

L'application charge automatiquement:

1. **Fiche_Complète_Contrôle_Approvisionnement_Interne.xlsx**
   - Feuille: `FICHE CONSOMATION JOURNALIERE`

2. **Calculateur_Ing_Viande 07,03,2026.xlsx**
   - Feuille: `📊 Conso Journalière`

3. **Calculateur_Emballage_V3.xlsx**
   - Feuille: `Synthèse Totaux`

## 🔌 API Endpoints

### Récupérer les données

```bash
# Toutes les données
GET /api/data/all

# Données spécifiques
GET /api/data/fiche-consommation
GET /api/data/calcul-viande
GET /api/data/emballage-synthese

# Avec contrôle du cache
GET /api/data/fiche-consommation?use_cache=false
```

### Télécharger des fichiers

```bash
# Télécharger via API
POST /api/upload/fiche-consommation (multipart/form-data file)
POST /api/upload/calcul-viande (multipart/form-data file)
POST /api/upload/emballage (multipart/form-data file)
```

### Gestion du cache

```bash
# Actualiser les données depuis Excel
POST /api/refresh

# Statistiques du cache
GET /api/cache-stats

# Vider le cache
DELETE /api/cache
```

### Santé de l'application

```bash
GET /health
```

## 🎯 Flux de travail quotidien

1. **Lancer l'application**
   ```bash
   double-clic run.bat
   ```

2. **Ouvrir le dashboard**
   - http://localhost:8000/dashboard

3. **Voir les données actuelles**
   - Les données sont automatiquement chargées au démarrage

4. **Mettre à jour les fichiers** (deux options):
   
   **Option A: Via Dashboard**
   - Clic bouton "📁 Télécharger fichier"
   - Sélectionner le type de fichier
   - Sélectionner le nouveau fichier .xlsx

   **Option B: Via API**
   ```bash
   curl -X POST -F "file=@nouveau_fichier.xlsx" \
     http://localhost:8000/api/upload/fiche-consommation
   ```

5. **Actualiser à tout moment**
   - Clic "🔄 Actualiser les données"
   - Ou: `POST /api/refresh`

## 💾 Système de Cache

### Comment ça marche?

1. Au démarrage, les fichiers Excel sont lus
2. Les données sont stockées en mémoire (RAM)
3. Les données sont sauvegardées en JSON dans `cache/`
4. Le cache auto-expire après 24h
5. Rechargement automatique du cache au démarrage

### Fichiers de cache

```
cache/
├── fiche_consommation_cache.json
├── calcul_viande_cache.json
└── emballage_synthese_cache.json
```

### Forcer une actualisation

```bash
# Via API
POST /api/refresh

# Via URL
curl -X POST http://localhost:8000/api/refresh
```

## 📊 Dashboard Features

- ✅ Vue des 3 sources de données
- ✅ Compteurs du nombre de lignes
- ✅ Onglets pour chaque feuille
- ✅ Tableaux affichant les 50 premières lignes
- ✅ Téléchargement de fichiers intégré
- ✅ Statut en temps réel
- ✅ Design moderne et responsive

## 🔧 Configuration

Configurer via le fichier `.env` (recommandé) pour:

- Changer le chemin des fichiers Excel
- Modifier les noms de fichiers
- Ajuster la durée de vie du cache
- Changer le port de l'API

```dotenv
# Chemin absolu (production)
EXCEL_DIR=/var/app/data/excel

# Ou chemin relatif au dossier fastapi_app
# EXCEL_DIR=../excel_data
```

## 📈 Performance

- **Temps de chargement initial**: ~1-2 secondes
- **Requête en cache**: <100ms
- **Utilisation mémoire**: ~50-200MB (selon taille des fichiers)
- **Espace disque cache**: ~5-20MB

## 🛠️ Dépannage

### Erreur: Module not found

```bash
# Assurez que l'environnement venv est activé
.venv\Scripts\activate

# Réinstaller dépendances
pip install -r requirements.txt
```

### Erreur: Fichier not found

- Vérifier que `EXCEL_DIR` pointe vers le bon dossier
- Vérifier les noms de fichiers dans `config.py`

### Cache corrompu

```bash
# Vider le cache
DELETE /api/cache

# Ou supprimer le dossier cache/
rm -r fastapi_app/cache
```

### Port 8000 déjà utilisé

Modifier dans `run.bat`:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 📞 Support

- Vérifier les logs dans la console
- Aller sur http://localhost:8000/docs pour explorer l'API
- Vérifier http://localhost:8000/health pour le statut

## 📝 Notes

- Les fichiers téléchargés remplacent les originaux
- Le cache est persistant entre les redémarrages
- Pas de base de données = pas de perte de données, tout est en fichiers
- Auto-refresh recommandé toutes les 24h

## 🎨 Personnalisation

### Ajouter une nouvelle feuille Excel

1. Éditer `config.py`:
```python
EXCEL_FILES = {
    "nouvelle_feuille": {
        "file_name": "MesData.xlsx",
        "sheet_name": "Ma Feuille",
        "cache_file": "nouvelle_feuille.json"
    }
}
```

2. Éditer `excel_reader.py` pour ajouter une méthode:
```python
@staticmethod
def get_nouvelle_feuille() -> Dict[str, Any]:
    config = EXCEL_FILES["nouvelle_feuille"]
    df = ExcelReader.read_excel_sheet(config["file_name"], config["sheet_name"])
    return {
        "name": "Nouvelle Feuille",
        "data": df.to_dict(orient='records'),
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "last_updated": datetime.now().isoformat()
    }
```

3. Éditer `data.py` pour ajouter un endpoint API

## 📜 Licence

MIT - Libre d'utilisation

---

**Version**: 1.0.0  
**Dernière mise à jour**: 10 avril 2026
