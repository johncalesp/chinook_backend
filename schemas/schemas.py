from app import ma


class CustomerSchema(ma.Schema):
    class Meta:
        fields = ('CustomerId','FirstName','LastName','Company','Address','City','State','Country','PostalCode','Phone','Fax','Email','Password')