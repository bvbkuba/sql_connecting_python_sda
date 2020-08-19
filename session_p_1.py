from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
engine = create_engine("sqlite:///:memory:", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    def __repr__(self):
        return f"<User(name={self.name}, fullname={self.fullname}, nickname={self.nickname})>"
    
Base.metadata.create_all(engine)
USERS_DATA = (
    {"name": "'Robert'", "fullname": "'Robert De Niro'", "nickname": "'Bobby'"},
    {"name": "'Bob'", "fullname": "'Dylan'", "nickname": "'Singer'"},
    {"name": "'Bob'", "fullname": "'Marley'", "nickname": "'Singer as well'"},
)
def create_users_bulk(data):
    return [User(**user) for user in data]

def add_users_to_db():
    session.add_all(create_users_bulk(USERS_DATA))
    session.commit()
    
add_users_to_db()

for user