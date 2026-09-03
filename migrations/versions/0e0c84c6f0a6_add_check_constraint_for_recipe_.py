"""Add CHECK constraint for recipe.servings > 0

Revision ID: 0e0c84c6f0a6
Revises: 96ef4328f9e2
Create Date: 2026-09-03 10:28:19.841768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e0c84c6f0a6'
down_revision: Union[str, Sequence[str], None] = '96ef4328f9e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('recipe') as batch_op:
        batch_op.create_check_constraint('ck_recipe_servings_positive', 'servings > 0')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('recipe') as batch_op:
        batch_op.drop_constraint('ck_recipe_servings_positive', type_='check')