"""Initial schema with all models

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-03-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types - using DROP CASCADE to avoid conflicts
    op.execute("DROP TYPE IF EXISTS userrole CASCADE;")
    op.execute("CREATE TYPE userrole AS ENUM ('farmer', 'agent', 'admin');")
    
    op.execute("DROP TYPE IF EXISTS growthstage CASCADE;")
    op.execute("CREATE TYPE growthstage AS ENUM ('seedling', 'vegetative', 'flowering', 'fruiting', 'maturation');")
    
    op.execute("DROP TYPE IF EXISTS notificationtype CASCADE;")
    op.execute("CREATE TYPE notificationtype AS ENUM ('disease_alert', 'advisory', 'price_alert', 'irrigation_reminder', 'system_alert');")
    
    op.execute("DROP TYPE IF EXISTS notificationchannel CASCADE;")
    op.execute("CREATE TYPE notificationchannel AS ENUM ('email', 'sms', 'in_app', 'push');")
    
    op.execute("DROP TYPE IF EXISTS notificationstatus CASCADE;")
    op.execute("CREATE TYPE notificationstatus AS ENUM ('pending', 'sent', 'failed', 'read');")
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=15), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('district', sa.String(length=50), nullable=True),
        sa.Column('role', postgresql.ENUM('farmer', 'agent', 'admin', name='userrole', create_type=False), nullable=False, server_default='farmer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # Create farms table
    op.create_table('farms',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('crop_type', sa.String(length=50), nullable=False),
        sa.Column('area_hectares', sa.Float(), nullable=False),
        sa.Column('soil_type', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['farmer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_farms_farmer_id'), 'farms', ['farmer_id'], unique=False)
    op.create_index(op.f('ix_farms_id'), 'farms', ['id'], unique=False)
    
    # Create uploads table
    op.create_table('uploads',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farm_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('image_path', sa.String(length=255), nullable=False),
        sa.Column('image_filename', sa.String(length=255), nullable=False),
        sa.Column('disease_detected', sa.String(length=100), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('crop', sa.String(length=50), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id']),
        sa.ForeignKeyConstraint(['farmer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_uploads_farmer_id'), 'uploads', ['farmer_id'], unique=False)
    op.create_index(op.f('ix_uploads_id'), 'uploads', ['id'], unique=False)
    op.create_index(op.f('ix_uploads_uploaded_at'), 'uploads', ['uploaded_at'], unique=False)
    
    # Create advisories table
    op.create_table('advisories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('upload_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('disease', sa.String(length=100), nullable=False),
        sa.Column('crop', sa.String(length=50), nullable=False),
        sa.Column('treatment', sa.Text(), nullable=False),
        sa.Column('organic_alternative', sa.Text(), nullable=True),
        sa.Column('prevention', postgresql.JSON(), nullable=True),
        sa.Column('fertilizer', sa.String(length=255), nullable=True),
        sa.Column('pesticide', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('model_name', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['upload_id'], ['uploads.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('upload_id', name='uq_advisory_upload_id')
    )
    op.create_index(op.f('ix_advisories_id'), 'advisories', ['id'], unique=False)
    op.create_index(op.f('ix_advisories_upload_id'), 'advisories', ['upload_id'], unique=True)
    
    # Create irrigation_logs table
    op.create_table('irrigation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farm_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crop', sa.String(length=50), nullable=False),
        sa.Column('growth_stage', postgresql.ENUM('seedling', 'vegetative', 'flowering', 'fruiting', 'maturation', name='growthstage', create_type=False), nullable=False),
        sa.Column('soil_moisture', sa.Float(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('rainfall', sa.Float(), nullable=True),
        sa.Column('water_qty_liters_per_hectare', sa.Float(), nullable=False),
        sa.Column('frequency_days', sa.Float(), nullable=True),
        sa.Column('irrigation_method', sa.String(length=50), nullable=True),
        sa.Column('recommended_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('is_applied', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_irrigation_logs_farm_id'), 'irrigation_logs', ['farm_id'], unique=False)
    op.create_index(op.f('ix_irrigation_logs_id'), 'irrigation_logs', ['id'], unique=False)
    op.create_index(op.f('ix_irrigation_logs_recommended_at'), 'irrigation_logs', ['recommended_at'], unique=False)
    
    # Create market_prices table
    op.create_table('market_prices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crop', sa.String(length=50), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('mandi', sa.String(length=100), nullable=False),
        sa.Column('price_per_quintal', sa.Float(), nullable=False),
        sa.Column('price_per_kg', sa.Float(), nullable=True),
        sa.Column('min_price', sa.Float(), nullable=True),
        sa.Column('max_price', sa.Float(), nullable=True),
        sa.Column('price_date', sa.DateTime(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_prices_crop'), 'market_prices', ['crop'], unique=False)
    op.create_index(op.f('ix_market_prices_id'), 'market_prices', ['id'], unique=False)
    op.create_index(op.f('ix_market_prices_price_date'), 'market_prices', ['price_date'], unique=False)
    op.create_index(op.f('ix_market_prices_state'), 'market_prices', ['state'], unique=False)
    
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_type', postgresql.ENUM('disease_alert', 'advisory', 'price_alert', 'irrigation_reminder', 'system_alert', name='notificationtype', create_type=False), nullable=False),
        sa.Column('channel', postgresql.ENUM('email', 'sms', 'in_app', 'push', name='notificationchannel', create_type=False), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'sent', 'failed', 'read', name='notificationstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('retry_count', sa.String(), nullable=True, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['farmer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_farmer_id'), 'notifications', ['farmer_id'], unique=False)
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_status'), 'notifications', ['status'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_notifications_status'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_farmer_id'), table_name='notifications')
    op.drop_table('notifications')
    
    op.drop_index(op.f('ix_market_prices_state'), table_name='market_prices')
    op.drop_index(op.f('ix_market_prices_price_date'), table_name='market_prices')
    op.drop_index(op.f('ix_market_prices_id'), table_name='market_prices')
    op.drop_index(op.f('ix_market_prices_crop'), table_name='market_prices')
    op.drop_table('market_prices')
    
    op.drop_index(op.f('ix_irrigation_logs_recommended_at'), table_name='irrigation_logs')
    op.drop_index(op.f('ix_irrigation_logs_id'), table_name='irrigation_logs')
    op.drop_index(op.f('ix_irrigation_logs_farm_id'), table_name='irrigation_logs')
    op.drop_table('irrigation_logs')
    
    op.drop_index(op.f('ix_advisories_upload_id'), table_name='advisories')
    op.drop_index(op.f('ix_advisories_id'), table_name='advisories')
    op.drop_table('advisories')
    
    op.drop_index(op.f('ix_uploads_uploaded_at'), table_name='uploads')
    op.drop_index(op.f('ix_uploads_id'), table_name='uploads')
    op.drop_index(op.f('ix_uploads_farmer_id'), table_name='uploads')
    op.drop_table('uploads')
    
    op.drop_index(op.f('ix_farms_id'), table_name='farms')
    op.drop_index(op.f('ix_farms_farmer_id'), table_name='farms')
    op.drop_table('farms')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_table('users')
