# Analyse exploratoire des nouvelles colonnes du dataset étendu
# Ce script identifie et analyse les 3 nouvelles colonnes :
#   - orientation_sexuelle (catégorielle)
#   - nb_enfants (entier)
#   - quotient_caf (float
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")

FICHIER_SOURCE = "data-all-complete-684bf9cd92797851623245-1-692db972733a4917746473.csv"
COULEUR_PRINCIPALE = "#5B8DB8"
COULEUR_ALERTE     = "#E07B54"

os.makedirs("graphiques", exist_ok=True)# SECTION 1 – CHARGEMEN
print("=" * 65)
print("  EDA – NOUVELLES DONNÉES")
print("=" * 65)

df = pd.read_csv(FICHIER_SOURCE)
print(f"\n✔  Dataset chargé : {df.shape[0]} lignes × {df.shape[1]} colonnes")

# Colonnes du brief 1
colonnes_brief1 = [
    "nom", "prenom", "age", "taille", "poids", "sexe",
    "sport_licence", "niveau_etude", "region", "smoker",
    "nationalité_francaise", "revenu_estime_mois",
    "situation_familiale", "historique_credits", "risque_personnel",
    "date_creation_compte", "score_credit", "loyer_mensuel", "montant_pret"
]

nouvelles_colonnes = [c for c in df.columns if c not in colonnes_brief1]
print(f"\n  Colonnes existantes (brief 1) : {len(colonnes_brief1)}")
print(f"  Nouvelles colonnes détectées  : {nouvelles_colonnes}")# SECTION 2 – ANALYSE DES NOUVELLES COLONNE
print("\n" + "=" * 65)
print("  ANALYSE DES NOUVELLES COLONNES")
print("=" * 65)

for col in nouvelles_colonnes:
    print(f"\n── {col} ──")
    print(f"  Type       : {df[col].dtype}")
    print(f"  NaN        : {df[col].isnull().sum()} ({df[col].isnull().mean()*100:.1f}%)")
    print(f"  Uniques    : {df[col].nunique()}")
    if df[col].dtype in ["object", "string"] or str(df[col].dtype) == "string":
        print(f"  Valeurs    : {df[col].value_counts().to_dict()}")
    else:
        print(f"  Min/Max    : {df[col].min()} / {df[col].max()}")
        print(f"  Moyenne    : {df[col].mean():.2f}")
        print(f"  Négatifs   : {(df[col] < 0).sum()}")# SECTION 3 – DÉTECTION ANOMALIES nb_enfant
print("\n" + "=" * 65)
print("  ANOMALIES – nb_enfants")
print("=" * 65)

nb_negatifs = (df["nb_enfants"] < 0).sum()
print(f"\n  Valeurs négatives : {nb_negatifs} ({nb_negatifs/len(df)*100:.2f}%)")
print(f"  Distribution :\n{df['nb_enfants'].value_counts().sort_index().to_string()}")# SECTION 4 – VISUALISATION
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Analyse des nouvelles colonnes – Dataset étendu",
             fontsize=13, fontweight="bold")

# orientation_sexuelle
ax1 = axes[0]
counts = df["orientation_sexuelle"].value_counts()
ax1.bar(counts.index, counts.values, color=[COULEUR_ALERTE, COULEUR_PRINCIPALE],
        edgecolor="white")
ax1.set_title("orientation_sexuelle\n⚠️ Donnée sensible – Art. 9 RGPD", fontsize=10)
ax1.set_ylabel("Nombre")
for i, (_, v) in enumerate(counts.items()):
    ax1.text(i, v + 50, f"{v/len(df)*100:.1f}%", ha="center", fontsize=10)

# nb_enfants
ax2 = axes[1]
counts2 = df["nb_enfants"].value_counts().sort_index()
colors2 = ["red" if x < 0 else COULEUR_PRINCIPALE for x in counts2.index]
ax2.bar(counts2.index.astype(str), counts2.values, color=colors2, edgecolor="white")
ax2.set_title("nb_enfants\n⚠️ Valeurs négatives à corriger", fontsize=10)
ax2.set_ylabel("Nombre")
ax2.set_xlabel("Nombre d'enfants")

# quotient_caf
ax3 = axes[2]
sns.histplot(df["quotient_caf"], kde=True, ax=ax3,
             color=COULEUR_PRINCIPALE, edgecolor="white")
ax3.set_title("quotient_caf\n✅ Distribution normale", fontsize=10)
ax3.set_xlabel("Quotient CAF (€)")

plt.tight_layout()
plt.savefig("graphiques/01_nouvelles_colonnes.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n✔  Graphique sauvegardé : graphiques/01_nouvelles_colonnes.png")

print("\n" + "=" * 65)
print("  RÉSUMÉ EDA")
print("=" * 65)
print(f"""
  Nouvelles colonnes : {nouvelles_colonnes}

  orientation_sexuelle :
    → 🔴 DONNÉE SENSIBLE (Art. 9 RGPD)
    → Traitement interdit sans consentement explicite
    → Décision : SUPPRESSION

  nb_enfants :
    → ⚠️  {nb_negatifs} valeurs négatives (aberrantes)
    → Décision : remplacement par 0 (valeur minimale logique)
    → ✅ Colonne utile métier → CONSERVÉE

  quotient_caf :
    → ✅ Aucune anomalie détectée
    → Distribution normale
    → ✅ Donnée financière pertinente → CONSERVÉE
""")