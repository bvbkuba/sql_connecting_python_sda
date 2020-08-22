from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy import text, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, aliased, relationship
from sqlalchemy.sql import exists

engine = create_engine("sqlite:///:memory:", echo=True)   # tworzymy silnik, connection string odpowiada za połączenie z baża danych, echo=True za logi
# w connection stirngu mogłoby być nawet ip adress
Base = declarative_base()   #deklarowanie bazowej klasy, po której będziemy dziedziczyć maping tabeli
Session = sessionmaker(bind=engine) #deklarowanie sesji i połaczenie z silnikiem
session = Session()  # obiekt sesji, aby nie uruchamiać kilku sesji, tylko pracoeać na jednej sesji


class User(Base):  # klasa User dziedziczy po declarative_base() - zawiera schemat tabeli
    __tablename__ = "users"  #nazwa tabeli

    id = Column(Integer, primary_key=True) #kolumny 1-4. Istotne jest, że musimy importować Column oraz Integer i String z sqlalchemy, inaczej będą błędy
    name = Column(String)
    # name = Column(String(50), nullable = False)  # można dać ile liter może mieć tekst oraz i czy może być przyjęta  wartość null
    fullname = Column(String)
    nickname = Column(String)

    def __repr__(self):
        return f"<User(name={self.name}, fullname={self.fullname}, nickname={self.nickname})>"

class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='addresses')

    def __repr__(self):
        return f'Address(email_address={self.email_address})'

User.addresses = relationship(            #określamy relację i dodajemy atrybut do klasy
    'Address', order_by=Address.id, back_populates='user'
)


# relacje dajemy przed mappingiem

"""Kolejna dyrektywa – relationship służy, jak sama nazwa wskazuje, do ustawienia informacji o
relacji. Informuje ORM, że klasa Address powinna zostać połączona z klasą User
wykorzystując atrybut Address.user. relationship() korzysta z połączeń klucz obcy-klucz
 główny, aby domyślić się o jaki typ relacji chodzi (wiele do jednego).
Base.metadata.create_all(engine)  # łączy mappingi z sesją"""

Base.metadata.create_all(engine)  #tworzymy mapowanie

USERS_DATA = (
    {"name": "Robert", "fullname": "Robert De Niro", "nickname": "Bobby"},
    {"name": "Bob", "fullname": "Dylan", "nickname": "Singer"},
    {"name": "Bob", "fullname": "Marley", "nickname": "Singer as well"},
)

def create_users_bulk(data):
    return [User(**user) for user in data]


#uzyskamy listę obiektów: [<User(name='Robert', fullname='Robert De Niro', nickname='Bobby')>,
# <User(name='Bob', fullname='Dylan', nickname='Singer')>,
# <User(name='Bob', fullname='Marley', nickname='Singer as well')>]

def add_users_to_db():
    session.add_all(create_users_bulk(USERS_DATA))  #podajemy w postaci listy obiekty które chcemy dodać do sesji (do add_all)
    session.commit()
add_users_to_db()

print(session.query(User).all())   # wyprintowanie wszystkich userow w sesji

print('*'*50, 'Next_part', '*'*50)

#label sluzy jako alias w sql
for user in session.query(User.id,User.nickname.label('new_name')):
    print(user.id,user.new_name)  # zadziała
    # print(user.id,user.nickname)  # obiekt nie ma atrybutu nickname bo zmieniliśmy go na new_name - będzie błąd
    # print(User.id,User.nickname)   # jest ok, bo zmieniliśmy nickname na new_name dla usera w pętli for, a nie w klasie User.
    # print(User.id,User.new_name)  # wyrzuci błąd, bo klasa User nie ma atrybutu new_name, ma nickname. Zmieniony jest tylko dla usera w petli(lub funkcji)

banned_users = aliased(User,name = 'banned_user')   #alt + enter pozwala importować od razu

for user in session.query(banned_users.nickname.label('alter')):   #do nazwania tabeli tak jakby kopii aby móc pracować
    #przykładowo chcemy pracować na 2 tych samych kolumnach tej samej tabeli to tworzymy label i na nim działamy
    print(user.alter)


test_user = session.query(User).filter(text('id=:id')).params(id = 1).all()   #Jeżeli chcemy do zapytania przekazać zmienne musimy je oznaczyć z użyciem dwukropka
print(test_user)

print('******************************************','hereeeeee')

sql_statement = text("SELECT * FROM users WHERE name = :name")  # przypisujemy do name kolumne name
user = session.query(User).from_statement(sql_statement).params(name='Bob').all()
print(user)

print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

sql_statement = text("SELECT * FROM users WHERE id = :id")
user = session.query(User).from_statement(sql_statement).params(id=1).all()
print(user)
#działa




"""Dopasowanie kolumn działa w prostych przypadkach, jednak może się okazać problematyczne w
bardziej zaawansowanych instrukcjach np. gdy nazwy kolumn są zduplikowane (zapytania gdzie są
JOIN’y).
W takich przypadkach, gdy ORM sobie nie radzi możemy ręcznie wskazać kolumny, z których
chcemy wyciągnąć dane."""

query = "SELECT id, fullname, nickname FROM users where id=:id"
statement = text(query)
statement = statement.columns(User.id, User.fullname, User.nickname)



q = session.query(User).from_statement(statement).params(id=1).all()
for user in q:
    print(user)


#zliczanie osób - zrobi podzapytanie
count_users = session.query(User).count()
print(count_users)
 #zliczanie osób - szybsze - nie robi podzapytania. Dodatkowo z sql alchemy importujemy func, która pozwala potem zrobić np. func.count
session.query(func.count("*")).select_from(User).scalar()



