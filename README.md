# 🗄️ M3 Brief 2 – Extension de la Base de Données
### Projet FastIA – Intégration de nouvelles sources de données

---

## 📋 Description

FastIA intègre de nouvelles sources de données dans sa base relationnelle existante.
Ce projet étend le schéma du **Brief 1** en ajoutant de nouvelles colonnes via une
migration **Alembic**, sans casser l'API ni les données existantes.

---

## 📁 Structure du projet

```
fastia-m3-brief2-db-extension/
├── alembic.ini                          # Configuration Alembic
├── app/
│   ├── config/
│   │   └── database.py                  # Connexion SQLAlchemy
│   └── models/
│       └── client.py                    # Modèles ORM mis à jour
├── migrations/
│   ├── env.py                           # Environnement Alembic
│   ├── README_migrations.md             # Documentation migrations
│   └── versions/
│       └── 001_add_nb_enfants_quotient_caf.py  # Migration brief 2
├── scripts/
│   ├── eda_nouvelles_donnees.py         # Analyse exploratoire
│   ├── clean_nouvelles_donnees.py       # Pipeline nettoyage
│   └── import_nouvelles_donnees.py      # Import en base
├── graphiques/
│   └── 01_nouvelles_colonnes.png        # Visualisation EDA
├── datasheet_nouvelles_donnees.md       # Analyse éthique
└── README.md
```

---

## 🔍 Nouvelles données analysées

Le nouveau dataset contient **3 colonnes supplémentaires** par rapport au brief 1 :

| Colonne | Type | Décision | Justification |
|---|---|---|---|
| `orientation_sexuelle` | Catégorielle | ❌ **Supprimée** | Donnée sensible – RGPD Art. 9 |
| `nb_enfants` | Entier | ✅ **Conservée** | Pertinente métier, valeurs négatives corrigées |
| `quotient_caf` | Float | ✅ **Conservée** | Donnée financière pertinente |

---

## ⚖️ Décisions éthiques

### `orientation_sexuelle` – Suppression obligatoire

L'orientation sexuelle est une **donnée sensible de catégorie spéciale** selon l'article 9 du RGPD. Son traitement est interdit sans consentement explicite. Elle a été **exclue du pipeline** avant toute intégration en base.

### `nb_enfants` – Correction des anomalies

252 valeurs négatives détectées (2.52%) → remplacées par `0` (valeur minimale logique).

### `quotient_caf` – Correction des anomalies

66 valeurs négatives détectées → remplacées par `0`.

---

## 🔧 Pipeline de traitement

```bash
# 1. Analyse exploratoire
python3 scripts/eda_nouvelles_donnees.py

# 2. Nettoyage des données
python3 scripts/clean_nouvelles_donnees.py

# 3. Migration du schéma
alembic upgrade head

# 4. Import des nouvelles données
python3 scripts/import_nouvelles_donnees.py
```

---

## 📦 Migration Alembic

### Ce que fait la migration `001`

Ajoute deux colonnes dans `donnees_financieres` :

```python
op.add_column("donnees_financieres",
    sa.Column("nb_enfants", sa.Integer(), nullable=True))
op.add_column("donnees_financieres",
    sa.Column("quotient_caf", sa.Float(), nullable=True))
```

### Commandes utiles

```bash
# Appliquer la migration
alembic upgrade head

# Vérifier l'état
alembic current

# Historique
alembic history

# Rollback
alembic downgrade -1
```

### Vérification post-migration

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('fastia.db')
cursor = conn.execute('PRAGMA table_info(donnees_financieres)')
for col in cursor.fetchall():
    print(col)
conn.close()
"
```

---

## 🔗 Compatibilité avec le Brief 1

| Élément | Statut |
|---|---|
| Table `clients` | ✅ Inchangée |
| Table `profils` | ✅ Inchangée |
| Table `donnees_financieres` | ✅ Étendue (2 colonnes ajoutées) |
| API FastAPI (brief 1) | ✅ Fonctionnelle |
| Données existantes | ✅ Préservées |

Les nouvelles colonnes sont `nullable=True` ce qui garantit la rétrocompatibilité totale avec les données et l'API du brief 1.

---

## 🚀 Installation

```bash
# Cloner le repo
git clone https://github.com/mtounekti/fastia-m3-brief2-db-extension.git
cd fastia-m3-brief2-db-extension

# Environnement virtuel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copier la base du brief 1
cp ~/projects/fastia-m3-api-database/fastia.db .

# Appliquer la migration
alembic upgrade head

# Lancer le pipeline complet
python3 scripts/eda_nouvelles_donnees.py
python3 scripts/clean_nouvelles_donnees.py
python3 scripts/import_nouvelles_donnees.py
```

---

## 🔗 Références

- [RGPD – Article 9 : données sensibles](https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre2#Article9)
- [Documentation Alembic](https://alembic.sqlalchemy.org/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)

---

*Brief M3 – Extension BDD | FastIA 2025*