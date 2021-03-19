from flask import Flask, session, redirect, flash, render_template, request, url_for
from markupsafe import escape
from datetime import date
import sqlite3
import datetime
import pymongo

app = Flask(__name__, template_folder='templates')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Database configuration
conn = sqlite3.connect('library.db')
print("Opened SQLdatabase successfully")
##### THIS LINK NEEDS TO CHANGE TO YOUR OWN LOCAL SERVER , DATABASE NAME , DATABASE COLLECTION #########
# Localised Mongodb -> change the db to your database

# Lundy COnnectionc
client = pymongo.MongoClient(
    "mongodb://127.0.0.1:27017/?compressors=zlib&gssapiServiceName=mongodb")
# Elton Connection
# client = pymongo.MongoClient(
#     "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false")
db = client["libraryDatabase"]
collection = db["libraryCollection"]

# books in specific


##############################################################################################################
#                                   START OF ACCOUNT PAGE and Functionality
##############################################################################################################

##### START OF Library WORKS FINE #############
@ app.route('/library', methods=['GET', 'POST'])
def library():
    if 'userID' in session:
        return render_template('library.html')
    if request.method == 'POST':
        bookSearch = request.form['bookSearch']
        return redirect(url_for('results', bookSearch=bookSearch))
    return redirect(url_for('login'))
##### END OF library WORKS FINE #############


@ app.route('/book/<int:bookid>', methods=['GET', 'POST'])
def bookDetail(bookid):
    # get book detail
    result = list(db.libraryCollection.find({'_id':  bookid}))
    # get book availability
    with sqlite3.connect("library.db") as con:
        cur = con.cursor()

        userHasBooks = str(bookid) in refreshBorrowlisiting(
            cur) or str(bookid) in refreshReservelisiting(cur)

        print(userHasBooks)

        SQL_command = "SELECT availability, reservedAvailability FROM book WHERE bookID = '" + \
            str(bookid) + "'"
        cur.execute(SQL_command)
        rows = cur.fetchall()
        for row in rows:
            availability = row[0]
            reserved = row[1]
    return render_template('bookDetail.html', result=result, availability=availability, reserved=reserved, userHasBooks=userHasBooks)


