# Foodscan
Cordova app that scans barcodes on food elements and retrieves their nutritional information

Frontend:
>Cordova
-cordova.plugins.barcodeScanner to scan barcodes
-Javascript template engine that loads UI

Installing
Enter cordova run android in root directory

Backend:
>Python: 
-flask for HTTP
-Pika for message passing
>RabbitMQ
>cURL cmd

FoodscanAPI.py
-Sets up a local network (LAN) api access point that the Cordova client can pass data to. (Set ip to computer ip at bottom of method)
-Passes received REST request data to APIgateway.py

APIgateway.py
-A dummy micro service that can be used to scale the backend.
-Passes REST request data to OFFapiHandler.py

OFFapiHandler.py
-Constructs an HTTP request and initiates the request using OS level cURL cmd.
-Data is requested from the api at: world.openfoodfacts.org
-Response from world.openfoodfacts.org is passed to responsePreparer.py micro service

responsePreparer.py
-Deconstructs JSON data from world.openfoodfacts.org and reconstructs a JSON data load specific to the applications needs.
-Passes the ready response back to FoodscanAPI.py which was blocked.

![FoodScan](https://github.com/iojupiter/Foodscan/blob/master/Screenshot%202023-04-05%20at%2015.49.17.png?raw=true)
