from flask import Flask,render_template,request,session,redirect, url_for
import sys
import sqlite3
import pickle
import numpy as np
import pandas as pd
import bz2file as bz2
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = "super secret key"
# conn=sqlite3.connect("signup.db")
# c=conn.cursor()
# # c.execute("create table if not exists user (name text, username text, pass text)")
# c.execute("create table if not exists Employees ( name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, pass TEXT NOT NULL)")  
# conn.commit()
# conn.close()


@app.route("/")
@app.route("/home",methods=['GET','POST'])
def home():
    return render_template('home_page.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/apps_options")
def apps_options():
    return render_template('apps_options.html')

@app.route("/home_pred")
def home_pred():
    return render_template('home_pred.html')

@app.route("/home_bank_deposit_pred")
def home_bank_deposit_pred():
    return render_template('bank_term_app.html')


def preproc(data):
    scaler=pickle.load(open("bank_term_deposit_ML\model_and_scaler\scaler.pickle", "rb"))
    obj_cols_list=[]
    for col in data.columns:
        if (data[col].dtypes == object):
            obj_cols_list.append(col)
    print(obj_cols_list) 
    data = pd.get_dummies(data, columns = obj_cols_list)
    data = scaler.transform(data)
    return data   

@app.route('/bank_deposit', methods = ['GET', 'POST'])
def bank_deposit():
    # model=pickle.load(open("bank_term_deposit_ML\model_and_scaler\RF_model.pickle", "rb"))
    model_com=bz2.BZ2File('bank_term_deposit_ML\model_and_scaler\RF_model_compressed.pbz2', 'rb')
    model=pickle.load(model_com)
    if request.method == 'POST':
            f = request.files['file']
            data=pd.read_csv(f,index_col=0)
            print('file......',f,flush=True)
            data_copy=data.copy()
            data_copy=preproc(data_copy)
            predicted=model.predict(data_copy)
            data['predicted_score']=predicted
            data.to_csv('bank_term_deposit_ML\\user_download_result\\result.csv')
            return render_template("bank_term_download_res.html")
#     # return data
@app.route('/database_download', methods = ['GET', 'POST'])
def database_download():
    return send_from_directory('bank_term_deposit_ML\\user_download_result\\', 'result.csv')

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
                return redirect(url_for("apps_options"))

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