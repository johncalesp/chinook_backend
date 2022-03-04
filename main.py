from flask import jsonify, request
from sqlalchemy.sql import label, func, select
from app import app, db
import datetime
from flask_jwt_extended import jwt_required, create_access_token
from models.models import Customer, Invoice, InvoiceItem, Track, MediaType, Genre, Album, Artist
from schemas.schemas import CustomerSchema, TracksByCustomer, InvoiceSchema, SongsByInvoice
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

track_by_customer = TracksByCustomer()
tracks_by_customer = TracksByCustomer(many=True)

invoice_by_customer = InvoiceSchema()
invoices_by_customer = InvoiceSchema(many=True)

song_invoice = SongsByInvoice()
songs_invoice = SongsByInvoice(many=True)


@app.route('/api/test', methods=['GET'])
def test():
    return jsonify(message="This is a test")


# @app.route('/api/customers', methods=['GET'])
# def customers():
#     customers_list = Customer.query.all()
#     results = customers_schema.dump(customers_list)
#     return jsonify(results)
#
#
# @app.route('/api/customer_details/<int:customerid>', methods=['GET'])
# def customer_details(customerid: int):
#     customer = Customer.query.filter_by(CustomerId=customerid).first()
#     if customer:
#         result = customer_schema.dump(customer)
#         return jsonify(result)
#     else:
#         return jsonify(message='There is no customer with that id'), 404


@app.route('/api/customer_login', methods=['POST'])
def customer_login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    user = Customer.query.filter_by(Email=email, Password=password).first()
    if user:
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(identity=email, expires_delta=expires)
        customer_json = customer_schema.dump(user)
        return jsonify(customer={'customerId': customer_json['CustomerId'],
                                 'firstName': customer_json['FirstName'],
                                 'lastName': customer_json['LastName'],
                                 'company': customer_json['Company'],
                                 'address': customer_json['Address'],
                                 'city': customer_json['City'],
                                 'state': customer_json['State'],
                                 'country': customer_json['Country'],
                                 'postalCode': customer_json['PostalCode'],
                                 'phone': customer_json['Phone'],
                                 'fax': customer_json['Fax'],
                                 'email': customer_json['Email']}, accessToken=access_token)
    else:
        return jsonify(user), 401


@app.route('/api/tracks_by_customers/<int:customerid>/<int:pagenum>', methods=['GET'])
@jwt_required()
def tracks_by_customers(customerid: int, pagenum: int):
    list_tracks = Customer.query \
        .join(Invoice, Customer.CustomerId == Invoice.CustomerId) \
        .join(InvoiceItem, Invoice.InvoiceId == InvoiceItem.InvoiceId) \
        .join(Track, InvoiceItem.TrackId == Track.TrackId) \
        .join(MediaType, MediaType.MediaTypeId == Track.MediaTypeId) \
        .join(Genre, Genre.GenreId == Track.GenreId) \
        .join(Album, Album.AlbumId == Track.AlbumId) \
        .join(Artist, Artist.ArtistId == Album.ArtistId) \
        .add_columns(Track.TrackId,
                     Track.Name,
                     Track.Composer,
                     Album.Title.label('Album'),
                     Artist.Name.label('Artist'),
                     Genre.Name.label('Genre'),
                     MediaType.Name.label('MediaType'),
                     label('Duration', func.round(Track.Milliseconds / (1000 * 60.0), 2)), Track.UnitPrice) \
        .filter(Customer.CustomerId == customerid) \
        .order_by(Track.TrackId).paginate(page=pagenum, per_page=10, error_out=False)  # Track.TrackId.desc()
    num_pages = list_tracks.pages
    total_items = list_tracks.total
    if len(list_tracks.items) > 1:
        results = tracks_by_customer.dump(list_tracks.items)
        return jsonify(data=results, pages=num_pages, totalItems=total_items)
    else:
        results = tracks_by_customer.dump(list_tracks.items)
        return jsonify(data=results, pages=num_pages, totalItems=total_items)


