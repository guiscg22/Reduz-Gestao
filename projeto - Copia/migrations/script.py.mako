"""
Revision ID: ${up_revision}
Revises: ${down_revision | none}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa

${message}

def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
