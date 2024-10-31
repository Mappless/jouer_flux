from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///db.sqlite3")
Session = sessionmaker(engine, expire_on_commit=False)
