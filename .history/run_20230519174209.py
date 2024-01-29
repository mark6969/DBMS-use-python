from flask import Flask, render_template, request, session, redirect
import re
import os
import csv

app = Flask(__name__)
app.secret_key = 'secret-key'  # 設定Session的密鑰
login = False


# 設定預先設定的帳號密碼
USERS = {
    'user': 'password',
    'admin': 'admin123'
}

# 普通使用者權限
USER_PERMISSIONS = {
    'SELECT': True,
    'UPDATE': False,
    'DELETE': False,
    'CREATE': False,
    'DELETE TABLE': False
}

# 管理員權限
ADMIN_PERMISSIONS = {
    'SELECT': True,
    'UPDATE': True,
    'DELETE': True,
    'CREATE': True,
    'DELETE TABLE': True
}


def get_all(table):
    data = []
    with open("DBs/%s.csv" % table, 'r') as file:
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
    for file_name in os.listdir("./DBs"):
        if file_name.endswith('.csv'):
            table_name = os.path.splitext(file_name)[0]
            tables.append(table_name)
    return tables


def add_data(table, data_list):
    with open("DBs/%s.csv" % table, 'r+', newline='') as file:
        db_key = file.readline().replace("\n", "").split(",")
        if len(db_key) == len(data_list):
            writer = csv.writer(file)
            writer.writerow(data_list)
            return True
        return False


def execute_query(query):
    if query.startswith('SELECT'):
        _, column, _, table = query.split()
        return select_data(column, table)
    elif query.startswith('DELETE TABLE'):
        _, _, table = query.split()
        os.remove("DBs/%s.csv" % table)
        return ['DB deleted successfully.']
    elif query.startswith('DELETE'):
        _, _, table, _, condition_column, _, condition_value = query.split()
        delete_data(table, condition_column, condition_value)
        return ['Data deleted successfully.']
    elif query.startswith('INSERT'):
        table = query.split()[2]
        values = re.findall(r'\((.*?)\)', query)[0]
        values_list = [value.strip() for value in values.split(',')]
        if add_data(table, values_list):
            return ['Data inserted successfully.']
        else:
            return ['Data inserted error']
    elif query.startswith('CREATE'):
        match = re.search(r'CREATE (\w+) \((.*?)\)', query)
        if match:
            table_name = match.group(1)
            columns = [column.strip() for column in match.group(2).split(',')]
            create_table(table_name, columns)
            return ['Table created successfully.']
        else:
            return ['Invalid query. Please check your input.']
    elif query.startswith('UPDATE'):
        _, table, _, column, _, value, _, condition_column, _, condition_value = query.split()
        update_data(table, column, value, condition_column, condition_value)
        return ['Data updated successfully.']
    else:
        return ['Invalid query. Please check your input.']


def select_data(column, table):
    data = []
    with open("DBs/%s.csv" % table, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if column == '*':
                data.append(row)
            elif column in row:
                data.append(row[column])
    return data


def delete_data(table, condition_column, condition_value):
    with open("DBs/%s.csv" % table, 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    filtered_rows = [row for row in rows if row.get(condition_column) != condition_value]

    with open("DBs/%s.csv" % table, 'w', newline='') as file:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)


def create_table(table_name, columns):
    csv_filename = f'{table_name}.csv'
    with open("./DBs/%s" % csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)


def update_data(table, column, value, condition_column, condition_value):
    with open("DBs/%s.csv" % table, 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    updated_rows = []
    for row in rows:
        if row.get(condition_column) == condition_value:
            row[column] = value
        updated_rows.append(row)

    with open("DBs/%s.csv" % table, 'w', newline='') as file:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)


@app.route('/table/<database_name>')
def show_database(database_name=None):
    if database_name is None:
        database_name = session.get('database_name')
    tables = get_all_tables(database_name)
    return render_template('table.html', tables=tables)


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' not in session or not session['username']:
        return redirect('/login')
    if request.method == 'POST':
        command = request.form['command']
        if 'username' not in session or not session['username']:
            return redirect('/login')
        username = session['username']
        if username == 'admin':
            permissions = ADMIN_PERMISSIONS
        else:
            permissions = USER_PERMISSIONS
        if not has_permission(command, permissions):
            return 'Permission denied'
        results = execute_query(command)
        return render_template('index.html', results=results)
    elif request.method == 'GET':
        if 'username' in session and session['username']:
            login = True
            return redirect('/')
        else:
            return redirect('/login')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect('/')
        else:
            return 'Invalid credentials'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


def has_permission(command, permissions):
    # 解析指令
    command_parts = command.split()
    if command_parts[0] not in permissions:
        return False
    # 若是 SELECT 指令，則允許
    if command_parts[0] == 'SELECT':
        return True
    # 檢查指令權限
    return permissions[command_parts[0]]


if __name__ == '__main__':
    app.run(debug=True)

