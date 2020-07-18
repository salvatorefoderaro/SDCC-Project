from flask import Flask, request #import main Flask class and request object
import requests

app = Flask(__name__) #create the Flask app

@app.route('/testGet', methods=['GET'])
def query_example():
    return request.args.get('deviceID') #if key doesn't exist, returns None

@app.route('/testPost', methods=['POST'])
def formexample():
    input_json = request.get_json(force=True) 
    # force=True, above, is necessary if another developer 
    # forgot to set the MIME type to 'application/json'
    return input_json

@app.route('/testGet')
def testGet():
    try:
        res = requests.get('http://localhost:5000/testGet?deviceID=10')
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return "Errore nella chiamata alla funzione get"
    return res.text

@app.route('/testPost') 
def jsonexample():
    dictToSend = {'question':'what is the answer?'}
    try:
        res = requests.post('http://localhost:5000/testPost', json=dictToSend)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return "Errore nella chiamata alla funzione post"
    return res.text

if __name__ == '__main__':
    app.run(debug=True, port=5000) #run app in debug mode on port 5000