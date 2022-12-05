from flask import Flask, render_template, request, redirect, url_for
from flask_restful import Resource, Api, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required,logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

studentFields = {
    'id':fields.Integer,
    'name':fields.String,
    'age':fields.Integer,
    'group':fields.String,
    'college_name':fields.String,
}

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    age = db.Column(db.Integer, default = 0)
    group = db.Column(db.String(200), nullable = False)
    college_name = db.Column(db.String(200), nullable = False)

    def __repr__(self):
        return self.name + str(self.age)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable=False, unique = True)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return self.name

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=80)], render_kw={"placeholder":"Username"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValidationError("The username already exists, please choose another one!")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=80)], render_kw={"placeholder":"Username"})
    submit = SubmitField('Login')

    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()
        if not existing_username:
            raise ValidationError("The username is wrong, please check it!")


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        else:
            raise ValidationError("No such a username, please try again!")

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username = form.username.data, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("register.html", form=form)
    
@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        id = request.form['id']
        name = request.form['name']
        age = request.form['age']
        group = request.form['group']
        college = request.form['college']
        new_task = Student(id=id, name=name, age=age, group= group, college_name=college)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "Something's gone wrong!"
    else:
        students = Student.query.order_by(Student.id).all()
        return render_template('index.html', students=students)


@app.route('/delete/<int:id>')
def delete(id):
    task_delete = Student.query.get_or_404(id)

    try:
        db.session.delete(task_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Something's gone wrong!"


@app.route("/update/<int:id>", methods =['GET', 'POST'])
def update(id):
    task_update = Student.query.get_or_404(id)
    
    if request.method == "POST":
        task_update.id = request.form['id']
        task_update.name = request.form['name']
        task_update.age = request.form['age']
        task_update.group = request.form['group']
        task_update.college = request.form['college']

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Something's gone wrong!"
    else:
        return render_template("update.html", task = task_update)

class Items(Resource):
    @marshal_with(studentFields)
    def get(self):
        students = Student.query.all()
        return students

    @marshal_with(studentFields)
    def post(self):
        data = request.json
        student = Student(id =data['id'], name = data['name'], age = data['age'], group=data['group'], college_name = data['college_name'])
        db.session.add(student)
        db.session.commit()

        students = Student.query.all()
        return students

class Item(Resource):
    @marshal_with(studentFields)
    def get(self, pk):
        student = Student.query.filter_by(id=pk).first()
        return student

    @marshal_with(studentFields)
    def put(self,pk):
        data = request.json
        student = Student(id =data['id'], name = data['name'], age = data['age'], group=data['group'], college_name = data['college_name'])

        db.session.commit()
        return student
    
    @marshal_with(studentFields)
    def delete(self,pk):
        student = Student.query.filter_by(id=pk).first()
        db.session.delete(student)
        db.session.commit()
        students = Student.query.all()
        return students

api.add_resource(Items, "/items")
api.add_resource(Item, "/items/<int:pk>")

if __name__ == "__main__":
    app.run(debug = True)
