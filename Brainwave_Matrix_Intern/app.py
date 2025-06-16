from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pin = request.form['pin']
        users = load_users()
        for username, info in users.items():
            if info['pin'] == pin:
                session['user'] = username
                return redirect('/dashboard')
        return "Invalid PIN"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    users = load_users()
    user = session['user']
    return render_template('dashboard.html', user=user, balance=users[user]['balance'])

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        amount = float(request.form['amount'])
        users = load_users()
        users[session['user']]['balance'] += amount
        users[session['user']]['history'].append(f"Deposited ₹{amount}")
        save_users(users)
        return redirect('/dashboard')
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        amount = float(request.form['amount'])
        users = load_users()
        if users[session['user']]['balance'] >= amount:
            users[session['user']]['balance'] -= amount
            users[session['user']]['history'].append(f"Withdrew ₹{amount}")
            save_users(users)
            return redirect('/dashboard')
        else:
            return "Insufficient balance"
    return render_template('withdraw.html')

@app.route('/changepin', methods=['GET', 'POST'])
def changepin():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        new_pin = request.form['new_pin']
        users = load_users()
        users[session['user']]['pin'] = new_pin
        save_users(users)
        return redirect('/dashboard')
    return render_template('changepin.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        account_number = request.form['account_number']
        ifsc = request.form['ifsc']
        amount = float(request.form['amount'])
        users = load_users()
        sender = session['user']

        recipient = None
        for username, info in users.items():
            if info.get('account') == account_number and info.get('ifsc') == ifsc:
                recipient = username
                break

        if not recipient:
            return "Recipient not found"
        if users[sender]['balance'] < amount:
            return "Insufficient balance"

        users[sender]['balance'] -= amount
        users[recipient]['balance'] += amount
        users[sender]['history'].append(f"Transferred ₹{amount} to {recipient}")
        users[recipient]['history'].append(f"Received ₹{amount} from {sender}")
        save_users(users)
        return redirect('/dashboard')
    return render_template('transfer.html')

@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/')
    users = load_users()
    return render_template('history.html', history=users[session['user']]['history'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
@app.route('/balance')
def balance():
    if 'user' not in session:
        return redirect('/')
    users = load_users()
    user = session['user']
    balance = users[user]['balance']
    return render_template('balance.html', balance=balance)

    
if __name__ == '__main__':
    app.run(debug=True)
