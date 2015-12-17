from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime

Base = declarative_base()

# Define Category class 
class Category(Base):
    __tablename__ = 'categories'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name
       }

# Define Item class 
class Item(Base):
    __tablename__ = 'items'
   
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    creator = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    desc = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'created'      : self.created,
           'creator'      : self.creator,
           'name'         : self.name,
           'desc'         : self.desc,
           'category_id'  : self.category_id
       }

# Function to provide a session object for the database
def get_session():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session
 
# Open catalog database
engine = create_engine('postgresql://catalog:udacity@localhost/catalog')
 

Base.metadata.create_all(engine)
