# Pipeline de nettoyage des nouvelles données
# Ce script applique les décisions issues de l'EDA et de la datasheet éthique :
#   1. Suppression orientation_sexuelle (Art. 9 RGPD)
#   2. Correction nb_enfants négatifs → 0
#   3. Correction quotient_caf négatifs → 0
#   4. Nettoyage des colonnes existantes (même pipeline que brief 1)
#   5. Export du CSV propre
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
import os

FICHIER_SOURCE = "data-all-complete-684bf9cd92797851623245-1-692db972733a4917746473.csv"
FICHIER_PROPRE = "data_complete_clean.csv"
SEUIL_COL_VIDE = 0.40
SEUIL_IQR      = 1.5

os.makedirs("graphiques", exist_ok=True)
# SECTION 1 – CHARGEMENT
print("=" * 65)
print("  NETTOYAGE DES NOUVELLES DONNÉES")
print("=" * 65)

df = pd.read_csv(FICHIER_SOURCE)
print(f"\n✔  Dataset chargé : {df.shape[0]} lignes × {df.shape[1]} colonnes")
# SECTION 2 – SUPPRESSION DONNÉES SENSIBLES (RGPD Art. 9)
print("\n" + "=" * 65)
print("  ÉTAPE 1 – SUPPRESSION DONNÉES SENSIBLES")
print("=" * 65)

# orientation_sexuelle = donnée sensible catégorie spéciale Art. 9 RGPD
# Traitement interdit sans consentement explicite
df = df.drop(columns=["orientation_sexuelle"])
print(f"\n  ❌ orientation_sexuelle supprimée (Art. 9 RGPD)")
print(f"  Dimensions restantes : {df.shape}")
# SECTION 3 – SUPPRESSION COLONNES QUASI-VIDES (> 40% NaN)
print("\n" + "=" * 65)
print("  ÉTAPE 2 – SUPPRESSION COLONNES QUASI-VIDES (> 40% NaN)")
print("=" * 65)

colonnes_a_supprimer = [col for col in df.columns
                        if df[col].isnull().mean() > SEUIL_COL_VIDE]

for col in colonnes_a_supprimer:
    print(f"\n  - {col} ({df[col].isnull().mean()*100:.1f}% NaN) → supprimée")

df = df.drop(columns=colonnes_a_supprimer)
print(f"\n✔  Dimensions restantes : {df.shape}")
# SECTION 4 – CORRECTION DES VALEURS ABERRANTES
print("\n" + "=" * 65)
print("  ÉTAPE 3 – CORRECTION VALEURS ABERRANTES")
print("=" * 65)

# nb_enfants : valeurs négatives → 0
nb_negatifs_enfants = (df["nb_enfants"] < 0).sum()
df["nb_enfants"] = df["nb_enfants"].clip(lower=0)
print(f"\n  nb_enfants : {nb_negatifs_enfants} valeurs négatives → remplacées par 0")

# quotient_caf : valeurs négatives → 0
nb_negatifs_caf = (df["quotient_caf"] < 0).sum()
df["quotient_caf"] = df["quotient_caf"].clip(lower=0)
print(f"  quotient_caf : {nb_negatifs_caf} valeurs négatives → remplacées par 0")
# SECTION 5 – IMPUTATION DES VALEURS MANQUANTES
print("\n" + "=" * 65)
print("  ÉTAPE 4 – IMPUTATION DES VALEURS MANQUANTES")
print("=" * 65)

print(f"\n  NaN avant imputation :")
print(df.isnull().sum()[df.isnull().sum() > 0].to_string())

# situation_familiale → mode
mode_situation = df["situation_familiale"].mode()[0]
df["situation_familiale"] = df["situation_familiale"].fillna(mode_situation)
print(f"\n  situation_familiale → mode : '{mode_situation}'")

# loyer_mensuel → KNN Imputer
colonnes_num = df.select_dtypes(include=np.number).columns.tolist()
imputer = KNNImputer(n_neighbors=5)
df[colonnes_num] = imputer.fit_transform(df[colonnes_num])
print(f"  loyer_mensuel → KNN Imputer (k=5)")
print(f"\n  NaN après imputation : {df.isnull().sum().sum()}")
print("  ✔  Aucune valeur manquante restante.")
# SECTION 6 – WINSORISATION DES OUTLIERS
print("\n" + "=" * 65)
print("  ÉTAPE 5 – WINSORISATION DES OUTLIERS (IQR × 1.5)")
print("=" * 65)

colonnes_a_clipper = ["revenu_estime_mois", "loyer_mensuel",
                      "montant_pret", "quotient_caf"]

for col in colonnes_a_clipper:
    Q1  = df[col].quantile(0.25)
    Q3  = df[col].quantile(0.75)
    IQR = Q3 - Q1
    borne_basse = Q1 - SEUIL_IQR * IQR
    borne_haute = Q3 + SEUIL_IQR * IQR
    nb_avant = ((df[col] < borne_basse) | (df[col] > borne_haute)).sum()
    df[col] = df[col].clip(lower=borne_basse, upper=borne_haute)
    print(f"\n  {col} : {nb_avant} valeurs winsorisées "
          f"[{borne_basse:.2f} ; {borne_haute:.2f}]")
# SECTION 7 – EXPORT
print("\n" + "=" * 65)
print("  ÉTAPE 6 – EXPORT")
print("=" * 65)

df.to_csv(FICHIER_PROPRE, index=False)

print(f"""
  ┌─────────────────────────────────────────────────────┐
  │ Dataset nettoyé exporté : {FICHIER_PROPRE:<27}│
  │ Lignes    : {df.shape[0]:<42}│
  │ Colonnes  : {df.shape[1]:<42}│
  │ NaN total : {df.isnull().sum().sum():<42}│
  └─────────────────────────────────────────────────────┘

  Colonnes finales : {list(df.columns)}

  Opérations réalisées :
  ┌─────────────────────────────────────────────────────┐
  │ 1. Suppression orientation_sexuelle (RGPD Art. 9)  │
  │ 2. Suppression colonnes > 40% NaN                  │
  │    (historique_credits, score_credit)               │
  │ 3. nb_enfants négatifs → 0                         │
  │ 4. quotient_caf négatifs → 0                       │
  │ 5. Imputation situation_familiale (mode)            │
  │ 6. Imputation loyer_mensuel (KNN k=5)               │
  │ 7. Winsorisation outliers (IQR × 1.5)              │
  └─────────────────────────────────────────────────────┘
""")
print("  Nettoyage terminé ✅")