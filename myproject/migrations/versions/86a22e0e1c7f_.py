"""empty message

Revision ID: 86a22e0e1c7f
Revises: a6ac4e0b4bb8
Create Date: 2023-07-29 12:13:15.019757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86a22e0e1c7f'
down_revision = 'a6ac4e0b4bb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(batch_op.f('fk_question_user_id'), 'user', ['user_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_question_user_id'), type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###