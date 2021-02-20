from flask import Flask, render_template, request, url_for

app = Flask(__name__)

##trial comment for git push


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


if __name__ == '__main__':
    app.run(debug=True)
