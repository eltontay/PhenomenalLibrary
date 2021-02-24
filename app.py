from flask import Flask, session, redirect, flash, render_template, request, url_for
from markupsafe import escape
import sqlite3
import pymongo

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Database configuration
conn = sqlite3.connect('database.db')
print("Opened SQLdatabase successfully")
# my trial server
client = pymongo.MongoClient("mongodb+srv://admin:admin@phenomcluster.1j72v.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["phenomLibrary"]
collection = db["libraryBooks"]


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # return render_template('login.html')
    if request.method == 'POST':
        try:
            userEmail = request.form['userEmail']
            userPassword = request.form['userPassword']
            if userEmail == "" or userPassword == "":
                quit()
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                SQL_command = "SELECT userID, userPassword FROM usersTable WHERE userEmail = '" + str(userEmail)+ "'"
                cur.execute(SQL_command)
                rows = cur.fetchall()
                actualpassword = ""
                sessionID = ""
                for row in rows:
                    sessionID = row[0]
                    actualpassword = row[1]
                if str(actualpassword) == str(userPassword):
                    session['userID'] = sessionID
                    return redirect(url_for('library'))
                else:
                    flash("wrong password or username")
        except:
           flash("Email address of Password is empty!")
    return render_template('login.html')
        

@app.route('/library', methods=['GET', 'POST'])
@app.route('/')
def library():
    if 'userID' in session:
        return render_template('library.html')
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('account.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            userEmail = request.form['userEmail']
            # check if the email is in use before
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                SQL_command = "SELECT userID FROM usersTable WHERE userEmail = '" + str(userEmail)+ "'"
                cur.execute(SQL_command)
                rows = cur.fetchall()
                sessionID = ""
                for row in rows:
                    sessionID = row[0]
                if sessionID != "":
                    quit()
            userPassword = request.form['userPassword']
            userFirstName = request.form['userFirstName']
            userLastName = request.form['userLastName']
            userPhoneNum = request.form['userPhoneNum']
            userStreetName = request.form['userStreetName']
            userBlockNum = request.form['userBlockNum']
            userStreetName = request.form['userStreetName']
            userPostalCode = request.form['userPostalCode']

            userNewEntry = (userEmail,
                            userPassword,
                            userFirstName,
                            userLastName,
                            userPhoneNum,
                            userStreetName,
                            userBlockNum,
                            userPostalCode)

            print(userNewEntry)
            msg = "Record successfully added"

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                SQL_command = "INSERT INTO usersTable (userEmail,"\
                                                    "userPassword,"\
                                                    "userFirstName,"\
                                                    "userLastName,"\
                                                    "userPhoneNum,"\
                                                    "userStreetName,"\
                                                    "userBlockNum,"\
                                                    "userPostalCode) VALUES (?,?,?,?,?,?,?,?)"
                print(SQL_command)
                cur.execute(SQL_command, userNewEntry)
            con.commit()
            return redirect(url_for('login'))
                
        except:
            flash("Email in use already!")

        con.close()
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
