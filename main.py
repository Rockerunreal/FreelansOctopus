from datetime import datetime
from flask import Flask, render_template, request, redirect, send_file, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2
from pymongo. mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from flask import render_template, flash, redirect, session, url_for, request, g, sessions
from bson.objectid import ObjectId



#DataBase
client = MongoClient("mongodb://localhost:27017")
users = client['Octopus']["Users"]
orders = client['Octopus']["Orders"]


#Print Values from DB
# for i in users.find():
#     print(i["name"], i["password"], i["_id"])


#Make an example "app" by class "Flask"

app = Flask(__name__)


#Return page "index.html". File include a catalog with cards and dynamic data output from DB
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.method)
        print(request.form["id"])
        print(orders.find_one({"_id": ObjectId(request.form["id"])}))
        orders.update_one({"_id": ObjectId(request.form["id"])}, {"$set": {"status": "active", "worker_id": request.cookies.get("id")}})
        return "Bad request"
    else:
        data = orders.find({"status": "builded"}).sort({"date": -1})
        return render_template('каталог.html', orders = data )


@app.route('/my_orders', methods=['GET', 'POST'])
def my_orders():
    if request.method == 'POST':
        print(request.method)
        print(request.form["id"])
        cost = orders.find_one({"_id": ObjectId(request.form["id"])})["cost"]
        worker = orders.find_one({"_id": ObjectId(request.form["id"])})["worker_id"]
        work = users.find_one({"_id": ObjectId(worker)})
        summ = int(work["balance"]) + int(cost)
        print(summ, int(work["balance"]), int(cost), worker, request.cookies["id"])
        users.update_one({"_id": ObjectId(worker)},{"$set": {"balance": summ}})
        orders.update_one({"_id": ObjectId(request.form["id"])}, {"$set": {"status": "off", "worker_id": request.cookies.get("id")}})
        return "Bad request"
    else:
        data = orders.find({{"user_id": str(request.cookies.get("id")), "status": "active"}}).sort({"date": -1})
        return render_template('Мои заказы.html', orders = data )


@app.route('/profile')
def profile():
    if request.cookies.get("logged") == "True":
        id = request.cookies.get("id")
        for i in users.find():
            if str(i["_id"]) == id:
                user = i
                for j in user:
                    print(user[j])
                return render_template('Профиль.html', user = user )

    else:
        redirect('/login')




#Return page with registration. Values from html-form saves in DB.
@app.route('/register', methods=['POST', 'GET'])
def register():
    print(request.method)
    if request.method == 'POST':
        login = request.form["Name"]
        code = request.form["Password"]
        vk = request.form["VK"]
        tg = request.form["Telegram"]
        git = request.form["GitHub"]
        try:
            users.insert_one({"name":login, "password":code, "vk": vk, "git": git, "tg": tg, "balance": 100, "skill": 0})
            return redirect("/")
        except:
            return "Bad Request"
    else:
        return render_template('Регистрация.html')


#Return page with login. Values expect in DB.
@app.route('/login', methods=['POST', 'GET'])
def login():
    print(request.method)
    log =''
    if request.method == 'POST':
        if request.cookies.get('logged'):
            log = request.cookies.get('logged')
        login = request.form["Name"]
        code = request.form["Password"]
        try:

            user = users.find_one({"name": login})
            if code == user["password"]:
                res = make_response("<h1>Sucsessfull autorisation<h1>")
                res.set_cookie("logged", "True")
                res.set_cookie("id", str(user["_id"]))
                print()
                return res, 200
        except:
            return "Bad Request"
    else:
        return render_template('вход.html')



@app.route('/create', methods=['POST', 'GET'])
def create():
    print(request.method)
    if request.cookies.get("logged") == "True":
        if request.method == 'POST':
            user_id = request.cookies.get("id")
            way = request.form["way"]
            title = request.form["title"]
            description = request.form["description"]
            cost = request.form["cost"]
            date = datetime.now()
            print(date)
            try:
                orders.insert_one({"user_id":user_id, "way": way, "title": title, "description": description, "cost": cost, "date":date, "status": "builded"})
                return redirect("/")
            except:
                return "Bad Request"
        else:
            return render_template('Создать ворк.html')
    else:
        return redirect('/login')



#Request for static-files(Media, scripts, styles)
@app.get("/{path}")
def get_picture(path):
    path1 = os.path.join('static',path)
    return send_file(f'{path1}')
@app.get("/register/{path}")
def get_picture_reg(path):
    path1 = os.path.join('static', path)
    return send_file(f'{path1}')
@app.get("/login/{path}")
def get_picture_log(path):
    path1 = os.path.join('static', path)
    return send_file(f'{path1}')
@app.get("/create/{path}")
def get_picture_r(path):
    path1 = os.path.join('static', path)
    return send_file(f'{path1}')
@app.get("/profile/{path}")
def get_picture_prof(path):
    path1 = os.path.join('static', path)
    return send_file(f'{path1}')

@app.route('/cookie/')
def cookie():
    if not request.cookies.get('foo'):
        res = make_response("Setting a cookie")
        res.set_cookie('foo', 'bar', max_age=60*60*24*365*2)
    else:
        res = make_response("Value of cookie foo is {}".format(request.cookies.get('foo')))

    return res

if __name__ == "__main__":
    app.run()
