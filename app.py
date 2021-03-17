from flask import Flask, session, redirect, flash, render_template, request, url_for
from markupsafe import escape
from datetime import date
import sqlite3
import pymongo

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Database configuration
conn = sqlite3.connect('library.db')
print("Opened SQLdatabase successfully")
##### THIS LINK NEEDS TO CHANGE TO YOUR OWN LOCAL SERVER , DATABASE NAME , DATABASE COLLECTION #########
# Localised Mongodb -> change the db to your database

# Lundy COnnectionc
client = pymongo.MongoClient(
     "mongodb://127.0.0.1:27017/?compressors=zlib&gssapiServiceName=mongodb")

# Elton connection
# client = pymongo.MongoClient(
#     "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false")
db = client["libraryDatabase"]
collection = db["libraryCollection"]
#######################################################################################################


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/library', methods=['GET', 'POST'])
def library():
    if 'userID' in session:
        return render_template('library.html')
    if request.method == 'POST':
        bookSearch = request.form['bookSearch']
        return redirect(url_for('results', bookSearch=bookSearch))
    return redirect(url_for('login'))

##books in specific
@ app.route('/book/<int:bookid>', methods=['GET', 'POST'])
def bookDetail(bookid):
    #get book detail
    result = list(db.libraryCollection.find({
        '_id' :  bookid
    }))
    #get book availability 
    with sqlite3.connect("library.db") as con:
        cur = con.cursor()
        SQL_command = "SELECT availability, reservedAvailability FROM book WHERE bookID = '" + \
            str(bookid) + "'"
        cur.execute(SQL_command)
        rows = cur.fetchall()
        for row in rows:
            availability = row[0]
            reserved = row[1]
        print(reserved)
        
    return render_template('bookDetail.html', result=result, availability=availability, reserved=reserved)


@app.route('/library/results', methods=['GET', 'POST'])
def results():
    bookSearch = request.form['bookSearch']
    # list(db.libraryCollection.find({"title" : bookSearch }))
    result = list(db.libraryCollection.find({"title" : bookSearch })) ##fuck this
    
    print(result)
    for i in result:
        print(i)
        print("wahat")
    return render_template('results.html', bookSearch=bookSearch, result=result)


@ app.route('/library/results/reservationSuccess', methods=['GET', 'POST'])
def reservationSuccess():
    _id = request.form['_id']
    result = collection.find_one({'_id': int(_id)})
    with sqlite3.connect("library.db") as con:
        cur = con.cursor()
        d = date.today().strftime("%d/%m/%y")
        SQL_command = "INSERT INTO reserve (userID, bookID, reserveDate) VALUES (?,?,?)"
        reserveEntry = (session['userID'], result['_id'], d)
        print(SQL_command)
        cur.execute(SQL_command, reserveEntry)
    con.commit()
    return render_template('reservationSuccess.html', result=result)


@ app.route('/library/results/borrowSuccess', methods=['GET', 'POST'])
def borrowSuccess():
    _id = request.form['_id']
    result = collection.find_one({'_id': int(_id)})
    try:
        collection.find_one_and_update(
            {'_id': int(_id)}, {'$set': {'available': False}})
        print(collection.find_one({'_id': int(_id)}))
    except:
        print("an exception has occured")
    with sqlite3.connect("library.db") as con:
        cur = con.cursor()
        d = date.today().strftime("%d/%m/%y")
        SQL_command = "INSERT INTO loan (userID, bookID, loanID, borrowDate, returnDate) VALUES (?,?,?,?,?)"
        loanEntry = (session['userID'], result['_id'], '', d, '')
        print(SQL_command)
        cur.execute(SQL_command, loanEntry)
    con.commit()
    return render_template('borrowSuccess.html', result=result)


@ app.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('account.html')


@ app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['userID']
            # check if the username is in use before
            with sqlite3.connect("library.db") as con:
                cur = con.cursor()
                SQL_command = "SELECT userName FROM userTable WHERE userName = '" + \
                    str(username) + "'"
                cur.execute(SQL_command)
                rows = cur.fetchall()
                sessionID = ""
                for row in rows:
                    sessionID = row[0]
                    print(sessionID)
                if sessionID != "":
                    flash("Username in use already!")
                    quit()
            email = request.form['email']
            userPassword = request.form['userPassword']
            fName = request.form['fName']
            lName = request.form['lName']
            phoneNum = request.form['phoneNum']
            blockNum = request.form['blockNum']
            streetName = request.form['streetName']
            unitNum = request.form['unitNum']
            postalCode = request.form['postalCode']

            userNewEntry = (username,
                            userPassword,
                            email,
                            fName,
                            lName,
                            phoneNum,
                            blockNum,
                            streetName,
                            unitNum,
                            postalCode)

            print(userNewEntry)
            msg = "Record successfully added"

            with sqlite3.connect("library.db") as con:
                cur = con.cursor()
                SQL_command = "INSERT INTO userTable (userName, userPassword, email, fName, lName, phoneNum, blockNum, streetName, unitNum, postalCode) VALUES (?,?,?,?,?,?,?,?,?,?)"
                print(SQL_command)
                cur.execute(SQL_command, userNewEntry)
            con.commit()
            print("success")
            return redirect(url_for('login'))

        except:
            print("help")

        con.close()
    return render_template('signup.html')

##### START OF LOGIN WORKS FINE #############
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    # return render_template('login.html')
    if request.method == 'POST':
        try:
            username = request.form['username']
            userPassword = request.form['userPassword']
            print("username: " + username + " password " + userPassword)
            if username == "" or userPassword == "":
                flash("Email address of Password is empty!")
                quit()
            with sqlite3.connect("library.db") as con:
                cur = con.cursor()
                SQL_command = "SELECT userName, userPassword FROM userTable WHERE userName = '" + \
                    str(username) + "'"
                cur.execute(SQL_command)
                print(SQL_command)
                rows = cur.fetchall()
                actualpassword = ""
                sessionID = ""
                for row in rows:
                    sessionID = row[0]
                    actualpassword = row[1]
                print("comes here leh password: " + sessionID +
                      " antoher one ius :" + actualpassword)
                print(actualpassword)
                print(userPassword)
                if str(actualpassword) == str(userPassword):
                    print("got leh")
                    session['userID'] = sessionID
                    return redirect(url_for('library'))
                else:
                    flash("wrong password or username")
        except:
            print("help")
    return render_template('login.html')
##### END OF LOGIN WORKS FINE #############


if __name__ == '__main__':
    app.run(debug=True)
