


import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app



CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8005"

posts = []


def fetch_posts():
	get_chain_address = "{0}/chain".format(CONNECTED_NODE_ADDRESS)
	response = requests.get(get_chain_address)
	if response.status_code == 200:
		content = []
		chain = json.loads(response.content.decode("utf-8"))
		for block in chain["chain"]:
			for tx in block["transactions"]:
				tx["index"] = block["index"]
				tx["hash"] = block["previous_hash"]
				content.append(tx)
		global posts
		posts = sorted(content, key=lambda k: k["timestamp"], reverse=True)


@app.route("/")

def index():
	fetch_posts()
	return render_template("index.html", \
				title="Content-Sharing Blockchain", \
				subtitle="Sphinx Consensus Algorithm", \
				posts=posts, \
				node_address=CONNECTED_NODE_ADDRESS, \
				readable_time=timestamp_to_string)


@app.route("/submit", methods=["POST"])

def submit_textarea():
	post_content = request.form["content"]
	author = request.form["author"]
	post_object = {
		"author" : author,
		"content" : post_content,
	}
	
	new_tx_address = "{0}/new_transaction".format(CONNECTED_NODE_ADDRESS)
	requests.post(new_tx_address, json=post_object, headers={"Content-type" : "application/json"})
	return redirect("/")


def timestamp_to_string(unix_time):
	return datetime.datetime.fromtimestamp(unix_time).strftime("%H:%M")
