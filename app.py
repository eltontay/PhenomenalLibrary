from flask import Flask, session, redirect, flash, render_template, request, url_for
from markupsafe import escape
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_mysqldb import MySQL
import datetime
import pymongo
import pymysql

app = Flask(__name__, template_folder='templates')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# # Database SQLAlchemy
engine = create_engine("mysql+pymysql://root:22dd22dd@localhost/library") ## change this to your password
engine.connect()

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '22dd22dd' ## change this to your password
app.config['MYSQL_DB'] = 'library'

mysql = MySQL(app)


##### THIS LINK NEEDS TO CHANGE TO YOUR OWN LOCAL SERVER , DATABASE NAME , DATABASE COLLECTION #########
# Localised Mongodb -> change the db to your database

# Lundy COnnectionc
client = pymongo.MongoClient(
    "mongodb://127.0.0.1:27017/?compressors=zlib&gssapiServiceName=mongodb")

# Elton Connection
# client = pymongo.MongoClient(
#     "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false")

# #YX Connection
# client = pymongo.MongoClient(
#     "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false"
# )

MongoDb = client["libraryDatabase"]
collection = MongoDb["libraryCollection"]

# books in specific


##############################################################################################################
#                                   START OF ACCOUNT PAGE and Functionality
##############################################################################################################

##### START OF Library WORKS FINE #############


@ app.route('/library', methods=['GET', 'POST'])
def library():
    if 'userID' in session:
        if (session['admin'] == 1):
            admin = True
            return render_template('library.html',admin=admin)
        else:
            return render_template('library.html')
    if request.method == 'POST':
        bookSearch = request.form['bookSearch']
        return redirect(url_for('results', bookSearch=bookSearch))
    return redirect(url_for('login'))
##### END OF library WORKS FINE #############


@ app.route('/usersOverview',methods=['GET','POST'])
def usersOverview():
    return render_template('usersOverview.html')


@ app.route('/book/<int:bookid>', methods=['GET', 'POST'])
def bookDetail(bookid):
    # get book detail
    result = list(MongoDb.libraryCollection.find({'_id':  bookid}))
    print(bookid)
    # get book availability
    with engine.connect() as con:
        userHasBooks = str(bookid) in refreshBorrowlisiting(
            con) or str(bookid) in refreshReservelisiting(con)
        print(userHasBooks)
        SQL_command = "SELECT availability, reservedAvailability FROM book WHERE bookID = '" + \
        str(bookid) + "'"
        print(SQL_command)
        rs = con.execute(SQL_command)
        print(rs)
        for row in rs:
            availability = row[0]
            reserved = row[1]
            print(row)
            print(availability)
            print(reserved)
    return render_template('bookDetail.html', result=result, availability=availability, reserved=reserved, userHasBooks=userHasBooks)


@app.route('/library/results', methods=['GET', 'POST'])
def results():
    with engine.connect() as con:
        bookSearch = request.form['bookSearch']
        bookAuthor = request.form['author']
        bookCategory = request.form['category']
        bookYear = request.form['year']
        if bookSearch == "" and bookAuthor == "" and bookCategory == "" and bookYear == "":
            flash("Please input at least one query")
            quit()
        availReserve = []
        result = list(collection.find({
            "title": {
                "$regex": bookSearch,
                "$options": "i"
            },
            "authors": {
                "$regex": bookAuthor,
                "$options": "i"
            },
            "categories": {
                "$regex": bookCategory,
                "$options": "i"
            },
            "publishedDate":
            {
                "$regex": bookYear,
                "$options": "i"
            }
        }))
        for r in result:
            print(r['_id'])
            SQL_command1 = "SELECT availability, reservedAvailability FROM book WHERE bookID = '" + str(r['_id']) + "'"
            rs1 = con.execute(SQL_command1)
            for row in rs1:
                if (row[0] == 1):
                    availReserve.append("Available to book!")
                elif (row[1] == 1):
                    SQL_command2 = "SELECT dueDate FROM loan WHERE bookID = '" + str(r['_id']) + "'"
                    print(SQL_command2)
                    rs2 = con.execute(SQL_command2)
                    for i in rs2:
                        availReserve.append("Available to reserve! Book will be available from " + str(i[0]))
                else :
                    SQL_command3 = "SELECT dueDate FROM loan WHERE bookID = '" + str(r['_id']) + "'"
                    print(SQL_command3)
                    rs3 = con.execute(SQL_command3)
                    for i in rs3:
                        availReserve.append("Not Available to reserve! Book will be available from " + str(i[0]))
        return render_template('results.html', bookSearch=bookSearch, result=result,availReserve=availReserve)
    return render_template('library.html')


