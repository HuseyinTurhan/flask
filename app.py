from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    age = db.Column(db.Integer, default = 0)
    group = db.Column(db.String(200), nullable = False)
    college_name = db.Column(db.String(200), nullable = False)

    def __repr__(self):
        return '<Task %r>' %self.id

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
        tasks = Student.query.order_by(Student.id).all()
        return render_template('index.html', tasks=tasks)


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


if __name__ == "__main__":
    app.run(debug = True)
