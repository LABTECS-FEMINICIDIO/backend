"""Adicionando novas colunas

Revision ID: 28cc73b22739
Revises: f2888dc752b0
Create Date: 2025-01-20 10:41:22.937647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f2888dc752b0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vitimas', sa.Column('site1', sa.String, nullable=True))
    op.add_column('vitimas', sa.Column('site2', sa.String, nullable=True))
    op.add_column('vitimas', sa.Column('site3', sa.String, nullable=True))
    op.add_column('vitimas', sa.Column('siteGeo1', sa.String, nullable=True))
    op.add_column('vitimas', sa.Column('siteGeo2', sa.String, nullable=True))
    op.add_column('vitimas', sa.Column('siteGeo3', sa.String, nullable=True))

def downgrade() -> None:
    op.drop_column('vitimas', sa.Column('site1', sa.String, nullable=True))
    op.drop_column('vitimas', sa.Column('site2', sa.String, nullable=True))
    op.drop_column('vitimas', sa.Column('site3', sa.String, nullable=True))
    op.drop_column('vitimas', sa.Column('siteGeo1', sa.String, nullable=True))
    op.drop_column('vitimas', sa.Column('siteGeo2', sa.String, nullable=True))
    op.drop_column('vitimas', sa.Column('siteGeo3', sa.String, nullable=True))