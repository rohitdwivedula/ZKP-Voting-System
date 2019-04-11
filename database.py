import pymysql
from Crypto.PublicKey import RSA 
'''
DATABASE DESIGN PATTERN
    - 'users' table for storing the list of all active voters. Will contain'
       plaintext usernames and password. In reality, it would be better to save
       the RSA public keys of all users (give users RSA private keys) and use 
       authentication methods to determine uses. Since this is just a demo, we are
       stroing plaintext passwords. 

    - 'nodes' table for storing the mined chain of each node. Contains two
       columns - the port number and the blockchain entire chain. We are assuming that
       the demo will be run on the same system, with two different nodes being hosted
       on different ports of localhost. 
'''

def generate_RSA(bits=2048):
   '''
   Generate an RSA keypair with an exponent of 65537 in PEM format
   param: bits The key length in bits
   Return private key and public key
   '''
   new_key = RSA.generate(bits, e=65537) 
   public_key = new_key.publickey().exportKey("PEM") 
   private_key = new_key.exportKey("PEM") 
   return private_key, public_key

def authenticate_user(usr, pwd):
   db = pymysql.connect("localhost", "rohit", "123456789", "blockchain", unix_socket="/var/run/mysqld/mysqld.sock", port = 0)
   cursor = db.cursor()
   query = "SELECT * FROM users WHERE username = \"" + usr + "\" AND password = \"" + pwd + "\""
   print(query)
   try:
      cursor.execute(query)
      result = cursor.rowcount
      if result == 0:
         return False
      else:
         return True
   except:
      print("Unexpected Auth Error")
      return False

def load_port(port_num):
   db = pymysql.connect("localhost", "rohit", "123456789", "blockchain", unix_socket="/var/run/mysqld/mysqld.sock", port = 0)
   cursor = db.cursor()
   query = "SELECT blockchain from nodes WHERE port = " + port_num
   try:
      cursor.execute(query)
      results = cursor.fetchone()
      print(results)
      for row in results:
         return row[0]
   except:
      return False


def all_ports():
   db = pymysql.connect("localhost", "rohit", "123456789", "blockchain", unix_socket="/var/run/mysqld/mysqld.sock", port = 0)
   cursor = db.cursor()
   query = "SELECT port FROM nodes"
   
   try:
      cursor.execute(query)
      results = cursor.fetchall()
      ports = []
      for row in results:
         ports.append(row[0])
      return ports
   except:
      # handle failure by assuming we're the only valid node
      return []


def insert_user(usr, pwd):
   db = pymysql.connect("localhost", "rohit", "123456789", "blockchain", unix_socket="/var/run/mysqld/mysqld.sock", port = 0)
   cursor = db.cursor()
   rsa_private_key, rsa_public_key = generate_RSA(1024)
   rsa_public_key = rsa_public_key.hex()
   rsa_private_key = rsa_private_key.hex()
   query = "INSERT INTO users(username, password, rsa_public_key, rsa_private_key) VALUES (\"" + usr +"\",\"" + pwd +"\", \"" + rsa_public_key + "\", \"" + rsa_private_key + "\")"
   # print(query)
   print("(Try) Create user:" +  usr)
   try:
      cursor.execute(query)
      db.commit()
      return True
   except:
      db.rollback()
      return False