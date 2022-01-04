from flask import jsonify,request
from sqlalchemy.sql import label, func
from app import app,jwt
from flask_jwt_extended import jwt_required, create_access_token
from models.models import Customer, Invoice, InvoiceItem, Track, MediaType, Genre, Album, Artist
from schemas.schemas import CustomerSchema, TracksByCustomer, InvoiceSchema, SongsByInvoice

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

track_by_customer = TracksByCustomer()
tracks_by_customer = TracksByCustomer(many=True)

invoice_by_customer = InvoiceSchema()
invoices_by_customer = InvoiceSchema(many=True)

song_invoice = SongsByInvoice()
songs_invoice = SongsByInvoice(many=True)


@app.route('/test', methods=['GET'])
def test():
    return jsonify(message="This is a test")


@app.route('/customers', methods=['GET'])
def customers():
    customers_list = Customer.query.all()
    results = customers_schema.dump(customers_list)
    return jsonify(results)


@app.route('/customer_details/<int:customerid>', methods=['GET'])
def customer_details(customerid: int):
    customer = Customer.query.filter_by(CustomerId=customerid).first()
    if customer:
        result = customer_schema.dump(customer)
        return jsonify(result)
    else:
        return jsonify(message='There is no customer with that id'), 404


@app.route('/customer_login', methods=['POST'])
def customer_login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    user = Customer.query.filter_by(Email=email,Password=password).first()
    if user:
        access_token = create_access_token(identity=email)
        customer_json = customer_schema.dump(user)
        return jsonify(customer=customer_json, access_token=access_token)
    else:
        return jsonify(user), 401


@app.route('/tracks_by_customers/<int:customerid>', methods=['GET'])
def tracks_by_customers(customerid: int):
    list_tracks = Customer.query\
                .join(Invoice, Customer.CustomerId == Invoice.CustomerId)\
                .join(InvoiceItem, Invoice.InvoiceId == InvoiceItem.InvoiceId)\
                .join(Track, InvoiceItem.TrackId == Track.TrackId)\
                .join(MediaType, MediaType.MediaTypeId == Track.MediaTypeId)\
                .join(Genre, Genre.GenreId == Track.GenreId)\
                .join(Album, Album.AlbumId == Track.AlbumId)\
                .join(Artist, Artist.ArtistId == Album.ArtistId)\
                .add_columns(Track.TrackId,
                             Track.Name,
                             Track.Composer,
                             Album.Title.label('Album'),
                             Artist.Name.label('Artist'),
                             Genre.Name.label('Genre'),
                             MediaType.Name.label('MediaType'),
                             label('Duration', func.round(Track.Milliseconds/(1000*60.0), 2)), Track.UnitPrice)\
                .filter(Customer.CustomerId == customerid)\
                .order_by(Track.TrackId).all() #Track.TrackId.desc()
    if len(list_tracks) > 1:
        results = tracks_by_customer.dump(list_tracks)
        return jsonify(results)
    else:
        results = track_by_customer.dump(list_tracks)
        return jsonify(results)


@app.route('/tracks_not_owned/<int:customerid>', methods=['GET'])
def tracks_not_owned(customerid: int):
    list_tracks = Customer.query\
                .join(Invoice, Customer.CustomerId == Invoice.CustomerId)\
                .join(InvoiceItem, Invoice.InvoiceId == InvoiceItem.InvoiceId)\
                .join(Track, InvoiceItem.TrackId == Track.TrackId)\
                .join(MediaType, MediaType.MediaTypeId == Track.MediaTypeId)\
                .join(Genre, Genre.GenreId == Track.GenreId)\
                .join(Album, Album.AlbumId == Track.AlbumId)\
                .join(Artist, Artist.ArtistId == Album.ArtistId)\
                .add_columns(Track.TrackId,
                             Track.Name,
                             Track.Composer,
                             Album.Title.label('Album'),
                             Artist.Name.label('Artist'),
                             Genre.Name.label('Genre'),
                             MediaType.Name.label('MediaType'),
                             label('Duration', func.round(Track.Milliseconds/(1000*60.0), 2)), Track.UnitPrice)\
                .filter(Customer.CustomerId != customerid)\
                .order_by(Track.TrackId).all() #Track.TrackId.desc()
    if len(list_tracks) > 1:
        results = tracks_by_customer.dump(list_tracks)
        return jsonify(results)
    else:
        results = track_by_customer.dump(list_tracks)
        return jsonify(results)


@app.route('/invoice_customer/<int:customerid>', methods=['GET'])
def invoice_customer(customerid: int):
    list_invoices = Invoice.query.filter_by(CustomerId=customerid).all()
    if len(list_invoices) > 1:
        results = invoices_by_customer.dump(list_invoices)
        return jsonify(results)
    else:
        result = invoice_by_customer.dump(list_invoices)
        return jsonify(result)


@app.route('/songs_by_invoice/<int:invoiceid>', methods=['GET'])
def songs_by_invoice(invoiceid: int):
    list_songs = InvoiceItem.query\
                .join(Track, Track.TrackId == InvoiceItem.TrackId)\
                .join(Album, Album.AlbumId == Track.AlbumId)\
                .join(Artist, Artist.ArtistId == Album.AlbumId)\
                .add_columns(Track.TrackId,
                             Track.Name,
                             label('Duration', func.round(Track.Milliseconds/(1000*60.0), 2)),
                             Album.Title.label('Album'),
                             Artist.Name.label('Artist'),
                             Track.UnitPrice)\
                .filter(InvoiceItem.InvoiceId == invoiceid).all()
    if len(list_songs) > 1:
        results = songs_invoice.dump(list_songs)
        return jsonify(results)
    else:
        result = song_invoice.dump(list_songs)
        return jsonify(result)


if __name__ == '__main__':
    app.run(port=3000)
