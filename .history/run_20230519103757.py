from flask import Flask, render_template, request
import csv

app = Flask(__name__)

DATABASE = 'database.csv'


def get_all_users():
    users = []
    with open(DATABASE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append(row)
    return users


def add_user(name, email):
    with open(DATABASE, 'a', newline='') as file:
        fieldnames = ['name', 'email']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({'name': name, 'email': email})


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        add_user(name, email)
    
    users = get_all_users()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)
