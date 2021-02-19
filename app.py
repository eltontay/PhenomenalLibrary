from flask import Flask, render_template, request
from user.models import User
app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/library', methods=['POST'])
def library():
    if request.method == 'POST':
        username = request.form['user']
        password = request.form['pass']
        return render_template('library.html')
    else:
        pass


@ app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    return User().signup()


if __name__ == '__main__':
    app.run(debug=True)
