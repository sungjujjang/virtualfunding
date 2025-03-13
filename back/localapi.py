from flask import Flask, request, jsonify
from db import *

app = Flask(__name__)

@app.route('/add_money')
def add_moneys():
    id = request.args.get('id')
    money = int(request.args.get('money'))
    result = add_money(id, money)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True, port=1100)