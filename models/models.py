from app import db
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


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
    invoices = relationship("Invoice", back_populates="customer")


class Invoice(db.Model):
    __tablename__ = 'invoices'
    InvoiceId = Column(Integer, primary_key=True )
    CustomerId = Column(Integer, ForeignKey('customers.CustomerId'))
    InvoiceDate = Column(DateTime)
    BillingAddress = Column(String)
    BillingCity = Column(String)
    BillingState = Column(String)
    BillingCountry = Column(String)
    BillingPostalCode = Column(String)
    Total = Column(Numeric(10,2))
    customer = relationship("Customer", back_populates="invoices")
    invoiceItem = relationship("InvoiceItem", back_populates="invoices")


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    InvoiceLineId = Column(Integer, primary_key=True )
    InvoiceId = Column(Integer, ForeignKey('invoices.InvoiceId'))
    TrackId = Column(Integer, ForeignKey('tracks.TrackId'))
    UnitPrice = Column(Numeric(10, 2))
    Quantity = Column(Integer)
    invoices = relationship("Invoice", back_populates="invoiceItem")
    tracks = relationship("Track", back_populates="trackItem")


class Track(db.Model):
    __tablename__ = 'tracks'
    TrackId = Column(Integer, primary_key=True )
    Name = Column(String)
    AlbumId = Column(Integer, ForeignKey('albums.AlbumId'))
    MediaTypeId = Column(Integer, ForeignKey('media_types.MediaTypeId'))
    GenreId = Column(Integer, ForeignKey('genres.GenreId'))
    Composer = Column(String)
    Milliseconds = Column(Integer)
    Bytes = Column(Integer)
    UnitPrice = Column(Numeric(10,2))
    trackItem = relationship("InvoiceItem", back_populates="tracks")
    album = relationship("Album", back_populates="track")
    media = relationship("MediaType", back_populates="track")
    genre = relationship("Genre", back_populates="track")


class Album(db.Model):
    __tablename__ = 'albums'
    AlbumId = Column(Integer, primary_key=True )
    Title = Column(String)
    ArtistId = Column(Integer, ForeignKey('artists.ArtistId'))
    track = relationship("Track", back_populates="album")
    artist = relationship("Artist", back_populates="album")


class Artist(db.Model):
    __tablename__ = 'artists'
    ArtistId = Column(Integer, primary_key=True )
    Name = Column(String)
    album = relationship("Album", back_populates="artist")


class MediaType(db.Model):
    __tablename__ = 'media_types'
    MediaTypeId = Column(Integer, primary_key=True )
    Name = Column(String)
    track = relationship("Track", back_populates="media")


class Genre(db.Model):
    __tablename__ = 'genres'
    GenreId = Column(Integer, primary_key=True )
    Name = Column(String)
    track = relationship("Track", back_populates="genre")
