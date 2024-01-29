from flask import Flask, render_template, request
import csv

app = Flask(__name__)

# CSV文件路徑
DATABASE = 'database.csv'


def get_all_users():
    users = []
    with open(DATABASE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append(row)
    return users


def add_user(name, age, sex):
    with open(DATABASE, 'a', newline='') as file:
        fieldnames = ['name', 'age', 'sex']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({'name': name, 'age': age, 'sex': sex})


def execute_query(query):
    if query.startswith('SELECT'):
        _, column, _, table = query.split()
        return select_data(column, table)
    elif query.startswith('DELETE'):
        _, _, table, _, condition_column, _, condition_value = query.split()
        delete_data(table, condition_column, condition_value)
    elif query.startswith('INSERT'):
        _, _, table, _, values = query.split()
        values_list = values.split(',')
        values_list = [value.strip() for value in values_list]
        add_user(*values_list)
    else:
        return []


def select_data(column, table):
    data = []
    with open(DATABASE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if column == '*':
                data.append(row)
            elif column in row:
                data.append({column: row[column]})
    return data


def delete_data(table, condition_column, condition_value):
    with open(DATABASE, 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    filtered_rows = [row for row in rows if row.get(condition_column) == condition_value]

    with open(DATABASE, 'w', newline='') as file:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        command = request.form['command']
        results = execute_query(command)
    else:
        results = []

    users = get_all_users()
    return render_template('index.html', users=users, results=results)


if __name__ == '__main__':
    app.run(debug=True)