@ app.route('/library/results/reservationSuccess', methods=['GET', 'POST'])
def reservationSuccess():
    _id = request.form['_id']
    result = list(MongoDb.libraryCollection.find({
        '_id':  int(_id)
    }))
    with engine.connect() as con:
        # check if he reserved more than 4 books anot
        SQL_command1 = "SELECT COUNT(endDate IS NULL) AS NumberOfBooks FROM reserve WHERE userID =  '" + \
            str(session['userID']) + "'"
        print(SQL_command1)
        rs = con.execute(SQL_command1)
        value = 0
        for r in rs:
            print(r[0])
            value = r[0]
        if value >= 4:
            return render_template('borrowFail.html', transactionType="reserve")

        # first update book status
        SQL_command2 = "UPDATE Book SET reservedAvailability = FALSE WHERE bookID = '" + \
            str(_id) + "'"
        print(SQL_command2)
        con.execute(SQL_command2)

        # update loan status
        d = date.today().strftime("%Y-%m-%d")
        SQL_command3 = "INSERT INTO reserve (userID, bookID, reserveDate, endDate) VALUES (" + str(session['userID']) + "," + str(_id) + ",'" + str(d) + "', NULL)"
        # loanEntry = (session['userID'], str(_id), d)
        print(SQL_command3)
        con.execute(SQL_command3)   
        notification = "Your reservation for " + \
            result[0]['title'] + " is successful!"
    return render_template('notification.html', notification=notification, bookTitle=result[0])


@ app.route('/library/results/borrowSuccess', methods=['GET', 'POST'])
def borrowSuccess():
    _id = request.form['_id']
    result = list(MongoDb.libraryCollection.find({
        '_id':  int(_id)
    }))
    with engine.connect() as con:
        if checkBorrowMoreThanFour(con, session['userID']):
            notification = "Your borrowing of " + \
                result[0]['title'] + \
                " is unsuccessful. You have reached your borrowing limit of 4 books."
            return render_template('notification.html', notification=notification, bookTitle=result[0])

        # first update book status
        borrowBookBaseOnID(con, _id)
    notification = "Your borrowing of "+result[0]['title'] + " is successful!"
    return render_template('notification.html', notification=notification, bookTitle=result[0])


##############################################################################################################
#                                   END OF Library PAGE and Functionality
##############################################################################################################


##############################################################################################################
#                                   START OF ACCOUNT PAGE and Functionality
##############################################################################################################

@ app.route('/account', methods=['GET', 'POST'])
def account():
    with engine.connect() as con:
        currBooksID = refreshBorrowlisiting(con)
        borrowedbooks = []
        currDates = refreshDateslisting(con)
        today = date.today().strftime("%Y-%m-%d")
        overDue = []
        running = 0
        for book in currBooksID:
            borrowedbooks.append(
                list(MongoDb.libraryCollection.find({'_id':  int(book)})))
            d1 = datetime.datetime.strptime(str(currDates[running][1]), "%Y-%m-%d")
            d2 = datetime.datetime.strptime(str(today), "%Y-%m-%d")
            if ((d2-d1).days > 0):
                overDue.append('Overdue')
                # check if fine has been added, if not then add
                if(refreshFineListing(con)):
                    SQL_command = "INSERT INTO fine (userID,fineCreationDate,fineAmount) VALUES (" + str(session['userID']) + ",'" + str(d2) + "'," + str(1) + ")"
                    con.execute(SQL_command)
            else:
                overDue.append('Not Overdue')
            running += 1
        currReservedID = refreshReservelisiting(con)
        reservedBooks = []
        for book in currReservedID:
            reservedBooks.append(
                list(MongoDb.libraryCollection.find({'_id':  int(book)})))
        fine = calculateFine(con)
    return render_template('account.html', borrowedbooks=borrowedbooks, reservedBooks=reservedBooks, currDates=currDates, overDue=overDue, fine=fine)


@ app.route('/extendLoan', methods=['GET', 'POST'])
def extendLoan():
    _id = request.form['_id']
    result = list(MongoDb.libraryCollection.find({
        '_id':  int(_id)
    }))

    with engine.connect() as con:

        # check if can extend Loan
        SQL_command1 = "SELECT reservedAvailability from book WHERE bookID = '" + \
            str(_id) + "'"
        rs1 = con.execute(SQL_command1)
        for row in rs1:
            ISreserved = row[0]

        if not ISreserved:
            notification = "Sorry, this book has been reserved and the loan cannot be extended"
            return render_template('notification.html', notification=notification, bookTitle=result[0])

        SQL_command2 = "SELECT loanID, dueDate, borrowDate from loan WHERE userID = '" + session['userID'] + "'" \
            "AND bookID = '" + str(_id) + "'" \
            "AND returnDate IS NULL "
        rs2 = con.execute(SQL_command2)
        for row in rs2:
            loanID = row[0]
            dueDate = row[1]
            borrowDate = row[2]

        # check if it has been extended before
        if days_between(borrowDate, dueDate):
            notification = "Sorry, this book has been extended before"
            return render_template('notification.html', notification=notification, bookTitle=result[0])

        dd = datetime.datetime.strptime(str(dueDate), "%Y-%m-%d") + datetime.timedelta(days=28)
        dd = dd.strftime("%Y-%m-%d")

        # update date base on ID
        SQL_command3 = "UPDATE loan SET dueDate = (?) WHERE loanID = '" + str(
            loanID) + "'"
        con.execute(SQL_command3, [dd])
        notification = result[0]['title'] + " has been successfully extended"
    return render_template('notification.html', notification=notification, bookTitle=result[0])


