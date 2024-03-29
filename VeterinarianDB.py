# Flask SQL Alchemy
from flask import Flask, jsonify, request
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.sql import select, and_, or_
from sqlalchemy import delete
from sqlalchemy import text
from sqlalchemy import distinct, func
import pprint
import json


connection_string = 'mysql+pymysql://root:my_password@127.0.0.1:3306/Veterinarian?autocommit=true'
engine = create_engine(connection_string, echo=True)
conn = engine.connect()

metadata = MetaData()

app = Flask(__name__)

port_number = 7002

# Get table structures from the database

ap = Table('appointment', metadata, autoload_with=engine)
bill = Table('billing', metadata, autoload_with=engine)
cli = Table('clients', metadata, autoload_with=engine)
ow = Table('owner', metadata, autoload_with=engine)
vet = Table('veterinarian', metadata, autoload_with=engine)


# Codes to GET all the elements from the tables using HTTP
# curl -v http://localhost:7002/appointments
@app.route('/appointments', methods=["GET"])
def get_appoitnment():
    query = select(ap)
    appointments = conn.execute(query).fetchall()
    return json.dumps([row._asdict() for row in appointments])

# curl -v http://localhost:7002/billings
@app.route('/billings', methods=["GET"])
def get_billing():
    query = select(bill)
    billings = conn.execute(query).fetchall()
    return json.dumps([row._asdict() for row in billings], default=str)

# curl -v http://localhost:7002/clients
@app.route('/clients', methods=["GET"])
def get_client():
    query = select(cli)
    clients = conn.execute(query).fetchall()
    return json.dumps([row._asdict() for row in clients])

# curl -v http://localhost:7002/owners
@app.route('/owners', methods=["GET"])
def get_owner():
    query = select(ow)
    owners = conn.execute(query).fetchall()
    return json.dumps([row._asdict() for row in owners])

# curl -v http://localhost:7002/veterinarians
@app.route('/veterinarians', methods=["GET"])
def get_veterinarian():
    query = select(vet)
    veterinarians = conn.execute(query).fetchall()
    return json.dumps([row._asdict() for row in veterinarians])


# Codes to GET the elements from the tables by ID using HTTP
# curl -v http://localhost:7002/appointments/id
@app.route('/appointments/<id>', methods=["GET"])
def get_appoitnment_by_id(id):
    query = select(ap).where(ap.c.appointment_id == id)
    appointments = conn.execute(query).fetchall()
    if appointments != []:
        return json.dumps([row._asdict() for row in appointments])
    return f'Appointment with id {id} not found', 404

# curl -v http://localhost:7002/billings/id
@app.route('/billings/<id>', methods=["GET"])
def get_billing_by_id(id):
    query = select(bill).where(bill.c.billing_id == id)
    billings = conn.execute(query).fetchall()
    if billings != []:
        return json.dumps([row._asdict() for row in billings], default=str)
    return f'Billing with id {id} not found', 404

# curl -v http://localhost:7002/clients/id
@app.route('/clients/<id>', methods=["GET"])
def get_client_by_id(id):
    query = select(cli).where(cli.c.client_id == id)
    clients = conn.execute(query).fetchall()
    if clients != []:
        return json.dumps([row._asdict() for row in clients])
    return f'Client with id {id} not found', 404

# curl -v http://localhost:7002/owners/id
@app.route('/owners/<id>', methods=["GET"])
def get_owner_by_id(id):
    query = select(ow).where(ow.c.owner_id == id)
    owners = conn.execute(query).fetchall()
    if owners != []:
        return json.dumps([row._asdict() for row in owners])
    return f'Owner with id {id} not found', 404

# curl -v http://localhost:7002/veterinarians/id
@app.route('/veterinarians/<id>', methods=["GET"])
def get_veterinarian_by_id(id):
    query = select(vet).where(vet.c.veterinarian_id == id)
    veterinarians = conn.execute(query).fetchall()
    if veterinarians != []:
        return json.dumps([row._asdict() for row in veterinarians])
    return f'Veterinarian with id {id} not found', 404