@app.route('/api/tracks_not_owned/<int:customerid>/<int:pagenum>', methods=['GET'])
@jwt_required()
def tracks_not_owned(customerid: int, pagenum: int):

    query_tracks_ids_owned = select(Track.TrackId)\
        .join(InvoiceItem, Track.TrackId == InvoiceItem.TrackId)\
        .join(Invoice, InvoiceItem.InvoiceId == Invoice.InvoiceId)\
        .join(Customer, Invoice.CustomerId == Customer.CustomerId)\
        .filter(Customer.CustomerId == customerid).subquery()

    list_tracks = Track.query \
        .join(Album, Album.AlbumId == Track.AlbumId) \
        .join(MediaType, MediaType.MediaTypeId == Track.MediaTypeId) \
        .join(Artist, Artist.ArtistId == Album.ArtistId) \
        .join(Genre, Genre.GenreId == Track.GenreId) \
        .add_columns(Track.TrackId,
                     Track.Name,
                     Track.Composer,
                     Album.Title.label('Album'),
                     Artist.Name.label('Artist'),
                     Genre.Name.label('Genre'),
                     MediaType.Name.label('MediaType'),
                     label('Duration', func.round(Track.Milliseconds / (1000 * 60.0), 2)), Track.UnitPrice) \
        .filter(Track.TrackId.not_in(query_tracks_ids_owned))\
        .order_by(Track.TrackId).paginate(page=pagenum, per_page=10, error_out=False)  # Track.TrackId.desc()

    num_pages = list_tracks.pages
    total_items = list_tracks.total
    if len(list_tracks.items) > 1:
        results = tracks_by_customer.dump(list_tracks.items)
        return jsonify(data=results, pages=num_pages, totalItems=total_items)
    else:
        results = tracks_by_customer.dump(list_tracks.items)
        return jsonify(data=results, pages=num_pages, totalItems=total_items)


@app.route('/api/invoice_customer/<int:customerid>/<int:pagenum>', methods=['GET'])
@jwt_required()
def invoice_customer(customerid: int, pagenum: int):
    list_invoices = Invoice.query.filter_by(CustomerId=customerid).paginate(page=pagenum, per_page=10, error_out=False)
    num_pages = list_invoices.pages
    total_items = list_invoices.total
    if len(list_invoices.items) > 1:
        results = invoices_by_customer.dump(list_invoices.items)
        return jsonify(data=results, pages=num_pages, totalItems=total_items)
    else:
        result = invoices_by_customer.dump(list_invoices.items)
        return jsonify(data=result, pages=num_pages, totalItems=total_items)


@app.route('/api/tracks_by_invoice/<int:invoiceid>/<int:pagenum>', methods=['GET'])
@jwt_required()
def songs_by_invoice(invoiceid: int, pagenum: int):
    list_songs = InvoiceItem.query \
        .join(Track, Track.TrackId == InvoiceItem.TrackId) \
        .join(Album, Album.AlbumId == Track.AlbumId) \
        .join(Artist, Artist.ArtistId == Album.ArtistId) \
        .add_columns(Track.TrackId,
                     Track.Name,
                     label('Duration', func.round(Track.Milliseconds / (1000 * 60.0), 2)),
                     Album.Title.label('Album'),
                     Artist.Name.label('Artist'),
                     Track.UnitPrice) \
        .filter(InvoiceItem.InvoiceId == invoiceid).paginate(page=pagenum, per_page=10, error_out=False)
    num_pages = list_songs.pages
    total_items = list_songs.total
    if len(list_songs.items) > 1:
        results = songs_invoice.dump(list_songs.items)
        return jsonify(data=results, pages=num_pages, totalItems=total_items)
    else:
        result = songs_invoice.dump(list_songs.items)
        return jsonify(data=result, pages=num_pages, totalItems=total_items)

@app.route('/api/update_user',methods=['POST'])
@jwt_required()
def update_user():
    if request.is_json:
        id = request.json['id']
        firstName = request.json['firstName']
        lastName = request.json['lastName']
        company = request.json['company']
        phone = request.json['phone']
        address = request.json['address']
        city = request.json['city']
    else:
        id = request.form['id']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        company = request.form['company']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']

    user = Customer.query.filter_by(CustomerId=id).first()
    user.FirstName = firstName
    user.LastName = lastName
    user.Company = company
    user.Phone = phone
    user.Address = address
    user.City = city
    db.session.commit()

    if user:
        customer_json = customer_schema.dump(user)
        return jsonify(customer={'customerId': customer_json['CustomerId'],
                                 'firstName': customer_json['FirstName'],
                                 'lastName': customer_json['LastName'],
                                 'company': customer_json['Company'],
                                 'address': customer_json['Address'],
                                 'city': customer_json['City'],
                                 'state': customer_json['State'],
                                 'country': customer_json['Country'],
                                 'postalCode': customer_json['PostalCode'],
                                 'phone': customer_json['Phone'],
                                 'fax': customer_json['Fax'],
                                 'email': customer_json['Email']})
    else:
        return jsonify(user), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=4000)
