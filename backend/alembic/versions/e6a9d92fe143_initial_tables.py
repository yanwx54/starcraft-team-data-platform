"""initial tables

Revision ID: e6a9d92fe143
Revises:
Create Date: 2026-06-14 17:06:52.998779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6a9d92fe143'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. 原始文章表
    op.create_table(
        'raw_articles',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wr_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('article_date', sa.Date(), nullable=True),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('parsed_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wr_id'),
    )
    op.create_index('idx_raw_articles_wr_id', 'raw_articles', ['wr_id'])
    op.create_index('idx_raw_articles_date', 'raw_articles', ['article_date'])

    # 2. 赛季表
    op.create_table(
        'seasons',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('season_name', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('season_name'),
    )

    # 3. 地图表
    op.create_table(
        'maps',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('map_uid', sa.String(length=50), nullable=False),
        sa.Column('kr_name', sa.String(length=200), nullable=True),
        sa.Column('en_name', sa.String(length=200), nullable=True),
        sa.Column('cn_name', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('map_uid'),
    )

    # 4. 赛季地图池
    op.create_table(
        'season_maps',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('season_id', sa.BigInteger(), nullable=False),
        sa.Column('map_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], name='fk_season_maps_season'),
        sa.ForeignKeyConstraint(['map_id'], ['maps.id'], name='fk_season_maps_map'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('season_id', 'map_id', name='uq_season_map'),
    )

    # 5. 队伍表
    op.create_table(
        'teams',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('team_uid', sa.String(length=50), nullable=False),
        sa.Column('team_name', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_uid'),
    )

    # 6. 选手表
    op.create_table(
        'players',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('player_uid', sa.String(length=50), nullable=False),
        sa.Column('kr_name', sa.String(length=200), nullable=True),
        sa.Column('game_id', sa.String(length=200), nullable=True),
        sa.Column('cn_name', sa.String(length=200), nullable=True),
        sa.Column('race', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_uid'),
    )

    # 7. 选手别名表
    op.create_table(
        'player_aliases',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('player_id', sa.BigInteger(), nullable=False),
        sa.Column('alias_name', sa.String(length=200), nullable=False),
        sa.Column('alias_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], name='fk_alias_player'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 8. 转队历史表
    op.create_table(
        'player_team_history',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('player_id', sa.BigInteger(), nullable=False),
        sa.Column('team_id', sa.BigInteger(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], name='fk_pth_player'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='fk_pth_team'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 9. 团战主表
    op.create_table(
        'matches',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wr_id', sa.BigInteger(), nullable=False),
        sa.Column('season_id', sa.BigInteger(), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('match_date', sa.Date(), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('team_a_id', sa.BigInteger(), nullable=True),
        sa.Column('team_b_id', sa.BigInteger(), nullable=True),
        sa.Column('winner_team_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], name='fk_match_season'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wr_id'),
    )

    # 10. 团战阶段表
    op.create_table(
        'match_stages',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.BigInteger(), nullable=False),
        sa.Column('stage_type', sa.String(length=20), nullable=False),
        sa.Column('stage_order', sa.Integer(), nullable=False),
        sa.Column('winner_team_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name='fk_stage_match'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 11. 对局明细表
    op.create_table(
        'match_details',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.BigInteger(), nullable=False),
        sa.Column('stage_id', sa.BigInteger(), nullable=True),
        sa.Column('game_no', sa.Integer(), nullable=True),
        sa.Column('map_id', sa.BigInteger(), nullable=True),
        sa.Column('player_a_id', sa.BigInteger(), nullable=False),
        sa.Column('player_b_id', sa.BigInteger(), nullable=False),
        sa.Column('winner_player_id', sa.BigInteger(), nullable=False),
        sa.Column('loser_player_id', sa.BigInteger(), nullable=False),
        sa.Column('score_a', sa.Integer(), server_default='1', nullable=True),
        sa.Column('score_b', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name='fk_md_match'),
        sa.ForeignKeyConstraint(['stage_id'], ['match_stages.id'], name='fk_md_stage'),
        sa.ForeignKeyConstraint(['map_id'], ['maps.id'], name='fk_md_map'),
        sa.ForeignKeyConstraint(['player_a_id'], ['players.id']),
        sa.ForeignKeyConstraint(['player_b_id'], ['players.id']),
        sa.ForeignKeyConstraint(['winner_player_id'], ['players.id']),
        sa.ForeignKeyConstraint(['loser_player_id'], ['players.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_match_details_match', 'match_details', ['match_id'])
    op.create_index('idx_match_details_player_a', 'match_details', ['player_a_id'])
    op.create_index('idx_match_details_player_b', 'match_details', ['player_b_id'])
    op.create_index('idx_match_details_winner', 'match_details', ['winner_player_id'])

    # 12. 奖金表
    op.create_table(
        'prize_pool',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.BigInteger(), nullable=False),
        sa.Column('player_id', sa.BigInteger(), nullable=False),
        sa.Column('prize_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name='fk_prize_match'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], name='fk_prize_player'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 13. 采集日志
    op.create_table(
        'crawl_log',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wr_id', sa.BigInteger(), nullable=True),
        sa.Column('log_level', sa.String(length=20), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
    )

    # 14. 数据异常中心
    op.create_table(
        'data_issues',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('issue_type', sa.String(length=50), nullable=True),
        sa.Column('source_table', sa.String(length=100), nullable=True),
        sa.Column('source_id', sa.BigInteger(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='open', nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
    )

    # 15. 翻译规则表
    op.create_table(
        'translation_rules',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('rule_type', sa.String(length=20), nullable=False),
        sa.Column('source_text', sa.String(length=255), nullable=False),
        sa.Column('translated_text', sa.String(length=255), nullable=False),
        sa.Column('alias_group', sa.String(length=255), nullable=True),
        sa.Column('priority', sa.Integer(), server_default='1', nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rule_type', 'source_text', name='uq_translation_rules_rule_type_source_text'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('translation_rules')
    op.drop_table('data_issues')
    op.drop_table('crawl_log')
    op.drop_table('prize_pool')
    op.drop_index('idx_match_details_winner', table_name='match_details')
    op.drop_index('idx_match_details_player_b', table_name='match_details')
    op.drop_index('idx_match_details_player_a', table_name='match_details')
    op.drop_index('idx_match_details_match', table_name='match_details')
    op.drop_table('match_details')
    op.drop_table('match_stages')
    op.drop_table('matches')
    op.drop_table('player_team_history')
    op.drop_table('player_aliases')
    op.drop_table('players')
    op.drop_table('teams')
    op.drop_table('season_maps')
    op.drop_table('maps')
    op.drop_table('seasons')
    op.drop_index('idx_raw_articles_date', table_name='raw_articles')
    op.drop_index('idx_raw_articles_wr_id', table_name='raw_articles')
    op.drop_table('raw_articles')