@ app.route('/returnBook', methods=['GET', 'POST'])
def returnBook():
    _id = request.form['_id']
    result = list(MongoDb.libraryCollection.find({
        '_id':  int(_id)
    }))
    with engine.connect() as con:
        # Get Loan ID
        SQL_command = "SELECT loanID from loan WHERE userID = '" + session['userID'] + "'" \
            "AND bookID = '" + str(_id) + "'" \
            "AND returnDate IS NULL"
        rs= con.execute(SQL_command)
        for row in rs:
            loanID = row[0]

        # update date base on ID
        SQL_command = "UPDATE loan SET returnDate = CURRENT_TIMESTAMP WHERE loanID = '" + \
            str(loanID) + "'"
        con.execute(SQL_command)

        # Update the return Date
        SQL_command = "UPDATE book SET availability = TRUE WHERE bookID = '" + \
            str(_id) + "'"
        con.execute(SQL_command)

        # Calculate Fine if have
        # make sure that reservation working
        notification = result[0]['title'] + " has been returned!"
    return render_template('notification.html', notification=notification, bookTitle=result[0])


@ app.route('/cancelReservation', methods=['GET', 'POST'])
def cancelReservation():
    _id = request.form['_id']
    result = list(MongoDb.libraryCollection.find({
        '_id':  int(_id)
    }))
    with engine.connect() as con:
        cancelReservationBaseOnIp(con, _id)
        # make sure that reservation working
        notification = " Your reservation for " + \
            result[0]['title'] + " has been cancelled!"
    return render_template('notification.html', notification=notification, bookTitle=result[0])


@ app.route('/reserveToBorrow', methods=['GET', 'POST'])
def reserveToBorrow():
    _id = request.form['_id']
    result = list(MongoDb.libraryCollection.find({
        '_id':  int(_id)
    }))
    with engine.connect() as con:
    # first check if you have more than 4 books
        if checkBorrowMoreThanFour(con, session['userID']):
            notification = "Your request to borrow " + \
                result[0]['title'] + \
                " is unsuccessful. You already borrowed more than 4 books"
            return render_template('notification.html', notification=notification, bookTitle=result[0])

        # check if the books is available
        print(checkBookAvail(con, _id))
        if not checkBookAvail(con, _id):
            notification = "Currently " + \
                result[0]['title'] + " is not available and still on loan"
            return render_template('notification.html', notification=notification, bookTitle=result[0])

        # end reservation
        # book is avail and less than four books
        borrowBookBaseOnID(con, _id)
        notification = "Your borrowing for "+result[0]['title'] + " is successful!"
    return render_template('notification.html', notification=notification, bookTitle=result[0])

##############################################################################################################
#                                   END OF ACCOUNT PAGE and Functionality
##############################################################################################################


##############################################################################################################
#                                   Start OF Account creation and login
##############################################################################################################

##### START OF SignUp WORKS FINE #############
@ app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        with engine.connect() as con:
            try:
                username = request.form['userID']
                # check if the username is in use before
                SQL_command1 = "SELECT userName FROM userTable WHERE userName = '" + \
                    str(username) + "'"
                rs = con.execute(SQL_command1)
                sessionID = ""
                for row in rs:
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
                                postalCode,
                                '0')

                print(userNewEntry)
                SQL_command2 = "INSERT INTO userTable (userName, userPassword, email, fName, lName, phoneNum, blockNum, streetName, unitNum, postalCode, admin) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
                print(SQL_command2)
                con.execute(SQL_command2, userNewEntry)
                return redirect(url_for('login'))
            except:
                print("help") 
    return render_template('signup.html')
##### End OF SignUp WORKS FINE #############

##### START OF LOGIN WORKS FINE #############


