from app import ma


class CustomerSchema(ma.Schema):
    class Meta:
        fields = ('CustomerId','FirstName','LastName','Company','Address','City','State','Country','PostalCode','Phone'
                  ,'Fax','Email','Password')


class InvoiceSchema(ma.Schema):
    class Meta:
        fields = ('InvoiceId', 'CustomerId', 'InvoiceDate',	'BillingAddress', 'BillingCity', 'BillingState'
                  , 'BillingCountry', 'BillingPostalCode', 'Total')


class SongsByInvoice(ma.Schema):
    class Meta:
        fields = ('TrackId', 'Name', 'Duration', 'Album', 'Artist', 'UnitPrice')


class TracksByCustomer(ma.Schema):
    class Meta:
        fields = ('TrackId', 'Name', 'Composer', 'Album', 'Artist', 'Genre', 'MediaType', 'Duration', 'UnitPrice')
