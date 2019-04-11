from uuid import uuid4
from flask import Flask, jsonify, request, render_template, session
from flask_bower import Bower
from argparse import ArgumentParser, ArgumentTypeError
from classes.blockchain import Blockchain
import random, string
from database import insert_user, authenticate_user

# Setup Argument Parser
parser = ArgumentParser()
parser.add_argument('-p', '--port', default=5000, type= int, help='port to listen on')
args = parser.parse_args()
port = args.port    

# Instantiate the Node
app = Flask(__name__)

# Instantiate the Blockchain
blockchain = Blockchain(port)

@app.route("/")
def main():
    if not session.get('logged_in'):
        return render_template('main.html')
    else:
        return "Hello Boss!"
    

@app.route('/api/mine', methods=['GET'])
def mine(): 
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/api/generate/user', methods=["GET"])
def create_voter():
    username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    print(username)
    print(password)
    if insert_user(username, password):
        user = {
            'username': username,
            'password': password 
        }
        return jsonify(user), 201
    else:
        return jsonify({'Error': 'Unexpected Database Error'}), 400

@app.route('/api/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    print(values)
    # Check that the required fields are in the POST'ed data
    required = ['voter', 'voted_for', 'private_key']
    
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    # Check user credentials by matching private and public keys
    if not authenticate_user(values['voter'], values['private_key']):
        # Status 401: Unauthorized
        print("User does not exist in voter list/incorrect auth")
        return jsonify("Authorization Error"), 401

    # Create a new Transaction, ensure vote of same candidate not in queue
    index = blockchain.new_transaction(values['voter'], values['voted_for'])
    if not index:
        return jsonify("Error: Vote already in Queue"), 406

    # Use zero knowledge proof to verify transaction
    if not blockchain.verify_transactions(values['voter']):
        # if there is a invalid transaction
        # return status code 406: Not Acceptable    
        print("ERROR: Invalid transaction")
        return jsonify("Transaction Error: Invalid trasnaction"), 406
    
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/api/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/api/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/api/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

app.run(host='0.0.0.0', port=port)