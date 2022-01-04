from app import db
from sqlalchemy import Column, Integer, String


class Customer(db.Model):
    __tablename__ = 'customers'
    CustomerId = Column(Integer, primary_key=True)
    FirstName = Column(String)
    LastName = Column(String)
    Company = Column(String)
    Address = Column(String)
    City = Column(String)
    State = Column(String)
    Country = Column(String)
    PostalCode = Column(String)
    Phone = Column(String)
    Fax = Column(String)
    Email = Column(String, unique=True)
    Password = Column(String)
