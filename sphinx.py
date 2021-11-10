from hashlib import sha256
import json
import time
from flask import Flask, request
import requests

class SphinxBlock:
	def __init__(self, index, transactions, timestamp, previous_hash, retry, timeout):
		self.index = index
		self.transactions = transactions
		self.timestamp = timestamp
		self.previous_hash = previous_hash
		self.nonce = 0
		self.retry = retry
		self.timeout = timeout

	def compute_hash(self):
		block_string = json.dumps(self.__dict__, sort_keys=True)
		return sha256(block_string.encode()).hexdigest()


class Blockchain:
	def __init__(self,difficulty):
		self.unconfirmed_transactions = [] 
		self.chain = [] 
		self.create_genesis_block()
		self.difficulty = difficulty
	
	def is_valid_proof(self, block, block_hash):
		if(not (block_hash.startswith("0" * self.difficulty) and block_hash == block.compute_hash())):
			while(block.retry != 0):
				self.prepare(self, block, block_hash)
				block.retry -= 1
			return False
		else:
			return True


	def create_genesis_block(self):
		genesis_block = SphinxBlock(0, [], time.time(), "0",2,5)
		genesis_block.hash = genesis_block.compute_hash()
		self.chain.append(genesis_block)

	def pre_prepare(self, transaction):
		self.unconfirmed_transactions.append(transaction)

	def prepare(self, block, proof):
		previous_hash = self.last_block.hash
		if (previous_hash != block.previous_hash or not self.is_valid_proof(block, proof)):
			return False
		block.hash = proof
		self.chain.append(block)
		return True

	def commit(self):
		if not self.unconfirmed_transactions:
			return False
		last_block = self.last_block
		new_block = SphinxBlock(last_block.index + 1, \
					self.unconfirmed_transactions, \
					time.time(), \
					last_block.hash,2,5)
		proof = self.sphinx_consensus(new_block)
		self.prepare(new_block, proof)
		self.unconfirmed_transactions = []
		return new_block.index

	def sphinx_consensus(self, block):
		block.nonce = 0
		computed_hash = block.compute_hash()
		start = time.time()
		while not computed_hash.startswith("0" * self.difficulty):
			block.nonce += 1
			computed_hash = block.compute_hash()
			if(time.time() - start > block.timeout * 60):
				return None
		return computed_hash


	@property
	def last_block(self):
		return self.chain[-1]

if(__name__ == "__main__"):
	for difficulty in range(1,11):
		temp_blockchain = Blockchain(difficulty=difficulty)
		temp_blockchain.pre_prepare("Content")
		start = time.time()
		temp_blockchain.commit()
		end = time.time()
		print(difficulty, end-start)
	
