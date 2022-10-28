from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from custom_session import M_scoped_session



engine = create_engine('sqlite:///database.db', echo=False)
Session_factory = sessionmaker(bind=engine)
Session = M_scoped_session(Session_factory)

with Session as session:
    #session.query()
    pass