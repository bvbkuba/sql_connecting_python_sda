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
Base.metadata.create_all(engine)
ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
session.add(ed_user)

USERS_DATA = (
    {"name": "'Robert'", "fullname": "'Robert De Niro'", "nickname": "'Bobby'"},
    {"name": "'Bob'", "fullname": "'Zylan'", "nickname": "'Singer'"},
    {"name": "'Bob'", "fullname": "'Marley'", "nickname": "'Singer as well'"},
)
def create_users_bulk(data):
    return [User(**user) for user in data]



def add_users_to_db():
    session.add_all(create_users_bulk(USERS_DATA))
    # for i in (create_users_bulk(USERS_DATA)):  #to samo co powyższa linijka
    #     session.add(i)
    # session.commit()   #zatwierdzenie spowoduje, że wszyscy z sesji, także ed_user zostaną dodani do bazy danych


add_users_to_db()


print('*'*60)
print(engine.execute('select * from users').fetchall())


query = session.query(User)  # przypisujemy sesje qeury do zmiennej query - czytelniej i wygodniej
print(f"{'*'*70} Query {'*'*70}")

# print(query.all())    #wyswietl wszystkich
# print(query.first())
# print(query.one())  #daje błąd jeśli jest jest więcej niż 1 user: MultipleResultsFound, dla 1 usera zwraca poprawny wynik, dla braku wierszy daje: 'NoResultFound: No row was found for one()'
#query.one() jest tylko dla query posiadającego 1 wiersz.

# print(query.scalar())  # zwraca None jeśli nie ma żadnego wiersza w bazie. MultipleResultFound gdy jest kilka userow.


# ed_user.name = 'Jako'
# session.commit()   #dajac commit session.dirty zwroci pusta liste. Bez tego pokaze ed_usera, bo dirty tworzy liste modyfikowanych obiektow od ostatniego commita
# print(session.dirty)


for user in query.order_by(User.name,User.fullname):   #sortowanie według name, fullname
    print(user)

for user in query.filter(User.id == 2):   #filtrowanie
    print(user)


for user in query.filter_by(id = 1):   #filtrowanie inne
    print(user)


print(f"{'*'*30} Przykłady rollback i new{'*'*30}")
print(session.new)  #coś jak git status
session.rollback()  # cos jak git reset
print(session.new)


