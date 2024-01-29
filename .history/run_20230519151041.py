from flask import Flask, render_template, request
import re
import os
import csv

app = Flask(__name__)

# CSV文件路徑
DATABASE = 'mydatabase.csv'


def get_all_users():
    users = []
    with open('mydatabase.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user = {
                'name': row['name'],
                'age': row['age'],
                'sex': row['sex']
            }
            users.append(user)
    return users

def get_all(table):
    data = []
    with open("%s.csv" % table, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def get_all_tables(database_name):
    tables = []
    csv_filename = f'{database_name}.csv'
    with open(csv_filename, 'r') as file:
        reader = csv.DictReader(file)
        tables = reader.fieldnames
    return tables

def get_all_csv_name():
    tables = []
    for file_name in os.listdir():
        if file_name.endswith('.csv'):
            table_name = os.path.splitext(file_name)[0]
            tables.append(table_name)
    return tables

def add_data(table, data_list):
    with open("%s.csv" % table, 'r+', newline='') as file:
        # fieldnames = ['name', 'age', 'sex']
        print("add_data")
        db_key = file.readline().replace("\n", "").split(",")
        if len(db_key) == len(data_list):
            writer = csv.writer(file)
            writer.writerow(data_list)
        # writer = csv.DictWriter(file, fieldnames=fieldnames)
        # writer.writerow({'name': name, 'age': age, 'sex': sex})


def execute_query(query):
    if query.startswith('SELECT'):
        _, column, _, table = query.split()
        return select_data(column, table)
    elif query.startswith('DELETE'):
        _, _, table, _, condition_column, _, condition_value = query.split()
        delete_data(table, condition_column, condition_value)
        return ['Data deleted successfully.']
    elif query.startswith('INSERT'):
        table = query.split()[2]
        values = re.findall(r'\((.*?)\)', query)[0]
        values_list = [value.strip() for value in values.split(',')]
        add_data(table, values_list)
        return ['Data inserted successfully.']
    elif query.startswith('CREATE'):
        match = re.search(r'CREATE (\w+) \((.*?)\)', query)
        if match:
            table_name = match.group(1)
            columns = [column.strip() for column in match.group(2).split(',')]
            create_table(table_name, columns)
            return ['Table created successfully.']
        else:
            return ['Invalid query. Please check your input.']
    else:
        return ['Invalid query. Please check your input.']


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

def create_table(table_name, columns):
    csv_filename = f'{table_name}.csv'
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)

@app.route('/table/<database_name>')
def show_database(database_name=None):
    if database_name is None:
        database_name = 'mydatabase'
    tables = get_all(database_name)
    if len(tables) != 0:
        keys=tables[0].keys()
    else:
        keys=[]
    return render_template('database.html', database=database_name, tables=tables, keys=keys)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        command = request.form['command']
        results = execute_query(command)
    else:
        results = []

    users = get_all_users()
    # tables = get_all_tables('mydatabase')
    tables = get_all_csv_name()
    print("users")
    print(users)
    print("results")
    print(results)
    return render_template('index.html', users=users, results=results, tables=tables)


if __name__ == '__main__':
    app.run(debug=True)
