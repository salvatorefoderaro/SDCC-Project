from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
   return format(request.args.get('language'))    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8002)