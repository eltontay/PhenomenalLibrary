from flask import Flask, render_template, request

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


@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        return render_template('signup.html')
    else:
        pass


if __name__ == '__main__':
    app.run(debug=True)
