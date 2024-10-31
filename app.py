from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.candidates import candidates
from models.votes import votes
from models.users import users

app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/')
def index():
    vote_counts = {candidate['id'] : 0 for candidate in candidates}

    for vote in votes:
        if vote['vote'] in vote_counts:
            vote_counts[vote['vote']] += 1
    
    for candidate in candidates:
        candidate['vote_count'] = vote_counts[candidate['id']]

    return render_template('index.html', candidates=candidates)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = [user for user in users if user['mail'] == email]
        if user and check_password_hash(user[0]['password'], password):
            session['is_logged_in'] = True
            session['id'] = user[0]['id']
            flash('Login berhasil!', 'error')
            return redirect(url_for('dashboard'))
        else:
            flash('Email atau password salah!')    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = [user for user in users if user['mail'] == email]
        if user:
            flash('Email sudah terdaftar!')
        else:
            user = {
                'id': len(users) + 1,
                'mail': email,
                'password': generate_password_hash(password)
            }
            users.append(user)
            flash('Berhasil membuat akun!')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'is_logged_in' not in session:
        flash('Anda harus login terlebih dahulu')
        return redirect(url_for('login'))
    return render_template('dashboard.html', candidates=candidates)

@app.route('/vote/<int:candidate_id>')
def vote(candidate_id):
    if 'is_logged_in' not in session:
        flash('Anda harus login terlebih dahulu')
        return redirect(url_for('login'))
    else:
        user_id = session['id']
        candidate = [candidate for candidate in candidates if candidate['id'] == candidate_id]
        if not any (vote['user_id'] == user_id for vote in votes):
            if candidate:
                vote = {
                    'id': len(votes) + 1,
                    'user_id': session['id'],
                    'vote': candidate_id
                }
                votes.append(vote)
                candidate[0]['vote_count'] += 1
                flash('Pengisian suara berhasil')
            else:
                flash('Kandidat tidak ditemukan')
            return redirect(url_for('dashboard'))
        else:
            flash('Anda sudah memberikan suara')
            return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('is_logged_in', None)
    session.pop('id', None)
    flash('Anda berhasil logout')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
