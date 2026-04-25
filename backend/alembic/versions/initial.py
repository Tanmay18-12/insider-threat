"""initial

Revision ID: initial
Revises: 
Create Date: 2026-04-24 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # We will let SQLAlchemy create tables on app start since we can't test docker right now.
    # However, for completeness of the alembic script:
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('USER', 'ADMIN', name='roleenum'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('baseline_computed', sa.Boolean(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table('ml_models',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_name', sa.String(), nullable=True),
        sa.Column('model_type', sa.String(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('trained_at', sa.DateTime(), nullable=True),
        sa.Column('feature_columns', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ml_models_model_name'), 'ml_models', ['model_name'], unique=False)

    op.create_table('user_baselines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('avg_daily_logins', sa.Float(), nullable=True),
        sa.Column('typical_hours', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('common_resources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('avg_file_accesses', sa.Float(), nullable=True),
        sa.Column('departments_accessed', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    op.create_table('activity_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.Enum('LOGIN', 'LOGOUT', 'FILE_ACCESS', 'FILE_DOWNLOAD', 'FILE_UPLOAD', 'FILE_DELETE', 'SYSTEM_ACCESS', 'NETWORK_REQUEST', 'PRIVILEGE_ESCALATION', 'USB_DEVICE', 'EMAIL_SENT', 'DATABASE_QUERY', 'CONFIG_CHANGE', 'FAILED_AUTH', name='eventtypeenum'), nullable=True),
        sa.Column('resource_accessed', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('is_anomalous', sa.Boolean(), nullable=True),
        sa.Column('flag_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severityenum'), nullable=True),
        sa.Column('alert_type', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('triggered_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged', sa.Boolean(), nullable=True),
        sa.Column('acknowledged_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('activity_log_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['activity_log_id'], ['activity_logs.id'], ),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('alerts')
    op.drop_table('activity_logs')
    op.drop_table('user_baselines')
    op.drop_index(op.f('ix_ml_models_model_name'), table_name='ml_models')
    op.drop_table('ml_models')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
