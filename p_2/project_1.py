from sqlalchemy import create_engine, Column, Integer, String, Sequence, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine("sqlite:///:memory:")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Levels(Base):
    __tablename__ = "levels"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    name = Column(String(50), nullable=False)

    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Courses", back_populates="levels")

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"


class Languages(Base):
    __tablename__ = "languages"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    name = Column(String(50), nullable=False)

    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Courses", back_populates="languages")

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"


class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    name = Column(String(50), nullable=False)

    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Courses", back_populates="categories")

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"


class Courses(Base):
    __tablename__ = "courses"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    name = Column(String(50), nullable=False)
    nr_of_lessons = Column(Integer, nullable=False)
    description = Column(String(255))
    price = Column(Float, nullable=False)

    languages = relationship("Languages", back_populates="course")
    categories = relationship("Categories", back_populates="course")
    levels = relationship("Levels", back_populates="course")

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}, level: {self.levels}, langL {self.languages}"


Base.metadata.create_all(engine)

LEVELS_DATA = (
    {"name": "A0"},
    {"name": "A1"},
    {"name": "A2"},
    {"name": "B1"},
    {"name": "B2"},
    {"name": "C1"},
    {"name": "C2"},
)

LANG_DATA = (
    {"name": "English"},
    {"name": "German"},
    {"name": "Spanish"},
    {"name": "Italian"},
)

CATEGORIES_DATA = (
    {"name": "Evening"},
    {"name": "Regular"},
    {"name": "Weekend"},
)


def get_level_objects():
    return [Levels(**level) for level in LEVELS_DATA]


def create_levels():
    session.add_all(get_level_objects())
    session.commit()


def get_lang_objects():
    return [Languages(**lang) for lang in LANG_DATA]


def create_langs():
    session.add_all(get_lang_objects())
    session.commit()


def get_categories_objects():
    return [Categories(**category) for category in CATEGORIES_DATA]


def create_categories():
    session.add_all(get_categories_objects())
    session.commit()


def create_basic_data():
    create_levels()
    create_langs()
    create_categories()


create_basic_data()