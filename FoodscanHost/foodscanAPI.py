#!flask/bin/python

"""
This module is responsible for setting up and maintaining a REST API.
This module listens for HTTP POST requests that contain a JSON object of which a key holds 'barcode'.
The barcode json object is passed to a publisher that gives it to the rest of the backend.
This module then blocks the API until it receives a reply from the rest of the backend.
The reply is a json object in every case. Either a product found, or product not found.

pydoc -w
"""

from flask import Flask, jsonify, abort, request
from flask.ext.cors import CORS, cross_origin
import json
import pika
from pprint import pprint

app = Flask(__name__)

cors = CORS(app, resources={r"/foo": {"origins": "localhost"}})


#FETCH A PRODUCT
#	curl -iv -H "Content-Type: application/json" -d '{"barcode": 7622300026752}' -X POST localhost:5000/api
@app.route('/api', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def fetchProduct():
	"""
	REST API endpoint using python Flask framework
	
	pydoc -w
	"""
	if not request.json or not 'barcode' in request.json:
		abort(400)
	else:
		data = {"barcode": request.json['barcode']}
		message = json.dumps(data)
		publisher2APIgateway(message)
		product = subscriberToPreparer()
		pprint(product)

	return product, 201


def publisher2APIgateway(message):
	"""
	method publishing to rest of backend
	
	pydoc -w
	"""
	print "publish to APIgatewayQueue", message
	#push the barcode message from front end to APIgatewayQueue
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.queue_declare(queue='ToAPIgatewayQueue')
	channel.basic_publish(exchange='', routing_key='ToAPIgatewayQueue', body=message)
	connection.close()
	#block front-end listens by passing control to subscriberToPreparer for product response
	return
	
def subscriberToPreparer():
	"""
	subscriber for a reply from backend micro-services
	
	pydoc -w
	"""
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	
	channel.queue_declare(queue='queueToFront')
	
	def callback(ch, method, properties, response):
		if(response != ''):
			channel.cancel()
			connection.close()
			global product 
			product = response	

	channel.basic_consume(callback, queue='queueToFront', no_ack=True)
	
	channel.start_consuming()
	
	return product
	



if __name__ == '__main__':
        #app.run(debug=True)
        app.run(host='192.168.0.14', debug=True)
