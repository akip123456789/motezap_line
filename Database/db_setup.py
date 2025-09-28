import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .base import Base
from .Models.Posted import Posted
from .Models.BlockUser import BlockUser
load_dotenv()

db_password=os.getenv("DB_PASSWORD")
db_user=os.getenv("DB_USERNAME")
db_server=os.getenv("DB_SERVER")
db_name=os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql://{db_user}:{db_password}@{db_server}/{db_name}",
    # 接続プールの設定
    pool_size=20,  # 基本接続プールサイズ
    max_overflow=30,  # 追加接続数
    pool_timeout=30,  # 接続取得のタイムアウト
    pool_recycle=3600,  # 接続の再利用時間（1時間）
    pool_pre_ping=True,  # 接続前のpingチェック
    # SSL設定
    connect_args={
        "sslmode": "prefer",  # SSL接続を優先するが、失敗した場合は非SSL接続を試行
        "connect_timeout": 10,  # 接続タイムアウト
        "application_name": "motezap_line"
    }
)

DB_Session=sessionmaker(autocommit=False, autoflush=False, bind=engine)


if __name__=="__main__":
    Base.metadata.create_all(bind=engine)
    print("テーブルが作成されました")

# python -m Database.db_setup