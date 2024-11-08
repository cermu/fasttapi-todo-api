"""added role column

Revision ID: a3f2fe3ba757
Revises: 9d1eac48eb2e
Create Date: 2024-11-07 12:27:53.279925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f2fe3ba757'
down_revision: Union[str, None] = '9d1eac48eb2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role', sa.String(length=10), nullable=False))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'role')
    # ### end Alembic commands ###
