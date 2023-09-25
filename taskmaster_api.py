from flask import Flask,render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

def create_app():
    app=Flask(__name__)
    # Setting up the dtaabase in postgres

    app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///test.db"
    db=SQLAlchemy(app)

    class Todo(db.Model):
        id=db.Column(db.Integer,primary_key=True)
        content=db.Column(db.String(250),nullable=False)
        date=db.Column(db.DateTime,default=datetime.utcnow)

        def __repr__(self):
            return "<Task %r>" % self.id

    return app,db,Todo

app,db,Todo=create_app()
with app.app_context():
    db.create_all()
    print("Database Created")


# Routes

@app.route("/",methods=["GET","POST"])
def hello():
    if request.method=="POST":
        task=request.form["content"]
        new_task=Todo(content=task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except:
            return "Could not add your task. Please try again"
    else:
        tasks=Todo.query.order_by(Todo.date).all()
        return render_template('index.html',tasks=tasks)
    
@app.route("/delete-task/<int:id>")
def delete(id):
    delete_task=Todo.query.get_or_404(id)

    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except:
        return "Could not delete your task"

@app.route("/update/<int:id>",methods=["GET","POST"])
def update(id):
    task=Todo.query.get_or_404(id)

    if request.method=="POST":
        task.content=request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html',task=task)

if __name__=="__main__":
    app.run(debug=True)