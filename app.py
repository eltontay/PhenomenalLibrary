import sqlite3
from flask import Flask, render_template, request, url_for

conn = sqlite3.connect('database.db')
print "Opened database successfully!"

conn.execute('CREATE TABLE user (username VARCHAR(20), password VARCHAR(20), firstname TEXT, lastname TEXT, address1 VARCHAR(40), address2 VARCHAR(40), postal INTEGER) ')
print "Table created successfully!"

conn.close()
app = Flask(__name__)

# trial comment for git push


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/library', methods=['GET', 'POST'])
def library():
    return render_template('library.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


@app.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('account.html')


@app.route('/signupComplete', methods=['GET', 'POST'])
def signupComplete():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            firstName = request.form['firstname']
            lastName = request.form['lastname']
            address1 = request.form['address1']
            address2 = request.form['address2']
            postal = request.form['postal']

            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO user (username,password,firstname,lastname,address1,address2,postal) VALUES (?,?,?,?,?,?,?), (username,password,firstname,lastname,address1,address2,postal) ")
                con.commit()
                msg = "User Successfully Added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("signupComplete.html", msg=msg)
            con.close()


if __name__ == '__main__':
    app.run(debug=True)
