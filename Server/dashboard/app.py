import requests
import mysql.connector as mysql
import json
from flask import Flask, render_template
from flask import request

app = Flask(__name__)

@app.route('/getDeviceStat')
def jsonDict():

    myString = requests.get("http://getdevicestatservice:8090/getDeviceStat").content
    
    return render_template('template_bootstrap.html', myString=data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8010)