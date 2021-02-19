from flask import Flask, render_template
from user.models import User
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    return User().signup()


if __name__ == '__main__':
    app.run(debug=True)
