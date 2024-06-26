"""add_last_updated_column

Revision ID: 700bda68d5c4
Revises: 7428eb5a2f13
Create Date: 2023-09-23 21:09:55.758173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '700bda68d5c4'
down_revision: Union[str, None] = '7428eb5a2f13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Devices', sa.Column('last_updated', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Devices', 'last_updated')
    # ### end Alembic commands ###
