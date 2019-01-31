"""add key-vaue table store

Revision ID: 78514b173380
Revises: 312e762dfa85
Create Date: 2019-01-21 21:59:34.979693

"""
from alembic import op
import sqlalchemy as sa

from busy_beaver import twitter
from busy_beaver.models import kv_store
from busy_beaver.retweeter import LAST_TWEET_KEY

# revision identifiers, used by Alembic.
revision = "78514b173380"
down_revision = "312e762dfa85"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "kv_store",
        sa.Column("key", sa.String(length=250), nullable=False),
        sa.Column("value", sa.LargeBinary(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )
    # ### end Alembic commands ###

    # initialize datastore with value of last tweet
    try:
        last_id = twitter.get_last_tweet_id()
    except Exception:  # NOT a fan, but it makes migration in prod easier
        last_id = 42
    kv_store.put_int(LAST_TWEET_KEY, last_id)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("kv_store")
    # ### end Alembic commands ###