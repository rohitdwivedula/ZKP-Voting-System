from time import time
import hashlib
from urllib.parse import urlparse
import mysql.connector 
import requests
import json
import random 

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        if not self.resolve_conflicts():
            # make genesis block if no other nodes already exist
            self.new_block(previous_hash='1', proof=100)        

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # only when a chain is longer than this chain, it will be replaced
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def verify_transactions(self, voter):
        '''
        Verify all transactions in current_transactions by:
          - checking if the voter has voted before
          -   
        :return: True if our chain was replaced, False if not
        '''
        # check if all transactions pending are valid
        for transaction in self.current_transactions:
            if self.already_voted(transaction['voter']):
                self.current_transactions.remove(transaction)
                print("Removed transaction " + transaction  + " as it is invalid")
        
        if len(self.current_transactions) == 0:
            print("No transactions in queue")
            return False
        
        for transaction in self.current_transactions:
            if transaction['voter'] == voter:
                transaction_to_verify = transaction
                break 

        # use zero knowledge proof to verify what's the vote
        # Interactive zero knowledge proof
        g = 961, p = 997
        # convert string to a number
        x = sum(ord(c) << i*8 for i, c in enumerate(transaction_to_verify['voted_for']))
        y = mod(g, x, p)
        '''BOB (this function) possesses secret information x'''
        for i in range(0,5):
            r = random.randrage(20, 100, 1)
            c = pow(g, r, p) # (g^r) mod p
            cipher1 = pow(g, ((x+r)%(p-1)), p)
            if not verifyChallenge(c, y, p, cipher1):
                print("FATAL ERROR: ZERO KNOWLEDGE PROOF VERIFICATION FAILED")
                return False
        return True

    @staticmethod
    def get_challenge(c, y, p):
        '''ALICE is trying to ascertain that bob has the info'''
        # this is the function that is trying to determine if values are known 
        cipher2 =  (c*y)%p
        if cipher2 == cipher1:
            # Alice is atleast partially convinced that Bob knows x 
            return True
        else:
            return False


    def already_voted(self, voter_id):
        current_index = 0
        while current_index < len(self.chain):
            transactions_in_block = self.chain[current_index]['transactions']
            for transaction in transactions_in_block:
                if transaction['voter'] == voter_id:
                    return True
            current_index += 1
        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, voter, voted_for):
        """
        Creates a new transaction to go into the next mined Block.
        This will not be mined/verified unless we call the mine function.
        It will just sit on the local disk
        :param voter: public key of voter
        :param voted_for: name of the candidate
        :return: The index of the Block that will hold this transaction
        """

        for transaction in self.current_transactions:
            if transaction['voter'] == voter:
                # this voter's vote is already waiting to be mined.
                # therefore, rejected.
                return False
        self.current_transactions.append({
            'voter': voter,
            'voted_for': voted_for
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Proof of Work:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """

        trial = f'{last_proof}{proof}{last_hash}'.encode()
        trial_hash = hashlib.sha256(trial).hexdigest()
        if trial_hash[:4] == "0000":
            print("Hash found: " + trial_hash)
        return trial_hash[:4] == "0000"
