from flask import Flask,flash, render_template, request, url_for
import sqlite3

    
app = Flask(__name__)

conn = sqlite3.connect('database.db')
print("Opened database successfully")


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
            userEmail = request.form['userEmail']
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
                
        except:
            print("uh oh")
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("signupComplete.html", msg=msg)
            con.close()

conn.close()
if __name__ == '__main__':
    app.run(debug=True)
