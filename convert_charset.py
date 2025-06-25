from alembic import op
import sqlalchemy as sa

def upgrade():
    # 为所有表修改字符集
    op.execute("ALTER TABLE `user` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    op.execute("ALTER TABLE `email_captcha` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    op.execute("ALTER TABLE `intelligence` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")