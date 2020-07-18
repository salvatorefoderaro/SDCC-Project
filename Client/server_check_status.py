from flask import Flask, request #import main Flask class and request object
import requests

app = Flask(__name__) #create the Flask app

@app.route('/checkStatus', methods=['GET'])
def query_example():
    return "I'm alive"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=7000) #run app in debug mode on port 5000