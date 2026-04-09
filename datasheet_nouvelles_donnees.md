# Datasheet – Nouvelles Données Dataset Étendu
> Projet : M3 Brief 2 – Extension de la base de données
> Date : 2025

---

## 1. Origine des nouvelles données

| Propriété | Valeur |
|---|---|
| Source | Données synthétiques complémentaires FastIA |
| Contexte | Extension du dataset M3 Brief 1 |
| Nouvelles colonnes | 3 (`orientation_sexuelle`, `nb_enfants`, `quotient_caf`) |
| Lignes | 10 000 (identiques au brief 1) |

---

## 2. Analyse des nouvelles colonnes

### `orientation_sexuelle` ❌ SUPPRIMÉE

| Propriété | Valeur |
|---|---|
| Type | Catégorielle (`hom` / `het`) |
| NaN | 0% |
| Sensibilité | 🔴 **Donnée sensible – Article 9 RGPD** |

**Justification de suppression :**
L'orientation sexuelle est une donnée à caractère personnel **sensible** au sens de l'article 9 du RGPD. Son traitement est **interdit** sauf consentement explicite de la personne concernée. De plus :
- Elle n'a aucune pertinence métier pour l'évaluation d'un risque crédit
- Son utilisation dans un modèle d'IA introduirait une discrimination directe
- Sa conservation constituerait un risque légal majeur pour FastIA

**Décision : Suppression obligatoire avant toute intégration en base.**

---

### `nb_enfants` ✅ CONSERVÉE (après correction)

| Propriété | Valeur |
|---|---|
| Type | Entier |
| NaN | 0% |
| Valeurs négatives | ~1% (aberrantes) |
| Sensibilité | 🟡 Faible (donnée socio-démographique) |

**Anomalies détectées :**
Des valeurs négatives (-1, -2, -4...) ont été détectées. Un nombre d'enfants ne peut pas être négatif — ces valeurs sont des erreurs de saisie ou d'encodage.

**Décision : Remplacement des valeurs négatives par 0** (valeur minimale logique).

**Pertinence métier :** Le nombre d'enfants est corrélé aux charges du foyer et donc pertinent pour l'évaluation du risque crédit.

---

### `quotient_caf` ✅ CONSERVÉE

| Propriété | Valeur |
|---|---|
| Type | Float |
| NaN | 0% |
| Distribution | Approximativement normale |
| Sensibilité | 🟢 Faible (donnée financière agrégée) |

**Justification :**
Le quotient familial CAF est une donnée financière publique qui reflète les revenus et charges d'un foyer. Elle est directement pertinente pour l'évaluation du risque crédit et ne présente aucune anomalie.

**Décision : Conservation avec standardisation (StandardScaler).**

---

## 3. Impact sur le schéma existant

| Table | Modification |
|---|---|
| `donnees_financieres` | Ajout de `nb_enfants` (Integer) et `quotient_caf` (Float) |
| `clients` | Aucune modification |
| `profils` | Aucune modification |

Les modifications sont **rétrocompatibles** — les colonnes existantes ne sont pas touchées, l'API du brief 1 reste fonctionnelle.

---

## 4. Risques éthiques résiduels

| Colonne | Risque | Mitigation |
|---|---|---|
| `nb_enfants` | Discrimination indirecte (familles nombreuses) | À surveiller lors de l'évaluation du modèle |
| `quotient_caf` | Proxy socio-économique | Acceptable car directement lié au risque crédit |

---

## 5. Références réglementaires

- [RGPD – Article 9 : données sensibles](https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre2#Article9)
- [CNIL – Recommandations IA 2025](https://www.cnil.fr/fr/ia-et-rgpd-la-cnil-publie-ses-nouvelles-recommandations)