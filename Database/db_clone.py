from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database.base import Base
from .Models.Posted import Posted
from .Models.BlockUser import BlockUser
from .Models.BookingCheck import Bookingcheck

# 元のDB
source_engine = create_engine(
    "postgresql://akihiro:FQMZK2ypMFSkldhD7xzp3kzji4lBGwCU@dpg-d2mjho0gjchc73cnd0p0-a.oregon-postgres.render.com/share_db_r2if"
)
SourceSession = sessionmaker(bind=source_engine)
source_session = SourceSession()

# コピー先のDB
dest_engine = create_engine(
    "postgresql://gong_you_detabesu_user:O1gvc02u89jIkvjF3gxLNYzHO588p7ae@dpg-d3r6i6mr433s73e7do5g-a.oregon-postgres.render.com/gong_you_detabesu"
)
DestSession = sessionmaker(bind=dest_engine)
dest_session = DestSession()

# テーブル構造をコピー先に作成
Base.metadata.create_all(bind=dest_engine)


def copy_table(model):
    rows = source_session.query(model).all()
    for row in rows:
        data = row.__dict__.copy()
        data.pop("_sa_instance_state", None)
        dest_session.add(model(**data))
    dest_session.commit()
    print(f"{model.__tablename__}: {len(rows)} 件コピー完了")


if __name__ == "__main__":
    # 外部キー依存関係に基づいてテーブルをソート
    sorted_tables = Base.metadata.sorted_tables
    print("コピー順:")
    for t in sorted_tables:
        print(f" - {t.name}")

    # SQLAlchemyのTableオブジェクトから対応するモデルを探す辞書を作る
    name_to_model = {
        cls.__tablename__: cls
        for cls in [Posted, BlockUser, Bookingcheck]
    }

    # 外部キー依存関係順にコピー実行
    for table in sorted_tables:
        model = name_to_model.get(table.name)
        if model:
            copy_table(model)

    source_session.close()
    dest_session.close()

#python -m Database.db_clone