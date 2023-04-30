from flask import Flask,render_template,request,session,redirect, url_for
import sys
import sqlite3
import pickle
import numpy as np
app = Flask(__name__)
app.secret_key = "super secret key"
# conn=sqlite3.connect("signup.db")
# c=conn.cursor()
# # c.execute("create table if not exists user (name text, username text, pass text)")
# c.execute("create table if not exists Employees ( name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, pass TEXT NOT NULL)")  
# conn.commit()
# conn.close()


@app.route("/")
@app.route("/home")
def home():
    return render_template('home_page.html')

@app.route("/login")
def login():
    return render_template('login.html')



@app.route("/home_pred")
def home_pred():
    return render_template('home_pred.html')


@app.route("/loggedin",methods=['GET','POST'])
def loggedin():
    if request.method=="POST":
        print('entered post login',flush=True)
        # name=request.form['name']
        email=request.form['email']
        passw=request.form['pass']
        conn=sqlite3.connect("signup.db")
        cur = conn.cursor()
        cur.execute("Select * from Employees where email='"+email+"' and pass='"+passw+"'")
        r=cur.fetchall()
        for i in r:
            print('rntered for..',i[1],i[2],flush=True)
            if (email==i[1] and passw==i[2]):
                session["logedin"]=True
                return redirect(url_for("home_pred"))

    return render_template('home.html')


@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method=="POST":
        name=request.form['name']
        email=request.form['email']
        passw=request.form['pass']
        conn=sqlite3.connect("signup.db")
        # print(name,email)
        cur = conn.cursor()
        cur.execute("INSERT INTO Employees (name,email,pass) VALUES (?,?,?)",(name,email,passw) )
        conn.commit()
        conn.close()
        print('added success!',flush=True)

        return render_template('success_account.html')
        
    return render_template('signup.html')

@app.route("/success_login",methods=['GET','POST'])
def success_login():
    return render_template('blog.html')


def ValuePredictor(to_predict_list):
    to_predict = np.array(to_predict_list).reshape(1, 12)
    loaded_model = pickle.load(open("ML_model_code\model.pkl", "rb"))
    result = loaded_model.predict(to_predict)
    return result[0]

@app.route('/result', methods = ['POST'])
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        to_predict_list = list(map(int, to_predict_list))
        result = ValuePredictor(to_predict_list)       
        if int(result)== 1:
            prediction ='Income more than 50K'
        else:
            prediction ='Income less than 50K'           
        return render_template("result.html", prediction = prediction)

if __name__ == "__main__":
    # app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)