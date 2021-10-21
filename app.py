from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///notes.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(2000))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.id} - {self.comment}"


class Notes(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    branch = db.Column(db.String(100))
    semester = db.Column(db.String(50))
    unit = db.Column(db.Integer)
    hide_flag = db.Column(db.String(1))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.subject} - {self.link}"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self) -> str:
        return f"{self.name}"


@app.route('/')
def home():
    return render_template('index.html', user = current_user)

@app.route('/download', methods = ['GET', 'POST'])
def download():
    if request.method == 'POST':
        subject = request.form['subject']
        unit = request.form['unit']
        link = request.form['link']
        sem_,sem__= [],""
        for k,v in request.form.items():
            if v == 'semester':
                sem_.append(k)
        sem__ = " ".join(sem_)
        print(sem__)
        branch_,branch__ = [],""
        for k,v in request.form.items():
            if v == 'branch':
                branch_.append(k)
        branch__ = " ".join(branch_)
        print(branch__)

        semester = sem__
        branch = branch__
        notes = Notes(subject = subject, link = link, branch = branch, unit = unit, semester = semester)
        db.session.add(notes)
        db.session.commit()


    allNotes = Notes.query.all()
    return render_template('download.html',allNotes = allNotes)

@app.route('/delete/<int:sno>')
@login_required
def delete(sno):
    todel =Notes.query.filter_by(sno=sno).first()
    db.session.delete(todel)
    db.session.commit()
    return redirect('/download')

@app.route('/contact', methods = ['GET', 'POST'])
def contact():
    if request.method == 'POST':
        print(request.form)
        a =request.form['name']
        b =request.form['email']
        c = request.form['subject']
        d = request.form['comments']
        comment = a +'-'+ b+'-'+c+ '-'+d
        contact = Contacts(comment=comment)
        db.session.add(contact)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/query' , methods = ['GET', 'POST'])
def query():
    if request.method == 'POST':
        # print(request.form)
        if request.form['Semester'] :
            semester = request.form['Semester']
            semester = "%{}%".format(semester)
            if request.form['Branch']:
                branch = request.form['Branch']
                branch = "%{}%".format(branch)
                allNotes = Notes.query.filter(Notes.semester.like(semester), Notes.branch.like(branch)).all()
            else: allNotes = Notes.query.filter(Notes.semester.like(semester)).all()

        elif request.form['Branch']:
            branch = request.form['Branch']
            branch = "%{}%".format(branch)
            allNotes = Notes.query.filter(Notes.branch.like(branch)).all()
        else : allNotes = Notes.query.all()

        return render_template('download.html', allNotes = allNotes)


@app.route('/update/<int:sno>' , methods = ['GET', 'POST'])
@login_required
def update(sno):
    if request.method=='POST':
        subject = request.form['subject']
        unit = request.form['unit']
        link = request.form['link']
        sem_, sem__ = [], ""
        for k, v in request.form.items():
            if v == 'semester':
                sem_.append(k)
        sem__ = " ".join(sem_)
        # print(sem__)
        branch_, branch__ = [], ""
        for k, v in request.form.items():
            if v == 'branch':
                branch_.append(k)
        branch__ = " ".join(branch_)
        print(branch__)

        semester = sem__
        branch = branch__

        toupdate = Notes.query.filter_by(sno=sno).first()
        toupdate.subject = subject
        toupdate.link = link
        toupdate.branch = branch
        toupdate.unit = unit
        toupdate.semester = semester


        db.session.add(toupdate)
        db.session.commit()
        return redirect(url_for('download'))
    else:
        toupdate = Notes.query.filter_by(sno=sno).first()
        return render_template('update.html', toupdate = toupdate )

@app.route('/login' , methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        email = request.form.get('email')
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged In successfully', category='success')
                login_user(user,remember=True)
                return redirect(url_for('home'))
            else:
                flash('Incorrect password', category = 'error')
        else:
            flash('email not found', category='error')
        return render_template('index.html',user=current_user)
    return render_template('index.html',user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/signup' , methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form.get('email')
        auth = request.form.get('auth')
        password1 = request.form['password1']
        password2 = request.form['password2']
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exist', category='error')
        elif len(password1) <7:
            flash('passwords must be at least 7 characters.', category='error')
        elif auth != 'KW@145':
            flash('Auth Code is not correct.', category='error')
        elif password1 != password2:
            flash('passwords are not the same', category='error')
        else:
            new_user = User(email = email, name = name, password = generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created', category='success')
        return render_template('index.html', user=current_user)
    return render_template('index.html', user=current_user)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# @app.route('/add')
# def add():
#     notes = Notes(subject = 'Bkon', link = "Bkon0", hide_flag = "Y")
#     db.session.add(notes)
#     db.session.commit()
#     return render_template('index.html')

# @app.route('/show')
# def show():
#     akon = Notes.query.all()
#     print(akon)
#     return render_template('index.html')

if __name__ == '__main__':
    app.run(debug= False, port=5000)