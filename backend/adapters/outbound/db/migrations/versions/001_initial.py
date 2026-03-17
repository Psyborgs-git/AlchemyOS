"""Initial migration - create molecules tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-03-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create molecules and molecular_properties tables."""
    # Create molecules table
    op.create_table(
        'molecules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('smiles', sa.String(length=500), nullable=False),
        sa.Column('inchi', sa.Text(), nullable=False),
        sa.Column('inchi_key', sa.String(length=27), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('formula', sa.String(length=100), nullable=False),
        sa.Column('mol_weight', sa.Float(), nullable=False),
        sa.Column('properties', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('safety_status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('experiment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_molecules_smiles'), 'molecules', ['smiles'])
    op.create_index(op.f('ix_molecules_inchi_key'), 'molecules', ['inchi_key'], unique=True)

    # Create molecular_properties table
    op.create_table(
        'molecular_properties',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('molecule_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('property_name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('method', sa.String(length=100), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_molecular_properties_molecule_id'), 'molecular_properties', ['molecule_id'])
    op.create_index(op.f('ix_molecular_properties_property_name'), 'molecular_properties', ['property_name'])


def downgrade() -> None:
    """Drop molecules and molecular_properties tables."""
    op.drop_index(op.f('ix_molecular_properties_property_name'), table_name='molecular_properties')
    op.drop_index(op.f('ix_molecular_properties_molecule_id'), table_name='molecular_properties')
    op.drop_table('molecular_properties')

    op.drop_index(op.f('ix_molecules_inchi_key'), table_name='molecules')
    op.drop_index(op.f('ix_molecules_smiles'), table_name='molecules')
    op.drop_table('molecules')
