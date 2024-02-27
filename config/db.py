#Esta clase sirve para conectarse a la base de datos que corre en el localhost
from sqlalchemy import create_engine, MetaData

engine = create_engine("mysql+mysqlconnector://root:****@127.0.0.1:3306/users")

meta = MetaData()

conn = engine.connect()
