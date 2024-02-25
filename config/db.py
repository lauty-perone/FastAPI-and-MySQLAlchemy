from sqlalchemy import create_engine, MetaData

DATABASE_URL = "mysql+pymysql://root:secret@localhost:3306/storedb"

engine = create_engine(DATABASE_URL)

meta = MetaData()

conn = engine.connect()
