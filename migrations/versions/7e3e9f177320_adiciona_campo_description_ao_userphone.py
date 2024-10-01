"""Adiciona campo phone_description ao UserPhone

Revision ID: 7e3e9f177320
Revises: d0c870efe078
Create Date: 2024-09-28 12:53:23.103974

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e3e9f177320'
down_revision = 'd0c870efe078'
branch_labels = None
depends_on = None


def upgrade():
    # Update the migration to add 'phone_description' instead of 'description'
    with op.batch_alter_table('userphones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone_description', sa.String(length=256), nullable=True))


def downgrade():
    # Drop 'phone_description' on downgrade
    with op.batch_alter_table('userphones', schema=None) as batch_op:
        batch_op.drop_column('phone_description')