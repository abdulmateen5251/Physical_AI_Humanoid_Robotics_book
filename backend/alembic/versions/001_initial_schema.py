"""Initial schema: users, user_profiles, answer_sessions, translations

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-06 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    
    # Users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    
    # User profiles table
    op.create_table(
        'user_profiles',
        sa.Column('profile_id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('background', sa.String(50), nullable=False, server_default='beginner'),
        sa.Column('difficulty_level', sa.String(50), nullable=False, server_default='beginner'),
        sa.Column('examples_preference', sa.String(50), nullable=False, server_default='moderate'),
        sa.Column('preferred_language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('consent_personalization', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('consent_data_collection', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    )
    op.create_index('idx_user_profiles_user_id', 'user_profiles', ['user_id'])
    
    # Answer sessions table
    op.create_table(
        'answer_sessions',
        sa.Column('session_id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('question', sa.Text, nullable=False),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('scope', sa.String(50), nullable=False),
        sa.Column('selected_text', sa.Text, nullable=True),
        sa.Column('chunk_ids', sa.JSON, nullable=False),
        sa.Column('retrieval_score_avg', sa.Float, nullable=True),
        sa.Column('llm_model', sa.String(100), nullable=False),
        sa.Column('feedback_rating', sa.Integer, nullable=True),
        sa.Column('feedback_comment', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('response_time_ms', sa.Integer, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_answer_sessions_user_id', 'answer_sessions', ['user_id'])
    op.create_index('idx_answer_sessions_created_at', 'answer_sessions', ['created_at'])
    
    # Translations table
    op.create_table(
        'translations',
        sa.Column('translation_id', sa.String(36), primary_key=True),
        sa.Column('chapter_id', sa.String(255), nullable=False),
        sa.Column('target_lang', sa.String(10), nullable=False),
        sa.Column('original_content', sa.Text, nullable=False),
        sa.Column('translated_content', sa.Text, nullable=False),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('llm_model', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('cached', sa.Boolean, nullable=False, server_default='true'),
    )
    op.create_index('idx_translations_chapter_lang', 'translations', ['chapter_id', 'target_lang'], unique=True)
    
    # Personalized content cache table
    op.create_table(
        'personalized_content',
        sa.Column('content_id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('chapter_id', sa.String(255), nullable=False),
        sa.Column('background', sa.String(50), nullable=False),
        sa.Column('difficulty_level', sa.String(50), nullable=False),
        sa.Column('examples_preference', sa.String(50), nullable=False),
        sa.Column('original_content', sa.Text, nullable=False),
        sa.Column('personalized_content', sa.Text, nullable=False),
        sa.Column('llm_model', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    )
    op.create_index('idx_personalized_content_user_chapter', 'personalized_content', ['user_id', 'chapter_id'])
    op.create_index('idx_personalized_content_expires_at', 'personalized_content', ['expires_at'])


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_table('personalized_content')
    op.drop_table('translations')
    op.drop_table('answer_sessions')
    op.drop_table('user_profiles')
    op.drop_table('users')
