"""add category in ticket

Revision ID: d8b182eb249c
Revises: 74f75afa574f
Create Date: 2026-09-07 11:55:06.035378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8b182eb249c'
down_revision: Union[str, Sequence[str], None] = '74f75afa574f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tickets', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_tickets_category_id_categories', 'tickets', 'categories',['category_id'], ['id'], ondelete='SET NULL')
    pass


def downgrade() -> None:
    op.drop_constraint('fk_tickets_category_id_categories', 'tickets', type_='foreignkey')
    op.drop_column('tickets', 'category_id')
    pass