# Codes to INSERT values into the tables using HTTP
# curl --header "Content-Type: application/json" --request POST --data "{\"id\": \"6\", \"first_name\": \"Pedro\", \"last_name\": \"Picapiedra\", \"direction\": \"Guayaquil\", \"phone\": \"0984787561\"}" -v http://localhost:7002/owners
@app.route("/owners", methods=["POST"])
def insert_owner():
    owner_details = request.get_json()
    id = owner_details["id"]
    first_name = owner_details["first_name"]
    last_name = owner_details["last_name"]
    direction = owner_details["direction"]
    phone = owner_details["phone"]

    # Check if ID already exists
    sel = ow.select().where(ow.c.owner_id == id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Owner with id {id} already exists', 409

    ins = ow.insert().values((id, first_name, last_name, direction, phone))
    conn.execute(ins)
    new_owner = {"id": id, "first_name": first_name, "last_name": last_name, "direction": direction, "phone": phone}
    return jsonify(new_owner), 201

# curl --header "Content-Type: application/json" --request POST --data "{\"client_id\": \"6\", \"owner_id\": \"5\", \"name\": \"Pichu\", \"species\": \"Cat\", \"breed\": \"Bengala\", \"sex\": \"Male\", \"age\": \"2\", \"treatment\": \"Active\"}" -v http://localhost:7002/clients
@app.route("/clients", methods=["POST"])
def insert_client():
    client_details = request.get_json()
    client_id = client_details["client_id"]
    owner_id = client_details["owner_id"]
    name = client_details["name"]
    species = client_details["species"]
    breed = client_details["breed"]
    sex = client_details["sex"]
    age = client_details["age"]
    treatment = client_details["treatment"]

    # Check if client ID already exists
    sel = cli.select().where(cli.c.client_id == client_id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Client with id {client_id} already exists', 409

    # Check if owner ID exists
    sel = ow.select().where(ow.c.owner_id == owner_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Owner with id {owner_id} not found', 404

    ins = cli.insert().values((client_id, owner_id, name, species, breed, sex, age, treatment))
    conn.execute(ins)
    new_client = {"client_id": client_id, "owner_id": owner_id, "name": name, "species": species, "breed": breed, "sex": sex, "age": age, "treatment": treatment}
    return jsonify(new_client), 201

# curl --header "Content-Type: application/json" --request POST --data "{\"id\": \"5\", \"name\": \"Alan\", \"last_name\": \"Walker\", \"phone\": \"0961452365\", \"direction\": \"Argentina\", \"specialization\": \"Cats\"}" -v http://localhost:7002/veterinarians
@app.route("/veterinarians", methods=["POST"])
def insert_veterinarian():
    veterinarian_details = request.get_json()
    id = veterinarian_details["id"]
    name = veterinarian_details["name"]
    last_name = veterinarian_details["last_name"]
    phone = veterinarian_details["phone"]
    direction = veterinarian_details["direction"]
    specialization = veterinarian_details["specialization"]

    # Check if ID already exists
    sel = vet.select().where(vet.c.veterinarian_id == id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Veterinarian with id {id} already exists', 409

    ins = vet.insert().values((id, name, last_name, phone, direction, specialization))
    conn.execute(ins)
    new_veterinarian = {"id": id, "name": name, "last_name": last_name, "phone": phone, "direction": direction, "specialization": specialization}
    return jsonify(new_veterinarian), 201

# curl --header "Content-Type: application/json" --request POST --data "{\"appointment_id\": \"4\", \"client_id\": \"2\", \"owner_id\": \"4\", \"veterinarian_id\": \"3\", \"date\": \"2023-12-15\", \"time\": \"16h30\", \"reason\": \"Vaccine\"}" -v http://localhost:7002/appointments
@app.route("/appointments", methods=["POST"])
def insert_appointment():
    appointment_details = request.get_json()
    appointment_id = appointment_details["appointment_id"]
    client_id = appointment_details["client_id"]
    owner_id = appointment_details["owner_id"]
    veterinarian_id = appointment_details["veterinarian_id"]
    date = appointment_details["date"]
    time = appointment_details["time"]
    reason = appointment_details["reason"]

    # Check if appointment ID already exists
    sel = ap.select().where(ap.c.appointment_id == appointment_id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Appointment with id {appointment_id} already exists', 409

    # Check if client ID exists
    sel = cli.select().where(cli.c.client_id == client_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Client with id {client_id} not found', 404

    # Check if owner ID exists
    sel = ow.select().where(ow.c.owner_id == owner_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Owner with id {owner_id} not found', 404

    # Check if owner ID is designated to client ID
    sel = cli.select().where(cli.c.owner_id == owner_id)
    result = conn.execute(sel).fetchall()
    if result:
        pass
    else:
        return f'Owner with ID {owner_id} is not designated to the client with ID {client_id}.', 400

    # Check if veterinarian ID exists
    sel = vet.select().where(vet.c.veterinarian_id == veterinarian_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Veterinarian with id {veterinarian_id} not found', 404

    # Check if the date is valid
    if len(date) > 10 or len(date) < 10:
        return f'Invalid date', 400

    # Check if the time is valid
    if len(time) > 5 or len(time) < 5:
        return f'Invalid time', 400

    ins = ap.insert().values((appointment_id, client_id, owner_id, veterinarian_id, date, time, reason))
    conn.execute(ins)
    new_appointment = {"appointment_id": appointment_id, "client_id": client_id, "owner_id": owner_id, "veterinarian_id": veterinarian_id, "date": date, "time": time, "reason": reason}
    return jsonify(new_appointment), 201

# curl --header "Content-Type: application/json" --request POST --data "{\"billing_id\": \"7\", \"appointment_id\": \"21\", \"client_id\": \"3\", \"owner_id\": \"2\", \"veterinarian_id\": \"1\", \"date\": \"2023-12-15\", \"service\": \"Vaccine\", \"cost\": \"7.50\"}" -v http://localhost:7002/billings
@app.route("/billings", methods=["POST"])
def insert_billing():
    billing_details = request.get_json()
    billing_id = billing_details["billing_id"]
    appointment_id = billing_details["appointment_id"]
    client_id = billing_details["client_id"]
    owner_id = billing_details["owner_id"]
    veterinarian_id = billing_details["veterinarian_id"]
    date = billing_details["date"]
    service = billing_details["service"]
    cost = billing_details["cost"]

    # Check if billing ID already exists
    sel = bill.select().where(bill.c.billing_id == billing_id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Billing with id {billing_id} already exists', 409

    # Check if appointment ID exists
    sel = ap.select().where(ap.c.appointment_id == appointment_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Appointment with id {appointment_id} not found', 404

    # Check if client ID exists
    sel = cli.select().where(cli.c.client_id == client_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Client with id {client_id} not found', 404

    # Check if owner ID exists
    sel = ow.select().where(ow.c.owner_id == owner_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Owner with id {owner_id} not found', 404

    # Check if owner ID is designated to client ID
    sel = cli.select().where(cli.c.owner_id == owner_id)
    result = conn.execute(sel).fetchall()
    if result:
        pass
    else:
        return f'Owner with ID {owner_id} is not designated to the client with ID {client_id}.', 400

    # Check if veterinarian ID exists
    sel = vet.select().where(vet.c.veterinarian_id == veterinarian_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Veterinarian with id {veterinarian_id} not found', 404

    # Check if the date is valid
    if len(date) > 10 or len(date) < 10:
        return f'Invalid date', 400

    ins = bill.insert().values((billing_id, appointment_id, client_id, owner_id, veterinarian_id, date, service, cost))
    conn.execute(ins)
    new_billing = {"billing_id": billing_id, "appointment_id": appointment_id, "client_id": client_id, "owner_id": owner_id, "veterinarian_id": veterinarian_id, "date": date, "service": service, "cost": cost}
    return jsonify(new_billing), 201


# Codes to UPDATE values from the tables using HTTP
# curl --header "Content-Type: application/json" --request PUT --data "{\"owner_id\": \"7\", \"first_name\": \"Pedro\", \"last_name\": \"Picapiedra\", \"direction\": \"Guayaquil\", \"phone\": \"0984787561\"}" -v http://localhost:7002/owners/id
@app.route("/owners/<id>", methods=["PUT"])
def update_owner(id):
    owner_details = request.get_json()
    owner_id = owner_details["owner_id"]
    first_name = owner_details["first_name"]
    last_name = owner_details["last_name"]
    direction = owner_details["direction"]
    phone = owner_details["phone"]

    # Check if ID already exists
    sel = ow.select().where(ow.c.owner_id == owner_id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Owner with id {id} already exists', 409

    stmt = ow.update().where(ow.c.owner_id == id).values((owner_id, first_name, last_name, direction, phone))
    conn.execute(stmt)
    updated_owner = {"owner_id": owner_id, "first_name": first_name, "last_name": last_name, "direction": direction, "phone": phone}
    return jsonify(updated_owner), 200

# curl --header "Content-Type: application/json" --request PUT --data "{\"client_id\": \"12\", \"owner_id\": \"5\", \"name\": \"Pichu\", \"species\": \"Cat\", \"breed\": \"Bengala\", \"sex\": \"Male\", \"age\": \"2\", \"treatment\": \"Active\"}" -v http://localhost:7002/clients/id
@app.route("/clients/<id>", methods=["PUT"])
def update_client(id):
    client_details = request.get_json()
    client_id = client_details["client_id"]
    owner_id = client_details["owner_id"]
    name = client_details["name"]
    species = client_details["species"]
    breed = client_details["breed"]
    sex = client_details["sex"]
    age = client_details["age"]
    treatment = client_details["treatment"]

    # Check if client ID already exists
    sel = cli.select().where(cli.c.client_id == client_id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Client with id {client_id} already exists', 409

    # Check if owner ID exists
    sel = ow.select().where(ow.c.owner_id == owner_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Owner with id {owner_id} not found', 404

    stmt = cli.update().where(cli.c.client_id == id).values((client_id, owner_id, name, species, breed, sex, age, treatment))
    conn.execute(stmt)
    updated_client = {"client_id": client_id, "owner_id": owner_id, "name": name, "species": species, "breed": breed, "sex": sex, "age": age, "treatment": treatment}
    return jsonify(updated_client), 200

# curl --header "Content-Type: application/json" --request PUT --data "{\"veterinarian_id\": \"8\", \"name\": \"Alan\", \"last_name\": \"Walker\", \"phone\": \"0961452365\", \"direction\": \"Argentina\", \"specialization\": \"Cats\"}" -v http://localhost:7002/veterinarians/id
@app.route("/veterinarians/<id>", methods=["PUT"])
def update_veterinarian():
    veterinarian_details = request.get_json()
    veterinarian_id = veterinarian_details["veterinarian_id"]
    name = veterinarian_details["name"]
    last_name = veterinarian_details["last_name"]
    phone = veterinarian_details["phone"]
    direction = veterinarian_details["direction"]
    specialization = veterinarian_details["specialization"]

    # Check if ID already exists
    sel = vet.select().where(vet.c.veterinarian_id == veterinarian_id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Veterinarian with id {id} already exists', 409

    stmt = vet.update().where(vet.c.veterinarian_id == id).values((veterinarian_id, name, last_name, phone, direction, specialization))
    conn.execute(stmt)
    updated_veterinarian = {"veterinarian_id": veterinarian_id, "name": name, "last_name": last_name, "phone": phone, "direction": direction, "specialization": specialization}
    return jsonify(updated_veterinarian), 200

# curl --header "Content-Type: application/json" --request PUT --data "{\"appointment_id\": \"2\", \"client_id\": \"2\", \"owner_id\": \"4\", \"veterinarian_id\": \"3\", \"date\": \"2023-12-15\", \"time\": \"16h30\", \"reason\": \"Vaccine\"}" -v http://localhost:7002/appointments/id
@app.route("/appointments/<id>", methods=["PUT"])
def update_appointment():
    appointment_details = request.get_json()
    appointment_id = appointment_details["appointment_id"]
    client_id = appointment_details["client_id"]
    owner_id = appointment_details["owner_id"]
    veterinarian_id = appointment_details["veterinarian_id"]
    date = appointment_details["date"]
    time = appointment_details["time"]
    reason = appointment_details["reason"]

    # Check if appointment ID already exists
    sel = ap.select().where(ap.c.appointment_id == appointment_id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Appointment with id {appointment_id} already exists', 409

    # Check if client ID exists
    sel = cli.select().where(cli.c.client_id == client_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Client with id {client_id} not found', 404

    # Check if owner ID exists
    sel = ow.select().where(ow.c.owner_id == owner_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Owner with id {owner_id} not found', 404

    # Check if owner ID is designated to client ID
    sel = cli.select().where(cli.c.owner_id == owner_id)
    result = conn.execute(sel).fetchall()
    if result:
        pass
    else:
        return f'Owner with ID {owner_id} is not designated to the client with ID {client_id}.', 400

    # Check if veterinarian ID exists
    sel = vet.select().where(vet.c.veterinarian_id == veterinarian_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Veterinarian with id {veterinarian_id} not found', 404

    # Check if the date is valid
    if len(date) > 10 or len(date) < 10:
        return f'Invalid date', 400

    # Check if the time is valid
    if len(time) > 5 or len(time) < 5:
        return f'Invalid time', 400

    stmt = ap.update().where(ap.c.appointment_id == id).values((appointment_id, client_id, owner_id, veterinarian_id, date, time, reason))
    conn.execute(stmt)
    updated_appointment = {"appointment_id": appointment_id, "client_id": client_id, "owner_id": owner_id, "veterinarian_id": veterinarian_id, "date": date, "time": time, "reason": reason}
    return jsonify(updated_appointment), 200

# curl --header "Content-Type: application/json" --request PUT --data "{\"billing_id\": \"15\", \"appointment_id\": \"21\", \"client_id\": \"3\", \"owner_id\": \"2\", \"veterinarian_id\": \"1\", \"date\": \"2023-12-15\", \"service\": \"Vaccine\", \"cost\": \"7.50\"}" -v http://localhost:7002/billings/id
@app.route("/billings", methods=["PUT"])
def update_billing():
    billing_details = request.get_json()
    billing_id = billing_details["billing_id"]
    appointment_id = billing_details["appointment_id"]
    client_id = billing_details["client_id"]
    owner_id = billing_details["owner_id"]
    veterinarian_id = billing_details["veterinarian_id"]
    date = billing_details["date"]
    service = billing_details["service"]
    cost = billing_details["cost"]

    # Check if billing ID already exists
    sel = bill.select().where(bill.c.billing_id == billing_id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        return f'Billing with id {billing_id} already exists', 409

    # Check if appointment ID exists
    sel = ap.select().where(ap.c.appointment_id == appointment_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Appointment with id {appointment_id} not found', 404

    # Check if client ID exists
    sel = cli.select().where(cli.c.client_id == client_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Client with id {client_id} not found', 404

    # Check if owner ID exists
    sel = ow.select().where(ow.c.owner_id == owner_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Owner with id {owner_id} not found', 404

    # Check if owner ID is designated to client ID
    sel = cli.select().where(cli.c.owner_id == owner_id)
    result = conn.execute(sel).fetchall()
    if result:
        pass
    else:
        return f'Owner with ID {owner_id} is not designated to the client with ID {client_id}.', 400

    # Check if veterinarian ID exists
    sel = vet.select().where(vet.c.veterinarian_id == veterinarian_id)
    result = conn.execute(sel).fetchone()
    if result is None:
        return f'Veterinarian with id {veterinarian_id} not found', 404

    # Check if the date is valid
    if len(date) > 10 or len(date) < 10:
        return f'Invalid date', 400

    stmt = bill.update().where(bill.c.billing_id == id).values((billing_id, appointment_id, client_id, owner_id, veterinarian_id, date, service, cost))
    conn.execute(stmt)
    updated_billing = {"billing_id": billing_id, "appointment_id": appointment_id, "client_id": client_id, "owner_id": owner_id, "veterinarian_id": veterinarian_id, "date": date, "service": service, "cost": cost}
    return jsonify(updated_billing), 200

# Codes to DELETE values from the tables using HTTP
# curl --request DELETE -v http://localhost:7002/owners/id
@app.route('/owners/<id>', methods=['DELETE'])
def delete_owner(id):
    sel = ow.select().where(ow.c.owner_id == id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        stmt = delete(ow).where(ow.c.owner_id == id)
        conn.execute(stmt)
        return f'Owner with ID {id} deleted', 200
    return f'Owner with ID {id} not found', 404

# curl --request DELETE -v http://localhost:7002/clients/id
@app.route('/clients/<id>', methods=['DELETE'])
def delete_client(id):
    sel = cli.select().where(cli.c.client_id == id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        stmt = delete(cli).where(cli.c.client_id == id)
        conn.execute(stmt)
        return f'Client with ID {id} deleted', 200
    return f'Client with ID {id} not found', 404

# curl --request DELETE -v http://localhost:7002/veterinarians/id
@app.route('/veterinarians/<id>', methods=['DELETE'])
def delete_veterinarian(id):
    sel = vet.select().where(vet.c.veterinarian_id == id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        stmt = delete(vet).where(vet.c.veterinarian_id == id)
        conn.execute(stmt)
        return f'Veterinarian with ID {id} deleted', 200
    return f'Veterinarian with ID {id} not found', 404

# curl --request DELETE -v http://localhost:7002/appointments/id
@app.route('/appointments/<id>', methods=['DELETE'])
def delete_appointment(id):
    sel = ap.select().where(ap.c.appointment_id == id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        stmt = delete(ap).where(ap.c.appointment_id == id)
        conn.execute(stmt)
        return f'Appointment with ID {id} deleted', 200
    return f'Appointment with ID {id} not found', 404

# curl --request DELETE -v http://localhost:7002/billings/id
@app.route('/billings/<id>', methods=['DELETE'])
def delete_billing(id):
    sel = bill.select().where(bill.c.billing_id == id)
    result = conn.execute(sel).fetchone()
    if result is not None:
        stmt = delete(bill).where(bill.c.billing_id == id)
        conn.execute(stmt)
        return f'Billing with ID {id} deleted', 200
    return f'Billing with ID {id} not found', 404


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port = port_number)

