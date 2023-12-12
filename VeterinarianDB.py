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

# Creating two tables as dictionaries for the Flask example

veterinarian = [{'veterinarian_id':1, 'veterinarian_first_name':'Josh', 'veterinarian_last_name': 'Smith', 'veterinarian_phone': '0985647123',
                'veterinarian_direction': 'Machala', 'specialization': 'Rabbits'},
				{'veterinarian_id':2, 'veterinarian_first_name':'Priscila', 'veterinarian_last_name': 'Loor', 'veterinarian_phone': '0998563154',
                'veterinarian_direction': 'Tena', 'specialization': 'Dogs'}
]

clients = [{'client_id':1, 'owner_id':1, 'client_name': 'Rocky',
            'client_species': 'Dog',
            'client_breed': 'Bulldog',
			'client_sex': 'Male',
            'client_age': 4,
            'treatment': 'Active'},
			{'client_id':2, 'owner_id':1, 'client_name': 'Vicky',
            'client_species': 'Cat',
            'client_breed': 'Persian',
			'client_sex': 'Female',
            'client_age': 1,
            'treatment': 'Active'},
			{'client_id':3, 'owner_id':2, 'client_name': 'Lucy',
            'client_species': 'Rabbit',
            'client_breed': 'Dutch',
			'client_sex': 'Female',
            'client_age': 3,
            'treatment': 'Finished'}
]

# Get table structures from the database

ap = Table('appointment', metadata, autoload_with=engine)
bill = Table('billing', metadata, autoload_with=engine)
cli = Table('clients', metadata, autoload_with=engine)
ow = Table('owner', metadata, autoload_with=engine)
vet = Table('veterinarian', metadata, autoload_with=engine)

# Alter table Clients to make the column client_age an Integer not null
query = "Alter table clients modify column client_age int not null"
conn.execute(text(query))

# Update Client Age from the Clients table using SQLAlchemy
stmt = cli.update().where(cli.c.client_id == 1).values(client_age = 4)
conn.execute(stmt)

stmt = cli.update().where(cli.c.client_id == 2).values(client_age = 1)
conn.execute(stmt)

stmt = cli.update().where(cli.c.client_id == 3).values(client_age = 3)
conn.execute(stmt)

stmt = cli.update().where(cli.c.client_id == 4).values(client_age = 3)
conn.execute(stmt)

# Update Client Sex from the Clients table using SQLAlchemy
stmt = cli.update().where(cli.c.client_id == 1).values(client_sex = "Male")
conn.execute(stmt)

stmt = cli.update().where(cli.c.client_id == 2).values(client_sex = "Female")
conn.execute(stmt)

stmt = cli.update().where(cli.c.client_id == 3).values(client_sex = "Female")
conn.execute(stmt)

stmt = cli.update().where(cli.c.client_id == 4).values(client_sex = "Male")
conn.execute(stmt)

# To show all the elements in the tables using SQLAlchemy
select_query = select(cli)
pprint.pprint(conn.execute(select_query).fetchall())

select_query = select(ow)
pprint.pprint(conn.execute(select_query).fetchall())

select_query = select(vet)
pprint.pprint(conn.execute(select_query).fetchall())


# To insert a new value into the tables using SQLAlchemy
#ins = cli.insert().values((5, 2, "Pichu", "Cat", "Bengala", "Male", 2, "Active"))
#conn.execute(ins)

# To delete a value of the tables using SQLAlchemy
stmt = delete(cli).where(cli.c.client_name == "Pichu")
conn.execute(stmt)


# Code to show the elements of the table Owners using HTTP
# curl -v http://localhost:7002/owners
@app.route('/owners')
def get_owners():
	select_query = select(ow)
	res = conn.execute(select_query).fetchall()
	return json.dumps([row._asdict() for row in res])


# Code to show the elements of the table Clients using HTTP
# curl -v http://localhost:7002/clients
@app.route('/clients')
def get_clients():
	select_query = select(cli)
	res = conn.execute(select_query).fetchall()
	return json.dumps([row._asdict() for row in res])


# To search a veterinarian according to their ID using HTTP
# curl -v http://localhost:7002/veterinarian/1
@app.route('/veterinarian/<int:id>')
def get_veterinarian(id):
	veterinarian_list = [veterinarian for veterinarian in veterinarian if veterinarian['veterinarian_id'] == id]
	if len(veterinarian_list) == 0:
		return f'Veterinarian with id {id} not found', 404
	return jsonify(veterinarian_list[0])


#To add a new client to the list using HTTP
# curl --header "Content-Type: application/json" --request POST --data "{\"name\": \"Pichu\"}" -v http://localhost:7002/client
@app.route('/client', methods=['POST'])
def post_product():
	# Retrieve the client from the request body
	request_product = request.json

	# Generate an ID for the post
	new_id = max([client['client_id'] for client in clients]) + 1

	#Create a new client
	new_client = {
		'client_id': new_id,
		'owner_id': 2,
		'client_name': request_product['name'],
		'client_species': 'Cat',
		'client_breed': 'Bengala',
		'client_sex': 'Male',
		'client_age': 2,
		'treatment': 'Active'
	}

	# Append the new client to our client list
	clients.append(new_client)

	# Return the new client back to the client
	return jsonify(new_client), 201


# To verify the list of the clients using HTTP
# curl -v http://localhost:7002/client
@app.route('/client')
def get_client():
	return jsonify(clients)


# To update the treatment of the client with id 2 from 'Active' to 'Finished' using HTTP
# curl --header "Content-Type: application/json" --request PUT --data "{\"treatment\": \"Finished\"}" -v http://localhost:7002/clients/2
@app.route('/clients/<int:id>', methods=['PUT'])
def put_client(id):
	# Get the request payload
	updated_client = request.json

	# Find the client with the specified ID
	for client in clients:
		if client['client_id'] == id:
			# Update the client treatment
			client['treatment'] = updated_client['treatment']
			return jsonify(client), 200

	return f'Client with id {id} not found', 404


# To delete a value from the veterinarian table according to their ID using HTTP
# curl --request DELETE -v http://localhost:7002/veterinarian/1
@app.route('/veterinarian/<int:id>', methods=['DELETE'])
def delete_veterinarian(id):
	# Find the veterinarian with the specified ID
	veterinarian_list = [veterinarian for veterinarian in veterinarian if veterinarian['veterinarian_id'] == id]
	if len(veterinarian_list) == 1:
		veterinarian.remove(veterinarian_list[0])
		return f'Veterinarian with id {id} deleted', 200

	return f'Veterinarian with id {id} not found', 404


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port = port_number)

