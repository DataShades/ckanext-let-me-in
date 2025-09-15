"""Add lmi_impostor_session table.

Revision ID: c27704201743
Revises:
Create Date: 2025-09-15 22:53:00.627589

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c27704201743'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'lmi_impostor_session',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('target_user_id', sa.Text(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires', sa.Integer(), nullable=False),
        sa.Column('state', sa.Text(), nullable=False, server_default='active'),
        sa.ForeignKeyConstraint(['target_user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_lmi_impostor_session_target_user_id', 'target_user_id'),
        sa.Index('ix_lmi_impostor_session_user_id', 'user_id'),
    )


def downgrade():
    op.drop_table('lmi_impostor_session')
