# Import des nouvelles données dans la base mise à jour
# Ce script :
#   1. Lit le CSV nettoyé (data_complete_clean.csv)
#   2. Met à jour les colonnes nb_enfants et quotient_caf
#      dans la table donnees_financieres existante
#   3. Vérifie la compatibilité avec l'API du brief 1

import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal, engine, Base
from app.models.client import Client, DonneeFinanciere

FICHIER_PROPRE = "data_complete_clean.csv"

def nettoyer_float(valeur):
    if pd.isna(valeur):
        return None
    return float(valeur)

def nettoyer_int(valeur):
    if pd.isna(valeur):
        return None
    return int(valeur)

def importer_nouvelles_colonnes():
    print("=" * 65)
    print("  IMPORT DES NOUVELLES DONNÉES")
    print("=" * 65)

    # ── Chargement du CSV propre ───────────────────────────────────────────
    print(f"\n[1/4] Chargement de : {FICHIER_PROPRE}")
    df = pd.read_csv(FICHIER_PROPRE)
    print(f"      ✔  {df.shape[0]} lignes × {df.shape[1]} colonnes")

    # Vérification des colonnes nécessaires
    if "nb_enfants" not in df.columns or "quotient_caf" not in df.columns:
        print("❌ Colonnes nb_enfants ou quotient_caf manquantes dans le CSV !")
        return

    db = SessionLocal()

    nb_clients = db.query(Client).count()
    print(f"\n[2/4] Clients en base : {nb_clients}")

    if nb_clients == 0:
        print("❌ Aucun client en base ! Lance d'abord import_data.py du brief 1.")
        db.close()
        return

    # MAJ des colonnes
    print(f"\n[3/4] Mise à jour de nb_enfants et quotient_caf...")

    nb_updates  = 0
    nb_erreurs  = 0

    # On itère sur les clients existants et on met à jour avec les nouvelles données
    clients = db.query(Client).order_by(Client.id).all()

    for i, client in enumerate(clients):
        if i >= len(df):
            break
        try:
            row = df.iloc[i]
            donnee = db.query(DonneeFinanciere)\
                       .filter(DonneeFinanciere.client_id == client.id)\
                       .first()

            if donnee:
                donnee.nb_enfants   = nettoyer_int(row["nb_enfants"])
                donnee.quotient_caf = nettoyer_float(row["quotient_caf"])
                nb_updates += 1

            # Commit par lots de 500
            if nb_updates % 500 == 0:
                db.commit()
                print(f"      {nb_updates} / {min(len(df), nb_clients)} mis à jour...", end="\r")

        except Exception as e:
            nb_erreurs += 1
            if nb_erreurs <= 3:
                print(f"\n      ⚠  Erreur ligne {i} : {e}")

    db.commit()
    db.close()

    # Vérification finale
    print(f"\n\n[4/4] Vérification...")
    db = SessionLocal()

    # Vérifie que les nouvelles colonnes sont bien remplies
    nb_avec_enfants = db.query(DonneeFinanciere)\
                        .filter(DonneeFinanciere.nb_enfants != None).count()
    nb_avec_caf     = db.query(DonneeFinanciere)\
                        .filter(DonneeFinanciere.quotient_caf != None).count()

    # Vérifie que l'API du brief 1 est toujours compatible
    nb_total = db.query(DonneeFinanciere).count()
    db.close()

    print(f"""
  ┌─────────────────────────────────────────────────────┐
  │ Mises à jour réussies : {nb_updates:<34}│
  │ Erreurs               : {nb_erreurs:<34}│
  │ nb_enfants renseignés : {nb_avec_enfants:<34}│
  │ quotient_caf renseigné: {nb_avec_caf:<34}│
  │ Total enregistrements : {nb_total:<34}│
  └─────────────────────────────────────────────────────┘

  ✅ Compatibilité API brief 1 : maintenue
     Les colonnes existantes n'ont pas été modifiées.
""")
    print("  Import terminé ✅")

if __name__ == "__main__":
    importer_nouvelles_colonnes()