@ app.route('/')
@ app.route('/login', methods=['GET', 'POST'])
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
            with engine.connect() as con:
                SQL_command = "SELECT userID, userPassword, admin FROM userTable WHERE userName = '" + \
                    str(username) + "'"
                rs = con.execute(SQL_command)
                actualpassword = ""
                sessionID = ""
                admin = ""
                for row in rs:
                    sessionID = str(row[0])
                    actualpassword = row[1]
                    admin = row[2]
                if str(actualpassword) == str(userPassword):
                    session['userID'] = sessionID
                    session['admin'] = admin
                    return redirect(url_for('library'))
                else:
                    flash("wrong password or username")
        except:
            print("help")
    return render_template('login.html')
##### END OF LOGIN WORKS FINE #############

##### START OF Logout WORKS FINE #############


@ app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))
##### END OF Logout WORKS FINE #############

##############################################################################################################
#                                   END OF Account creation and login
##############################################################################################################


def calculateFine(cur):
    SQL_command = "SELECT fineAmount FROM fine WHERE userID = '" + \
        session['userID'] + "'"
    rs = cur.execute(SQL_command)
    total = 0
    for row in rs:
        total += row[0]
    return total


def refreshFineListing(cur):
    SQL_command = "SELECT fineCreationDate FROM fine WHERE userID = '" + \
        session['userID'] + "'"
    rs = cur.execute(SQL_command)
    d = date.today().strftime("%Y-%m-%d")
    for row in rs:
        if (row[0] == d):
            return False
    return True


def refreshDateslisting(cur):
    SQL_command = "SELECT borrowDate, dueDate FROM loan WHERE returnDate IS NULL AND userID = '" + \
        session['userID'] + "'"
    rs = cur.execute(SQL_command)
    result = []
    for row in rs:
        result.append(list(row))
    return result


def refreshBorrowlisiting(cur):
    # get additional information about the borrowed books they hold and store in a variable
    SQL_command = "SELECT bookID FROM loan WHERE returnDate IS NULL AND userID = " + str(session['userID'])
    print(SQL_command)
    rs = cur.execute(SQL_command)
    result = []
    for row in rs:
        print(row[0])
        result.append(str(row[0]))
    return result


def refreshReservelisiting(cur):
    # get additional information about the borrowed books they hold and store in a variable
    SQL_command = "SELECT bookID FROM reserve WHERE endDate IS NULL AND userID = '" + \
        session['userID'] + "'"
    rs = cur.execute(SQL_command)
    result = []
    for row in rs:
        result.append(str(row[0]))
    return result


def days_between(d1, d2):
    d1 = datetime.datetime.strptime(str(d1), "%Y-%m-%d")
    d2 = datetime.datetime.strptime(str(d2), "%Y-%m-%d")
    return (abs((d2 - d1).days) > 50)


def checkBookAvail(cur, _id):
    # first count how many books the brother got borrowed
    SQL_command = "SELECT availability FROM book WHERE bookID = '" + \
        str(_id) + "'"
    rs = cur.execute(SQL_command)
    for row in rs:
        avail = row[0]
    return avail


def cancelReservationBaseOnIp(cur, _id):
    # Get Loan ID
    SQL_command = "SELECT reserveID from reserve WHERE userID = '" + session['userID'] + "'" \
        "AND bookID = '" + str(_id) + "'" \
        "AND endDate IS NULL"
    rs = cur.execute(SQL_command)
    for row in rs:
        reserveID = row[0]

    # update on reserve table
    SQL_command = "UPDATE reserve SET endDate = CURRENT_TIMESTAMP WHERE reserveID = '" + \
        str(reserveID) + "'"
    cur.execute(SQL_command)

    # Update on book side
    SQL_command = "UPDATE book SET reservedAvailability = TRUE WHERE bookID = '" + \
        str(_id) + "'"
    cur.execute(SQL_command)


def checkBorrowMoreThanFour(cur, id):
    # first count how many books the brother got borrowed
    SQL_command = "SELECT COUNT(returnDate IS NULL)  FROM loan WHERE userID =  '" + \
        str(id) + "'"
    print(SQL_command)
    rs = cur.execute(SQL_command)
    result = 0
    for r in rs:
        result = r[0]
    return (result >= 4)


def borrowBookBaseOnID(cur, _id):
    SQL_command = "UPDATE Book SET availability = FALSE WHERE bookID = '" + \
        str(_id) + "'"
    cur.execute(SQL_command)
    # update loan status
    d = date.today().strftime("%Y-%m-%d")
    dd = datetime.datetime.strptime("'" + d + "'", "%Y-%m-%d") + datetime.timedelta(days=28)
    dd = dd.strftime("%Y-%m-%d")

    SQL_command = "INSERT INTO loan (userID, bookID, borrowDate, dueDate, returnDate) VALUES (" + session['userID'] + "," + str(_id) + ",'" + d + "','" + dd + "', NULL)"
    print(SQL_command)
    cur.execute(SQL_command)


if __name__ == '__main__':
    app.run(debug=True)
