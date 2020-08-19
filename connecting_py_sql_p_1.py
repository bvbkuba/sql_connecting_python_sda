import sqlalchemy
from sqlalchemy import create_engine    #import tool to connect with database

engine = create_engine('sqlite:///:memory:',echo = True)    # create Object engine to connect with db
print(engine)   #information for me

department = """CREATE TABLE Department(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
name VARCHAR NOT NULL);"""  #create table in sql
engine.execute(department)

position = """CREATE TABLE Position(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
name VARCHAR NOT NULL);"""  #create table in sql
engine.execute(position)

employee = """CREATE TABLE Employee(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
first_name VARCHAR,
last_name VARCHAR,
email VARCHAR,
adress VARCHAR,
salary FLOAT,
position_id INTEGER,
department_id INTEGER,
FOREIGN KEY (position_id) references Position(id),
FOREIGN KEY (department_id) references Department(id)
);"""
engine.execute(employee)

#Dodawanie wierszy
engine.execute("INSERT INTO Department(name) VALUES ('HR');")   # za każdym razem musimy dawać engine.execute - czy tworząc tabele czy dodając wiersz
engine.execute("INSERT INTO Department(name) VALUES ('IT');")

# print(engine.execute("SELECT * FROM Department"))  # wrong
# print(engine.execute("SELECT * FROM Department").first()) # zwróci tylko 1 wiersz
query = engine.execute("SELECT * FROM Department")    #najlepsza opcja - przypisanie do zmiennej a potem pętla for
def show_table(select_query):
    for i in select_query:
        print(i)

show_table(query)

engine.execute("INSERT INTO Position (name) VALUES ('Back-end developer');")
engine.execute("INSERT INTO Position (name) VALUES ('Front-end developer');")
query_position = engine.execute("SELECT * FROM Position")
show_table(query_position)

engine.execute("INSERT INTO Employee ("
               "first_name, last_name, email, adress, salary, position_id, department_id"
               ") VALUES ('Maciej','Maciejowski', 'maciej@op.pl', 'IT Strasse 10/8', 4000.00, 1,1)")

query_employee = engine.execute("SELECT * FROM Employee")
show_table(query_employee)