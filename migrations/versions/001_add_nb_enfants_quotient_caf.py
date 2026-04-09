"""ajout nb_enfants et quotient_caf dans donnees_financieres

Revision ID: 001_add_nb_enfants_quotient_caf
Revises:
Create Date: 2025-12-01

Description:
    Migration brief 2 – Ajout de deux nouvelles colonnes dans la table
    donnees_financieres pour intégrer les nouvelles sources de données :
    - nb_enfants (Integer) : nombre d'enfants du client
    - quotient_caf (Float) : quotient familial CAF

    orientation_sexuelle NON intégrée : donnée sensible Art. 9 RGPD.

    Cette migration est rétrocompatible : les colonnes existantes ne sont
    pas modifiées, l'API du brief 1 reste fonctionnelle.
"""

from alembic import op
import sqlalchemy as sa

# Identifiants de révision
revision = "001_add_nb_enfants_quotient_caf"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Ajout des colonnes nb_enfants et quotient_caf dans donnees_financieres.
    Les colonnes sont nullable pour assurer la rétrocompatibilité avec
    les données existantes du brief 1.
    """
    op.add_column(
        "donnees_financieres",
        sa.Column("nb_enfants", sa.Integer(), nullable=True,
                  comment="Nombre d'enfants – valeurs négatives corrigées à 0")
    )
    op.add_column(
        "donnees_financieres",
        sa.Column("quotient_caf", sa.Float(), nullable=True,
                  comment="Quotient familial CAF – donnée financière complémentaire")
    )


def downgrade() -> None:
    """
    Suppression des colonnes ajoutées – rollback de la migration.
    """
    op.drop_column("donnees_financieres", "quotient_caf")
    op.drop_column("donnees_financieres", "nb_enfants")