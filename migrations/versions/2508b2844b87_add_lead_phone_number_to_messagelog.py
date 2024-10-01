"""Add lead_phone_number to MessageLog

Revision ID: 2508b2844b87
Revises: 5041a0b5f341
Create Date: 2024-10-01 16:26:47.550916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2508b2844b87'
down_revision = '5041a0b5f341'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lead_phone_number', sa.String(length=20), nullable=True))

    with op.batch_alter_table('userphones', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('userphones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.VARCHAR(length=256), nullable=True))

    with op.batch_alter_table('message_logs', schema=None) as batch_op:
        batch_op.drop_column('lead_phone_number')

    # ### end Alembic commands ###
