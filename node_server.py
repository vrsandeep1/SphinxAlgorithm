from hashlib import sha512
import json
import time

from flask import Flask, request
import requests


class Block:
	def __init__(self, index, transactions, timestamp, previous_hash):
		self.index = index
		self.transactions = transactions
		self.timestamp = timestamp
		self.previous_hash = previous_hash
		self.nonce = 0

	def compute_hash(self):
		block_string = json.dumps(self.__dict__, sort_keys=True)
		return sha512(block_string.encode()).hexdigest()


class Blockchain:
	difficulty = 2
	def __init__(self):
		self.unconfirmed_transactions = [] 
		self.chain = [] 
		self.create_genesis_block()

	def create_genesis_block(self):
		genesis_block = Block(0, [], time.time(), "0")
		genesis_block.hash = genesis_block.compute_hash()
		self.chain.append(genesis_block)

	def add_block(self, block, proof):
		previous_hash = self.last_block.hash
		if (previous_hash != block.previous_hash or not self.is_valid_proof(block, proof)):
			return False
		block.hash = proof
		self.chain.append(block)
		return True

	def mine(self):
		if not self.unconfirmed_transactions:
			return False
		last_block = self.last_block
		new_block = Block(last_block.index + 1, \
					self.unconfirmed_transactions, \
					time.time(), \
					last_block.hash)
		proof = self.proof_of_work(new_block)
		self.add_block(new_block, proof)
		self.unconfirmed_transactions = []
		announce_new_block(new_block)
		return new_block.index

	def proof_of_work(self, block):
		block.nonce = 0
		computed_hash = block.compute_hash()
		while not computed_hash.startswith("0" * Blockchain.difficulty):
			block.nonce += 1
			computed_hash = block.compute_hash()
		return computed_hash

	def add_new_transaction(self, transaction):
		self.unconfirmed_transactions.append(transaction)

	@classmethod
	def check_chain_validity(cls, chain):
		result = True
		previous_hash = "0"
		for block in chain:
			block_hash = block.hash
			delattr(block, "hash")
			if not cls.is_valid_proof(block, block.hash) or previous_hash != block.previous_hash:
				result = False
				break
			block.hash = block_hash
			previous_hash = block_hash
		return result

	@classmethod
	def is_valid_proof(cls, block, block_hash):
		return (block_hash.startswith("0" * Blockchain.difficulty) and block_hash == block.compute_hash())

	@property
	def last_block(self):
		return self.chain[-1]


app = Flask(__name__)
blockchain = Blockchain()
peers = set()

@app.route("/new_transaction", methods=["POST"])
def new_transaction():
	tx_data = request.get_json()
	required_fields = ["author", "content"]
	for field in required_fields:
		if not tx_data.get(field):
			return "Invalid transaction data", 404
	tx_data["timestamp"] = time.time()
	blockchain.add_new_transaction(tx_data)
	return "Success", 201

@app.route("/chain", methods=["GET"])
def get_chain():
	consensus()
	chain_data = []
	for block in blockchain.chain:
		chain_data.append(block.__dict__)
	return json.dumps({"length" : len(chain_data), "chain" : chain_data})

@app.route("/mine", methods=["GET"])
def mine_unconfirmed_transactions():
	result = blockchain.mine()
	if not result:
		return "There are no transactions to mine."
	return "Block #{0} has been mined.".format(result)

@app.route("/add_nodes", methods=["POST"])
def register_new_peers():
	nodes = request.get_json()
	if not nodes:
		return "Invalid data", 400
	for node in nodes:
		peers.add(node)
	return "Success", 201

@app.route("/pending_tx")
def get_pending_tx():
	return json.dumps(blockchain.unconfirmed_transactions)

def consensus():
	global blockchain
	longest_chain = None
	curr_len = len(blockchain.chain)
	for node in peers:
		response = requests.get("http://{0}/chain".format(node))
		length = response.json()["length"]
		chain = response.json()["chain"]
		if length > curr_len and blockchain.check_chain_validity(chain):
			curr_len = length
			longest_chain = chain
	if longest_chain:
		blockchain = longest_chain
		return True
	return False

@app.route("/add_block", methods=["POST"])
def validate_and_add_block():
	block_data = request.get_json()
	block = Block(block_data["index"], \
			block_data["transactions"], \
			block_data["timestamp", block_data["previous_hash"]])
	proof = block_data["hash"]
	added = blockchain.add_block(block, proof)
	if not added:
		return "The block was discarded by the node.", 400
	return "The block was added to the chain.", 201

def announce_new_block(block):
	for peer in peers:
		url = "http://{0}/add_block".format(peer)
		requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))

app.run(port=8005, debug=True)