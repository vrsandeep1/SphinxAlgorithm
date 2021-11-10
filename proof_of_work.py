from hashlib import sha256
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
		return sha256(block_string.encode()).hexdigest()


class Blockchain:
	
	def __init__(self,difficulty):
		self.unconfirmed_transactions = [] 
		self.chain = [] 
		self.create_genesis_block()
		self.difficulty = difficulty

	def create_genesis_block(self):
		genesis_block = Block(0, [], time.time(), "0")
		genesis_block.hash = genesis_block.compute_hash()
		self.chain.append(genesis_block)

	def add_block(self, block, proof):
		previous_hash = self.last_block.hash
		if (previous_hash != block.previous_hash):
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
		return new_block.index

	def proof_of_work(self, block):
		block.nonce = 0
		computed_hash = block.compute_hash()
		while not computed_hash.startswith("0" * self.difficulty):
			block.nonce += 1
			computed_hash = block.compute_hash()
		return computed_hash

	def add_new_transaction(self, transaction):
		self.unconfirmed_transactions.append(transaction)

	

	@property
	def last_block(self):
		return self.chain[-1]

if(__name__ == "__main__"):
	for difficulty in range(1,11):
		temp_blockchain = Blockchain(difficulty=difficulty)
		temp_blockchain.add_new_transaction(None)
		start = time.time()
		temp_blockchain.mine()
		end = time.time()
		print(difficulty, end-start)
	