@app.route('/library/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        try:
            bookSearch = request.form['bookSearch']
            bookAuthor = request.form['author']
            bookCategory = request.form['category']
            if bookSearch == "" and bookAuthor == "" and bookCategory == "":
                flash("Please input at least one query")
                quit()
            # result = list(collection.find(
            #     {"$text": {"$search": "" +
            #                str(bookSearch) + " " + str(bookAuthor) + " " + str(bookCategory) + "'"}}))
            # result = db.libraryCollection.find({"title": bookSearch})
            return render_template('results.html', bookSearch=bookSearch, result=result)
        except:
            print("help")
    return render_template('library.html')


@ app.route('/library/results/reservationSuccess', methods=['GET', 'POST'])
def reservationSuccess():
    _id = request.form['_id']
    result = list(db.libraryCollection.find({
        '_id':  int(_id)
    }))

    with sqlite3.connect("library.db") as con:
        cur = con.cursor()
        # check if he reserved more than 4 books anot
        SQL_command = "SELECT COUNT(endDate = '') FROM reserve WHERE userID =  '" + \
            str(session['userID']) + "'"
        print(SQL_command)
        cur.execute(SQL_command)
        numofBooks = cur.fetchall()
        print(numofBooks[0][0])
        if numofBooks[0][0] >= 4:
            return render_template('borrowFail.html', transactionType="reserve")

        # first update book status
        SQL_command = "UPDATE Book SET reservedAvailability = FALSE WHERE bookID = '" + \
            str(_id) + "'"
        # print(SQL_command)
        cur.execute(SQL_command)

        # update loan status
        d = date.today().strftime("%d/%m/%y")
        SQL_command = "INSERT INTO reserve (userID, bookID, reserveDate, endDate) VALUES (?,?,?,?)"
        loanEntry = (session['userID'], str(_id), d, '')
        # print(SQL_command)
        cur.execute(SQL_command, loanEntry)
    con.commit()
    notification = "Your reservation for " + \
        result[0]['title'] + " is successful!"
    return render_template('notification.html', notification=notification)


@ app.route('/library/results/borrowSuccess', methods=['GET', 'POST'])
def borrowSuccess():
    _id = request.form['_id']
    result = list(db.libraryCollection.find({
        '_id':  int(_id)
    }))

    with sqlite3.connect("library.db") as con:
        cur = con.cursor()
        if checkBorrowMoreThanFour(cur, session['userID']):
            notification = "brother cannot la more than 4 books borrowed liao"
            return render_template('notification.html', notification=notification)

        # first update book status
        borrowBookBaseOnID(cur, _id)

    con.commit()
    notification = "Your borrowing for "+result[0]['title'] + " is successful!"
    return render_template('notification.html', notification=notification)


##############################################################################################################
#                                   END OF Library PAGE and Functionality
##############################################################################################################


##############################################################################################################
#                                   START OF ACCOUNT PAGE and Functionality
##############################################################################################################

@ app.route('/account', methods=['GET', 'POST'])
def account():
    with sqlite3.connect("library.db") as con:
        cur = con.cursor()
        currBooksID = refreshBorrowlisiting(cur)
        borrowedbooks = []
        currDates = refreshDateslisting(cur)
        today = date.today().strftime("%d/%m/%y")
        overDue = []
        running = 0
        for book in currBooksID:
            borrowedbooks.append(
                list(db.libraryCollection.find({'_id':  int(book)})))
            d1 = datetime.datetime.strptime(currDates[running][1], "%d/%m/%y")
            d2 = datetime.datetime.strptime(today, "%d/%m/%y")
            if ((d2-d1).days > 0):
                overDue.append('Overdue')
            else:
                overDue.append('Not overdue')
            running += 1
        currReservedID = refreshReservelisiting(cur)
        reservedBooks = []
        for book in currReservedID:
            reservedBooks.append(
                list(db.libraryCollection.find({'_id':  int(book)})))

    con.commit()
    return render_template('account.html', borrowedbooks=borrowedbooks, reservedBooks=reservedBooks, currDates=currDates, overDue=overDue)


@ app.route('/extendLoan', methods=['GET', 'POST'])
def extendLoan():
    _id = request.form['_id']
    result = list(db.libraryCollection.find({
        '_id':  int(_id)
    }))

    with sqlite3.connect("library.db") as con:
        cur = con.cursor()

        # check if can extend Loan
        SQL_command = "SELECT reservedAvailability from book WHERE bookID = '" + \
            str(_id) + "'"
        cur.execute(SQL_command)
        rows = cur.fetchall()
        for row in rows:
            ISreserved = row[0]

        if not ISreserved:
            notification = "Sorry, this book has been reserved and the loan cannot be extended"
            return render_template('notification.html', notification=notification)

        SQL_command = "SELECT loanID, dueDate, borrowDate from loan WHERE userID = '" + session['userID'] + "'" \
            "AND bookID = '" + str(_id) + "'" \
            "AND returnDate = '' "
        cur.execute(SQL_command)
        rows = cur.fetchall()
        for row in rows:
            loanID = row[0]
            dueDate = row[1]
            borrowDate = row[2]

        # check if it has been extended before
        if days_between(borrowDate, dueDate):
            notification = "Sorry, this book has been extended before"
            return render_template('notification.html', notification=notification)

        dd = datetime.datetime.strptime(
            str(dueDate), "%d/%m/%y") + datetime.timedelta(days=28)
        dd = dd.strftime("%d/%m/%y")

        # update date base on ID
        SQL_command = "UPDATE loan SET dueDate = (?) WHERE loanID = '" + str(
            loanID) + "'"
        cur.execute(SQL_command, [dd])
        notification = result[0]['title'] + " has been successfully extended"
    return render_template('notification.html', notification=notification)


@ app.route('/returnBook', methods=['GET', 'POST'])
def returnBook():
    _id = request.form['_id']
    result = list(db.libraryCollection.find({
        '_id':  int(_id)
    }))

    with sqlite3.connect("library.db") as con:
        cur = con.cursor()
        # Get Loan ID
        SQL_command = "SELECT loanID from loan WHERE userID = '" + session['userID'] + "'" \
            "AND bookID = '" + str(_id) + "'" \
            "AND (returnDate = '' or returnDate = NULL) "
        cur.execute(SQL_command)
        rows = cur.fetchall()
        for row in rows:
            loanID = row[0]

        # update date base on ID
        SQL_command = "UPDATE loan SET returnDate = CURRENT_TIMESTAMP WHERE loanID = '" + \
            str(loanID) + "'"
        cur.execute(SQL_command)

        # Update the return Date
        SQL_command = "UPDATE book SET availability = TRUE WHERE bookID = '" + \
            str(_id) + "'"
        cur.execute(SQL_command)

        # Calculate Fine if have
        # make sure that reservation working
        notification = result[0]['title'] + " has been returned!"
    return render_template('notification.html', notification=notification)


@ app.route('/cancelReservation', methods=['GET', 'POST'])
def cancelReservation():
    _id = request.form['_id']
    result = list(db.libraryCollection.find({
        '_id':  int(_id)
    }))
    with sqlite3.connect("library.db") as con:
        cur = con.cursor()
        cancelReservationBaseOnIp(cur, _id)
        # make sure that reservation working
        notification = " Your reservation for " + \
            result[0]['title'] + " has been cancelled!"
    return render_template('notification.html', notification=notification)


@ app.route('/reserveToBorrow', methods=['GET', 'POST'])
def reserveToBorrow():
    _id = request.form['_id']
    result = list(db.libraryCollection.find({
        '_id':  int(_id)
    }))
    with sqlite3.connect("library.db") as con:
        cur = con.cursor()

        # first check if you have more than 4 books
        if checkBorrowMoreThanFour(cur, session['userID']):
            notification = "You already borrowed more than 4 books"
            return render_template('notification.html', notification=notification)

        # check if the books is available
        print(checkBookAvail(cur, _id))
        if not checkBookAvail(cur, _id):
            notification = "Currently the Book is not available and still on loan"
            return render_template('notification.html', notification=notification)

        # end reservation
        # book is avail and less than four books
        borrowBookBaseOnID(cur, _id)

    con.commit()
    notification = "Your borrowing for "+result[0]['title'] + " is successful!"
    return render_template('notification.html', notification=notification)

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
            with sqlite3.connect("library.db") as con:
                cur = con.cursor()
                SQL_command = "SELECT userID, userPassword FROM userTable WHERE userName = '" + \
                    str(username) + "'"
                cur.execute(SQL_command)
                rows = cur.fetchall()
                actualpassword = ""
                sessionID = ""
                for row in rows:
                    sessionID = str(row[0])
                    actualpassword = row[1]
                if str(actualpassword) == str(userPassword):
                    session['userID'] = sessionID
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


def refreshDateslisting(cur):
    SQL_command = "SELECT borrowDate, dueDate FROM loan WHERE (returnDate = '' or returnDate = NULL) AND userID = '" + \
        session['userID'] + "'"
    cur.execute(SQL_command)
    rows = cur.fetchall()
    result = []
    for row in rows:
        result.append(list(row))
    return result


def refreshBorrowlisiting(cur):
    # get additional information about the borrowed books they hold and store in a variable
    SQL_command = "SELECT bookID FROM loan WHERE (returnDate = '' or returnDate = NULL) AND userID = '" + \
        session['userID'] + "'"
    cur.execute(SQL_command)
    rows = cur.fetchall()
    result = []
    for row in rows:
        result.append(str(row[0]))
    return result


def refreshReservelisiting(cur):
    # get additional information about the borrowed books they hold and store in a variable
    SQL_command = "SELECT bookID FROM reserve WHERE (endDate = '' or endDate = NULL) AND userID = '" + \
        session['userID'] + "'"
    cur.execute(SQL_command)
    rows = cur.fetchall()
    result = []
    for row in rows:
        result.append(str(row[0]))
    return result


def days_between(d1, d2):
    d1 = datetime.datetime.strptime(str(d1), "%d/%m/%y")
    d2 = datetime.datetime.strptime(str(d2), "%d/%m/%y")
    return (abs((d2 - d1).days) > 50)


def checkBookAvail(cur, _id):
    # first count how many books the brother got borrowed
    SQL_command = "SELECT availability FROM book WHERE bookID = '" + \
        str(_id) + "'"
    cur.execute(SQL_command)
    rows = cur.fetchall()
    for row in rows:
        avail = row[0]
    return avail


def cancelReservationBaseOnIp(cur, _id):
    # Get Loan ID
    SQL_command = "SELECT reserveID from reserve WHERE userID = '" + session['userID'] + "'" \
        "AND bookID = '" + str(_id) + "'" \
        "AND (endDate = '' or endDate = NULL)"
    cur.execute(SQL_command)
    rows = cur.fetchall()
    for row in rows:
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
    SQL_command = "SELECT COUNT(returnDate)  FROM loan WHERE userID =  '" + \
        str(id) + "' AND (returnDate = '' or returnDate = NULL)"
    print(SQL_command)
    cur.execute(SQL_command)
    numofBooks = cur.fetchall()
    return (numofBooks[0][0] >= 4)


def borrowBookBaseOnID(cur, _id):
    SQL_command = "UPDATE Book SET availability = FALSE WHERE bookID = '" + \
        str(_id) + "'"
    cur.execute(SQL_command)
    # update loan status
    d = date.today().strftime("%d/%m/%y")
    dd = datetime.datetime.strptime(
        d, "%d/%m/%y") + datetime.timedelta(days=28)
    dd = dd.strftime("%d/%m/%y")

    SQL_command = "INSERT INTO loan (userID, bookID, borrowDate, dueDate, returnDate) VALUES (?,?,?,?,?)"
    loanEntry = (session['userID'], str(_id), d, dd, '')
    # print(SQL_command)
    cur.execute(SQL_command, loanEntry)


if __name__ == '__main__':
    app.run(debug=True)
