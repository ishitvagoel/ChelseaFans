from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "raw_snapshots",
        sa.Column("key", sa.String(255), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("stored_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "players",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("position", sa.String(64), nullable=True),
        sa.Column("nationality", sa.String(64), nullable=True),
        sa.Column("shirt_number", sa.Integer(), nullable=True),
    )
    op.create_table(
        "matches",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("kickoff", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "external_ids",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("external_id", sa.String(128), nullable=False),
        sa.Column("internal_id", sa.String(64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.UniqueConstraint("provider", "entity_type", "external_id"),
    )


def downgrade() -> None:
    op.drop_table("external_ids")
    op.drop_table("matches")
    op.drop_table("players")
    op.drop_table("raw_snapshots")