#funkcja zliczająca ilość osób o imieniach podobnych
print(session.query(func.count(User.name), User.name).group_by(User.name).all())



print('*'*50)

jack = User(name = 'Jack', fullname = 'Aka', nickname = 'jc123')
print(jack.addresses)

jack.adresses = [Address(email_address = 'email@email.com')]
print(jack.adresses[0].user)


# w pętli nie wyświetli jacka, musimy go najpierw dodać i dać commit (jak w git)
for user in session.query(User).all():
    print(user)


print('*'*50, 'Teraz dodanie jacka i będzie wyswietlony w petli', '*'*50)
session.add(jack)
session.commit()

for user in session.query(User).all():
    print(user)

"""Możemy chcieć połączyć dane z kilku tabel
Select *
From users
Join addresses
On users.id = addresses.user_id

ale lepiej zrobic to tak: 
session.query(User).join(Address).all()
"""


adalias1 = aliased(Address)
adalias2 = aliased(Address)
result = session.query(User.name,adalias1.email_address,adalias2.email_address,).join(adalias1, User.addresses).join(adalias2, User.addresses).filter(adalias1.email_address=='jack@gmail.com').filter(adalias2.email_address=='j25@yahoo.com')
for username, email1, email2 in result:
    print(username, email1, email2)


"""Załóżmy, że chcemy wczytać użytkowników wraz z informacją ile
rekordów adresów ma każdy z nich.
Jak to zrobić korzystając z mechanizmów SQLAlchemy?

Najlepszym sposobem na otrzymanie interesującego nas wyniku jest pogrupowanie
adresów po id użytkownika, a następnie korzystając z JOIN’a dołączyć
użytkownika.
W tym wypadku możemy użyć LEFT OUTER JOIN, aby uzyskać informacje,
także o użytkownikach, którzy nie mają żadnego adresu.


W sql:
SELECT
    users.id,
    users.nickname,
    addr_count.addr_count
FROM users
LEFT OUTER JOIN (
    SELECT
        user_id,
        count(*) AS addr_count
    FROM addresses
    GROUP BY user_id
) AS addr_count ON users.id = addr_count.user_id
"""

#podzapytanie
stmt = session.query(Address.user_id,func.count('*').label('address_count')).group_by(Address.user_id).subquery()
print(stmt)

"""Teraz, mając przygotowane podzapytanie zostało tylko połączyć go z głównym
zapytaniem.
Kolumny podzapytania są dostępne poprzez atrybut c."""

q= session.query(User, stmt.c.address_count).outerjoin(stmt, User.id == stmt.c.user_id).group_by(User.id).all()
print('xxxxxx', q)


"""Wcześniej wynik naszego zapytania zwrócił nam w ramach podzapytania jedną kolumnę - “count".
Co gdybyśmy chcieli wyciągnąć całą encję?
W tym celu musimy skorzystać z funkcji aliased(), aby połączyć alias z mapowaną klasą z
podzapytania."""
stmt = session.query(Address).subquery()
addr_alias = aliased(Address,stmt)
q= session.query(User,addr_alias).join(addr_alias, User.addresses).all()
print('yyyy',q)

#exists - importowany z sqlalchemy.sql

from sqlalchemy.sql import exists
stmt = exists().where(Address.user_id==User.id)
print(session.query(User.name).filter(stmt).all())
"""
INFO sqlalchemy.engine.base.Engine SELECT users.name AS users_name 
FROM users 
WHERE EXISTS (SELECT * 
FROM addresses 
WHERE addresses.user_id = users.id)
"""
query = session.query(User)
q = query.filter(User.addresses.any()).all()
q = query.filter(User.addresses.any(Address.email_address.ilike("ab%"))).all()
q = session.query(Address).filter(Address.user.has(User.name=='Jack')).all()
print(q)


"""Wcześniej, gdy pobieraliśmy adresy użytkownika zauważyliśmy, że najpierw utworzone
zostało jedno zapytanie, które pobrało użytkownika, potem, na żądanie zostały dla niego
ściągnięte adresy.
Czasami chcemy zmniejszyć liczbę zapytań – wolimy jedno duże zamiast kilku mniejszych.
By to osiągnąć możemy włączyć eager loading.
SQLAlchemy pozwala uruchomić eager loading na trzy sposoby – dwa automatyczne,
jeden manualny pozwalający optymalizować pobieranie"""

"""Ładowanie selektywne polega na wskazaniu pola relacji addresses metodzie orm.selectinload(), która
wygeneruje jednorazowo dwa zapytania – pierwsze do pobrania użytkownika, drugie do pobrania jego
adresów."""

from sqlalchemy.orm import selectinload
jack = session.query(User).options(
selectinload(User.addresses)).filter_by(name='Jack').one()


"""Ostatni sposób to połączenie operacji JOIN oraz eagear loading.
Takie podejście stosujemy kiedy chcemy wyciągnąć obiekt z relacji wielu do jeden, który musi
być wielokrotnie odfiltrowany.
"""
from sqlalchemy.orm import contains_eager
session.query(Address) \
.join(Address.user) \
.filter(User.name=='Jack') \
.options(contains_eager(Address.user)) \
.all()

# usuwanie
"""Jeżeli przeanalizujemy poprzednie zapytanie usuwające zauważymy, że rekordy z tabeli
“addresses” nadal są w bazie danych, a kolumna user_id jest ustawiona na None.
Domyślnie SQLAlchemy nie używa kaskady przy usuwaniu.
Jeśli chcemy zmienić domyślne zachowanie, to musimy jawnie wskazać opcję usuwania
kaskadowego.

User.addresses = relationship(
'Address', back_populates='user',
cascade='all, delete, delete-orphan')
"""