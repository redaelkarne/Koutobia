# 🚀 Quick Start Guide - Tableau de Bord Approvisionnement

## Installation rapide (5 minutes)

### Étape 1: Ouvrir la console

**Windows**:
- Appuyer sur `Win + R`
- Taper `cmd` ou `powershell`
- Appuyer sur `Entrée`

### Étape 2: Naviguer au dossier

```bash
cd C:\Users\bahaeddine\Desktop\Bouarfa\fastapi_app
```

### Étape 3: Lancer l'application

**Option A - Double-clic (plus simple)**
```
Double-clic sur run.bat
```

**Option B - Ligne de commande**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## ✅ Vérification du démarrage

Vous verrez:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## 🌐 Ouvrir le Dashboard

Ouvrir votre navigateur et aller à:
```
http://localhost:8000/dashboard
```

## 💡 Cas d'utilisation

### 1️⃣ Voir les données actuelles
- Le dashboard affiche automatiquement les données au chargement
- 35 lignes de fiche consommation
- 22 lignes de calcul viande
- 11 lignes d'emballage

### 2️⃣ Mettre à jour quotidiennement
- Clic sur "📁 Télécharger fichier"
- Sélectionner le type de fichier
- Sélectionner le nouveau .xlsx
- Les données s'actualisent automatiquement

### 3️⃣ Actualiser manuellement
- Clic sur "🔄 Actualiser les données"
- Ou accès direct: `http://localhost:8000/api/refresh`

## 🎯 3 Onglets disponibles

1. **Fiche Consommation** - Vue tabulaire des 35 enregistrements
2. **Calcul Viande** - Vue tabulaire des 22 produits
3. **Emballage** - Vue tabulaire des 11 synthèses

Chaque onglet affiche les 50 premières lignes des données

## 📊 Voir les statistiques

- Compteurs en haut pour chaque fichier
- Statut en temps réel (vert = à jour)
- Timestamp de la dernière actualisation

## 🔗 API - Accès programmatique

### Récupérer toutes les données
```bash
curl http://localhost:8000/api/data/all
```

### Récupérer les données spécifiques
```bash
curl http://localhost:8000/api/data/fiche-consommation
curl http://localhost:8000/api/data/calcul-viande
curl http://localhost:8000/api/data/emballage-synthese
```

### Actualiser les données
```bash
curl -X POST http://localhost:8000/api/refresh
```

### Vider le cache
```bash
curl -X DELETE http://localhost:8000/api/cache
```

## 📝 Documentation complète

Pour la version complète, voir: [README.md](README.md)

## ⚡ Performance

- **Cache auto**: Jusqu'à 24h entre actualisation
- **Temps chargement dashboard**: < 2 secondes
- **API response time**: ~ 50-100ms

## 🆘 Problèmes courants

### Port 8000 déjà utilisé?
Modifier run.bat ligne 20:
```
--port 8080
```

### Fichiers Excel non trouvés?
Définir le dossier des fichiers Excel dans `.env`:
```
EXCEL_DIR=/chemin/vers/dossier/excel
```

### Cache corrompu?
```bash
# Vider le cache
DELETE /api/cache
```

## ✨ Logs en temps réel

La console affiche tous les appels API:
```
INFO:     Started server process
INFO:     GET http://localhost:8000/api/data/all
INFO:     POST http://localhost:8000/api/upload/fiche-consommation
```

---

🎉 **C'est tout!** Vous êtes prêt à utiliser le dashboard!

Pour arrêter: `Ctrl + C` dans la console
