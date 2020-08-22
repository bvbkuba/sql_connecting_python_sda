from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy import text, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, aliased, relationship
from sqlalchemy.sql import exists

engine = create_engine("sqlite:///:memory:", echo=True)   # tworzymy silnik, connection string odpowiada za połączenie z baża danych, echo=True za logi
# w connection stirngu mogłoby być nawet ip adress
Base = declarative_base()   #deklarowanie bazowej klasy, po której będziemy dziedziczyć maping tabeli

class User(Base):  # klasa User dziedziczy po declarative_base() - zawiera schemat tabeli
    __tablename__ = "users"  #nazwa tabeli, w sql odpowiadałby za

    id = Column(Integer, primary_key=True) #kolumny 1-4. Istotne jest, że musimy importować Column oraz Integer i String z sqlalchemy, inaczej będą błędy
    name = Column(String(40))
    # name = Column(String(50), nullable = False)  # można dać ile liter może mieć tekst oraz i czy może być przyjęta  wartość null
    fullname = Column(String(50))
    nickname = Column(String(40))

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

# User.addresses = relationship(            #określamy relację i dodajemy atrybut do klasy
#     'Address', order_by=Address.id, back_populates='user'
# )
User.addresses = relationship(            #określamy relację i dodajemy atrybut do klasy
    'Address', order_by=Address.id, back_populates='user', cascade = 'all,delete,delete-orphan'  #delete-orphan - w relacji 1-1 usuwa te, które nie maja rodzica, matki itp
)

# # uselist = False w relationship oznacza, że jest to 1-1: link : https://gist.github.com/adam-harmasz/7c30ce06a04e8e70cabf120e3657c537

# relacje dajemy przed mappingiem

"""Kolejna dyrektywa – relationship służy, jak sama nazwa wskazuje, do ustawienia informacji o
relacji. Informuje ORM, że klasa Address powinna zostać połączona z klasą User
wykorzystując atrybut Address.user. relationship() korzysta z połączeń klucz obcy-klucz
 główny, aby domyślić się o jaki typ relacji chodzi (wiele do jednego).
Base.metadata.create_all(engine)  # łączy mappingi z sesją"""


#gdy mamy zadeklarowaną bazę to jak dodamy wywołanie metody create.all to "bindujemy" silnik, któ twory tabele.
#po wywołaniu tej metody poswstanie tabela
Base.metadata.create_all(engine)  #tworzymy mapowanie.
def create_tables():  #funkcja na base.metadate.create_all(engine)
    Base.metadata.create_all(bind=engine)


Session = sessionmaker(bind=engine) #deklarowanie sesji i połaczenie z silnikiem
#to samo co:
# Session = sessionmaker()
# Session.configure(bind = engine)  # do dodania silnika po stworzeniu sesji

session = Session()  # obiekt sesji, aby nie uruchamiać kilku sesji, tylko pracoeać na jednej sesji


edward = User(name=  'Ed', fullname = 'Edward Johnson',nickname = 'xyz')
print(edward.id)  #wyświetli ID = none, dlatego, żnie jest dodany do sesji. Po dodaniu go do sesji przyjmie ID np. =1


session.add(edward)
session.commit()

print(engine.execute('select * from users').fetchall())


session.add_all([
    User(name=  'Sam', fullname = 'Sam More',nickname = 'sammy12'),
    User(name=  'Joe', fullname = 'Joe Smith',nickname = 'js21')
])

session.commit()
print(session.query(User).all())    #zapytanie o wszystkich userów. Gdybyśmy mieli np. class Moto to query(Motor)
query = session.query(User)
print(query.all())   #query one - tylko do 1 obiektu, inaczej bledy. Scalar dla 0 obiektow = [], dla jednego [obiekt], dla wiecej error

bob = User(name=  'Bob', fullname = 'Bob Marley',nickname = 'bobb442')
session.add(bob)
session.commit()
bob.nickname = 'bobby42'
print(session.dirty)
print(session.query(User).all())   #ma metode flush :  https://stackoverflow.com/questions/4201455/sqlalchemy-whats-the-difference-between-flush-and-commit

print(session.dirty)

#session.new pokaze obiekty, ktore sa .add ale nie .commit

# filter zwraca listę

for user in session.query(User.nickname, User.fullname):   #zwraca tylko nick i pelne imie)
    print(user)

banned_users = aliased(User,name = 'banned_user')   #alt + enter pozwala importować od razu

for user in session.query(banned_users.nickname.label('alter')):   #do nazwania tabeli tak jakby kopii aby móc pracować
    #przykładowo chcemy pracować na 2 tych samych kolumnach tej samej tabeli to tworzymy label i na nim działamy
    print(user.alter)

sql_statement = text("SELECT * FROM users WHERE name = :name")  # przypisujemy do name kolumne name
user = session.query(User).from_statement(sql_statement).params(name='Bob').all()
print(user)


# select count(*) from users =session.query(User).count()
print(session.query(User).count())
# print(session.query(func.count('*')).select_from(User).scalar())   #to samo podzapytanie co powyzsze

print(session.query(func.count(User.id)).scalar())

print(session.query(func.count(User.name), User.name).group_by(User.name).all())   #func.count(zlicz imiona, dla user.name

jack = User(name = 'Jack', fullname= 'Jack Doe', nickname = '123')
jack.addresses= [Address(email_address = 'jack@op.pl')]  # dodajemy adres jack'a
print(jack.addresses)
print(jack.addresses[0].user)

session.add(jack)
session.commit()
#
print(session.query(User, Address).filter(User.id == Address.user_id).all())
#wyświetla tylko 1 usera, bo tylko 1 user ma adres podany. Join usera z adresem
# print(session.query(User).join(Address).all())


adalias1 = aliased(Address)
adalias2 = aliased(Address)
result = session.query(User.name,adalias1.email_address,adalias2.email_address,).join(adalias1, User.addresses).join(adalias2, User.addresses).filter(adalias1.email_address=='jack@gmail.com').filter(adalias2.email_address=='j25@yahoo.com')
for username, email1, email2 in result:
    print(username, email1, email2)

#musi mieć 2+ adresy zgodne, które podaliśmy

stmt = session.query(
    Address.user_id,func.count('*').label('address_count')
    ).group_by(Address.user_id).subquery()
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



# ponizszy kod zwraca userow
stmt = exists().where(Address.user_id==User.id)
print(session.query(User).filter(stmt).all())


# any - coś jak warunek logiczny który zwraca tych, którzy mają np. email podany
query = session.query(User)
question = query.filter(User.addresses.any()).all()
# question2 = query.filter(User.fullname.any()).all()   #blad bo jest string a any działa na liście
print(question)

print(session.query(User).all())
jack= session.query(User).filter_by(name='Jack').one()
print(jack)
session.delete(jack)  #usuwamy Usera, ale nie usuwamy np. jego adresów email któr były w osobnej klasie. Potrzebuje do tego opcję cascade
session.commit()
print(session.query(User).all())
print(session.query(Address).all())



# many to many: https://gist.github.com/adam-harmasz/2831be4437e252e88f0040fcb5c7f069