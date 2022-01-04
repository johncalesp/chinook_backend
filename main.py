from flask import jsonify,request
from app import app,jwt
from flask_jwt_extended import jwt_required, create_access_token
from models.models import Customer
from schemas.schemas import CustomerSchema

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


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


if __name__ == '__main__':
    app.run(port=3000)
