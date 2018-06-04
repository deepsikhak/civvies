from flask import Flask, jsonify, request, json, render_template
from data import Categories

app = Flask(__name__)

Categories = Categories()


@app.route('/', methods=['GET'])
def getHome():
    return render_template('home.html')


@app.route('/whats-new', methods=['GET'])
def whatsnew():
    return render_template('whats-new.html')

@app.route('/categories', methods=['GET'])
def categories():
    return render_template('categories.html', categories = Categories)

@app.route('/category/<string:id>/', methods=['GET'])
def category(id):
    return render_template('category.html', id=id)

if __name__ == '__main__':
    app.run(host="localhost", debug=True, port=5001)