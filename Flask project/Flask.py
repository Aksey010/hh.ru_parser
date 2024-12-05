from flask import Flask, render_template, request
from hh_api import hh_parser
import json

app = Flask(__name__)
print(app.name)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/form")
def form():
    return render_template('form.html')


@app.route('/form/result', methods=['POST'])
def sumbit():
    vac = request.form['vacancy']
    city = request.form['city']
    hh_parser(vacancy=vac, city=city)

    with open('result.json', mode='r') as f:
        data = json.load(f)
        print(data)

    return render_template('results.html', **data)


@app.route("/contacts")
def contacts():
    return render_template('contacts.html')

if __name__ == '__main__':
    app.run(debug=True)
