import json
import random
import uuid
from datetime import datetime
from datetime import timedelta

import pyrebase
from flask import Flask, render_template, request, redirect, session, jsonify

from functions import check_username_and_token, redirect_to_case_study, login_required, get_similarity_text

# app = Flask(__name__, static_url_path='/static')

''' Add your credentials here --> FIREBASE'''

config = {
    "apiKey": "************",
    "authDomain": "************",
    "databaseURL": "************",
    "projectId": "************",
    "storageBucket": "************",
    "messagingSenderId": "************",
    "appId": "************"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__)
app.config['SESSION_COOKIE_DURATION'] = timedelta(hours=1)
app.secret_key = '**********'


@app.route("/thank-you")
@login_required
def thank_you():
    session.pop("username", None)
    session.pop("current_user", None)

    return "thank you for your participation!"


'''This is the login area of my app'''


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        input_username = request.form['name']
        input_token = request.form['password']

        print('This is debugging', input_username, input_token)

        if check_username_and_token(input_username, input_token):
            print("I am here 2")
            user_id = str(uuid.uuid4())
            user_details = db.child("user_details").order_by_child(
                "username").equal_to(input_username).get().val()
            print("therese are", user_details)
            if user_details:
                current_user = {"username": input_username, "user_id": user_id}
                session["current_user"] = current_user
                session['logged_in'] = True
                print("this is current user", current_user)
                user_details_values = list(user_details.values())[0]
                if all(key in user_details_values.keys() for key in ["age", "gender", "role"]):
                    group_user = user_details_values["group"]
                    language_user = user_details_values["language"]
                    path_return = redirect_to_case_study(
                        group_user, language_user)

                    # user has already given all the details, forward to the case study
                    return path_return
            else:

                current_user = {"username": input_username, "user_id": user_id}
                session["current_user"] = current_user
                session['logged_in'] = True
                db.child("user_details").push(current_user)
                print("this is current user", current_user)
                return redirect('/details')
        else:
            error = 'Invalid username or password'
            return render_template("index.html", error=error)
    print("why I am here?")
    return render_template("index.html")


''' Here the details of the users are queried and written to the database'''

''' Get the Details of the User Page'''
@app.route("/details")
@login_required
def details():
    return render_template("details.html")

@app.route('/details', methods=['POST'])
@login_required
def register():
    getusername = session['current_user']
    username = getusername.get('username')
    print("debugging", username)

    if request.method == 'POST':

        user_details = db.child("User").order_by_child(
            "username").equal_to(username).get().val()
        group = user_details[list(user_details.keys())[0]]["group"]
        language = user_details[list(user_details.keys())[0]]["language"]
        # print(group, language)

        age = request.form.get('age')
        gender = request.form.get('gender')
        role = request.form.get('role')

        user_details = session['current_user']
        user_id = user_details['user_id']

        user_details = db.child("user_details").order_by_child(
            "username").equal_to(username).get().val()
        for key, value in user_details.items():
            db.child("user_details").child(key).update(
                {"age": age, "gender": gender, "role": role, "group": group, "language": language,
                 "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")})

        return redirect_to_case_study(group, language)

    return render_template("details.html")



''' Here is the group A for both languages '''

global counter
counter = 0

''' Interface for Group A for English '''
@app.route("/Joi", methods=["GET", "POST"])
@login_required
def GroupAEN():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    getusername = session['current_user']
    username = getusername.get('username')
    with open("static/data/A_text_data_en_4.json", "r") as f:
        data = json.load(f)

    texts = [d for d in data]

    global counter
    print("debugging which ", counter)
    if counter == len(texts):
        counter = 0
        return redirect("/thank-you")

    try:
        text = texts[counter]["Text"]

        intens = texts[counter]["Intensity"]
        if intens == 1:
            intens = "Intimidation"
        elif intens == 2:
            intens = "Offensive"
        elif intens == 3:
            intens = "Promotion of violence"
        elif intens == 0:
            intens = ""

        print("which counter", counter)

        label = texts[counter]["Label"]

        if request.method == "POST":

            form_id = request.form.get("hate")

            if form_id == "no":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }

                db.child("GroupAEN").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupAEN.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)

            elif form_id == "yes":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }

                db.child("GroupAEN").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupAEN.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)
            else:

                hate_label = texts[counter]["Label"]
                intens_label = texts[counter]["Intensity"]

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": hate_label,
                    "intensity_label": intens_label,
                    "text_id": counter,
                    "Person_annotator": "agrees with them"
                }

                db.child("GroupAEN").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

            return render_template("groupAEN.html", text=text, texts=text, counter=counter, intens=intens, label=label)

    except IndexError:
        counter = 0
        return redirect("/thank-you")

    return render_template("groupAEN.html", text=text, texts=text, counter=counter, intens=intens, label=label)


@app.route("/Joi", methods=["POST"])
@login_required
def annotate():
    global counter
    hate = request.form.get("hate")
    intensity = None
    if hate == "yes":
        intensity = request.form.get("intensity")
    counter += 1
    return redirect("/Joi")

''' Interface for Group A for German '''
@app.route("/Love", methods=["GET", "POST"])
@login_required
def groupADE():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    getusername = session['current_user']
    username = getusername.get('username')
    with open("static/data/A_text_data_de_4.json", "r") as f:
        data = json.load(f)

    texts = [d for d in data]

    global counter
    print("debugging which ", counter)
    if counter == len(texts):
        counter = 0
        return redirect("/thank-you")

    try:
        text = texts[counter]["Text"]

        intens = texts[counter]["Intensity"]
        if intens == 1:
            intens = "Intimidation"
        elif intens == 2:
            intens = "Offensive"
        elif intens == 3:
            intens = "Promotion of violence"
        elif intens == 0:
            intens = ""

        print("which counter", counter)

        label = texts[counter]["Label"]

        if request.method == "POST":

            form_id = request.form.get("hate")

            if form_id == "no":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }

                db.child("groupADE").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupADE.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)

            elif form_id == "yes":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }
                database_name = "groupADE" + username
                db.child("groupADE").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupADE.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)
            else:

                hate_label = texts[counter]["Label"]
                intens_label = texts[counter]["Intensity"]

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": hate_label,
                    "intensity_label": intens_label,
                    "text_id": counter,
                    "Person_annotator": "agrees with them"
                }
                db.child("groupADE").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

            return render_template("groupADE.html", text=text, texts=text, counter=counter, intens=intens, label=label)

    except IndexError:
        counter = 0
        return redirect("/thank-you")

    return render_template("groupADE.html", text=text, texts=text, counter=counter, intens=intens, label=label)


@app.route("/Love", methods=["POST"])
@login_required
def annotate1():
    global counter
    hate = request.form.get("hate")
    intensity = None
    if hate == "yes":
        intensity = request.form.get("intensity")
    counter += 1
    return redirect("/Love")

''' Here is the group B for both languages '''
''' Interface for Group B for German '''

@app.route("/Happiness", methods=["GET", "POST"])
@login_required
def groupBDE():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    getusername = session['current_user']
    username = getusername.get('username')
    with open("static/data/B_text_data_de_4.json", "r") as f:
        data = json.load(f)

    texts = [d for d in data]

    global counter
    print("debugging which ", counter)
    if counter == len(texts):
        counter = 0
        return redirect("/thank-you")

    try:
        text = texts[counter]["Text"]

        intens = texts[counter]["Intensity"]
        if intens == 1:
            intens = "Intimidation"
        elif intens == 2:
            intens = "Offensive"
        elif intens == 3:
            intens = "Promotion of violence"
        elif intens == 0:
            intens = ""

        print("which counter", counter)

        label = texts[counter]["Label"]

        if request.method == "POST":

            form_id = request.form.get("hate")

            if form_id == "no":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }

                db.child("groupBDE").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupBDE.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)

            elif form_id == "yes":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }

                db.child("groupBDE").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupBDE.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)
            else:

                hate_label = texts[counter]["Label"]
                intens_label = texts[counter]["Intensity"]

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": hate_label,
                    "intensity_label": intens_label,
                    "text_id": counter,
                    "Person_annotator": "agrees with them"
                }

                db.child("groupBDE").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

            return render_template("groupBDE.html", text=text, texts=text, counter=counter, intens=intens, label=label)

    except IndexError:
        counter = 0
        return redirect("/thank-you")

    return render_template("groupBDE.html", text=text, texts=text, counter=counter, intens=intens, label=label)


@app.route("/Happiness", methods=["POST"])
@login_required
def annotate2():
    global counter
    hate = request.form.get("hate")
    intensity = None
    if hate == "yes":
        intensity = request.form.get("intensity")
    counter += 1
    return redirect("/Happiness")

''' Interface for Group B for English '''

@app.route("/cheer", methods=["GET", "POST"])
@login_required
def groupBEN():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    getusername = session['current_user']
    username = getusername.get('username')
    with open("static/data/B_text_data_en_4.json", "r") as f:
        data = json.load(f)

    texts = [d for d in data]

    global counter
    print("debugging which ", counter)
    if counter == len(texts):
        counter = 0
        return redirect("/thank-you")

    try:
        text = texts[counter]["Text"]

        intens = texts[counter]["Intensity"]
        if intens == 1:
            intens = "Intimidation"
        elif intens == 2:
            intens = "Offensive"
        elif intens == 3:
            intens = "Promotion of violence"
        elif intens == 0:
            intens = ""

        print("which counter", counter)

        label = texts[counter]["Label"]

        if request.method == "POST":

            form_id = request.form.get("hate")

            if form_id == "no":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }
                db.child("groupBEN").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupBEN.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)

            elif form_id == "yes":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }
                db.child("groupBEN").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupBEN.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)
            else:

                hate_label = texts[counter]["Label"]
                intens_label = texts[counter]["Intensity"]

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": hate_label,
                    "intensity_label": intens_label,
                    "text_id": counter,
                    "Person_annotator": "agrees with them"
                }

                db.child("groupBEN").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

            return render_template("groupBEN.html", text=text, texts=text, counter=counter, intens=intens, label=label)

    except IndexError:
        counter = 0
        return redirect("/thank-you")

    return render_template("groupBEN.html", text=text, texts=text, counter=counter, intens=intens, label=label)


@app.route("/cheer", methods=["POST"])
@login_required
def annotate3():
    global counter
    hate = request.form.get("hate")
    intensity = None
    if hate == "yes":
        intensity = request.form.get("intensity")
    counter += 1
    return redirect("/cheer")


''' Here is the group C for both languages '''
''' Interface for Group C for German '''

@app.route("/enjoyment", methods=["GET", "POST"])
@login_required
def groupCDE():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    getusername = session['current_user']
    username = getusername.get('username')
    with open("static/data/C_text_data_de_4.json", "r") as f:
        data = json.load(f)

    texts = [d for d in data]

    global counter
    print("debugging which ", counter)
    if counter == len(texts):
        counter = 0
        return redirect("/thank-you")

    try:
        text = texts[counter]["Text"]

        intens = texts[counter]["Intensity"]
        if intens == 1:
            intens = "Intimidation"
        elif intens == 2:
            intens = "Offensive"
        elif intens == 3:
            intens = "Promotion of violence"
        elif intens == 0:
            intens = ""

        print("which counter", counter)

        label = texts[counter]["Label"]

        if request.method == "POST":

            form_id = request.form.get("hate")

            if form_id == "no":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }

                db.child("groupCDE").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupCDE.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)

            elif form_id == "yes":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }

                db.child("groupCDE").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupCDE.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)
            else:

                hate_label = texts[counter]["Label"]
                intens_label = texts[counter]["Intensity"]

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": hate_label,
                    "intensity_label": intens_label,
                    "text_id": counter,
                    "Person_annotator": "agrees with them"
                }

                db.child("groupCDE").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

            return render_template("groupCDE.html", text=text, texts=text, counter=counter, intens=intens, label=label)

    except IndexError:
        counter = 0
        return redirect("/thank-you")

    return render_template("groupCDE.html", text=text, texts=text, counter=counter, intens=intens, label=label)


@app.route("/enjoyment", methods=["POST"])
@login_required
def annotate4():
    global counter
    hate = request.form.get("hate")
    intensity = None
    if hate == "yes":
        intensity = request.form.get("intensity")

    counter += 1
    return redirect("/enjoyment")

''' Interface for Group C for English '''

@app.route("/blessedness", methods=["GET", "POST"])
@login_required
def groupCEN():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    getusername = session['current_user']
    username = getusername.get('username')
    with open("static/data/C_text_data_en_4.json", "r") as f:
        data = json.load(f)

    texts = [d for d in data]

    global counter
    print("debugging which ", counter)
    if counter == len(texts):
        counter = 0
        return redirect("/thank-you")

    try:
        text = texts[counter]["Text"]

        intens = texts[counter]["Intensity"]
        if intens == 1:
            intens = "Intimidation"
        elif intens == 2:
            intens = "Offensive"
        elif intens == 3:
            intens = "Promotion of violence"
        elif intens == 0:
            intens = ""

        print("which counter", counter)

        label = texts[counter]["Label"]

        if request.method == "POST":

            form_id = request.form.get("hate")

            if form_id == "no":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }
                db.child("groupCEN").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupCEN.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)

            elif form_id == "yes":

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": request.form.get("hate"),
                    "intensity_label": request.form.get("intensity"),
                    "text_id": counter
                }

                db.child("groupCEN").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

                return render_template("groupCEN.html", text=text, texts=text, counter=counter, intens=intens,
                                       label=label)
            else:

                hate_label = texts[counter]["Label"]
                intens_label = texts[counter]["Intensity"]

                data = {
                    "username": username,
                    "text": text,
                    "hate_label": hate_label,
                    "intensity_label": intens_label,
                    "text_id": counter,
                    "Person_annotator": "agrees with them"
                }

                db.child("groupCEN").child(username).push(data)

                counter += 1
                text = texts[counter]["Text"]
                intens = texts[counter]["Intensity"]
                if intens == 1:
                    intens = "Intimidation"
                elif intens == 2:
                    intens = "Offensive"
                elif intens == 3:
                    intens = "Promotion of violence"
                elif intens == 0:
                    intens = ""
                label = texts[counter]["Label"]

            return render_template("groupCEN.html", text=text, texts=text, counter=counter, intens=intens, label=label)

    except IndexError:
        counter = 0
        return redirect("/thank-you")

    return render_template("groupCEN.html", text=text, texts=text, counter=counter, intens=intens, label=label)


@app.route("/blessedness", methods=["POST"])
@login_required
def annotate5():
    global counter
    hate = request.form.get("hate")
    intensity = None
    if hate == "yes":
        intensity = request.form.get("intensity")
    counter += 1
    return redirect("/blessedness")


''' Here is the group D for both languages - Dashboard Group '''

''' English dashboard Group D'''
@app.route('/satisfaction', methods=['GET', 'POST'])
@login_required
def groupDEN():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 20

    child_url = "/iframeen1"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "Seems like you cant get away from these parasites anymore its happening and getting worse everywhere "
    texts = get_similarity_text(Text, "English", 2)
    print("debugging", texts)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        # do something with the form data
        print('Selected class:', selected_class)
        print('Selected intensity:', selected_intensity)
        print('Selected intensity:', selected_action)

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text': Text,
                        'selected_class': selected_class,
                        'selected_intensity': selected_intensity,
                        'selected_action': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/satisfaction2")

    # If the request method is GET, return the form template
    return render_template('EN_part1.html', child_url=child_url, username=username, progress=progress, text=text)


@app.route('/satisfaction2', methods=['GET', 'POST'])
@login_required
def groupDEN2():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 40

    child_url = "/iframeen2"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "They only know how to destory our civilization"
    texts = get_similarity_text(Text, "English", 1)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        # do something with the form data
        print('Selected class:', selected_class)
        print('Selected intensity:', selected_intensity)
        print('Selected intensity:', selected_action)

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text2': Text,
                        'selected_class2': selected_class,
                        'selected_intensity2': selected_intensity,
                        'selected_action2': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/satisfaction3")

    # If the request method is GET, return the form template
    return render_template('EN_part2.html', child_url=child_url, username=username, progress=progress, text=text)


@app.route('/satisfaction3', methods=['GET', 'POST'])
@login_required
def groupDEN3():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 60

    child_url = "/iframeen3"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "The White race is best because when the Creator made Whites , He made them better than He made the other races"
    texts = get_similarity_text(Text, "English", 2)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        # do something with the form data
        print('Selected class:', selected_class)
        print('Selected intensity:', selected_intensity)
        print('Selected intensity:', selected_action)

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text3': Text,
                        'selected_class3': selected_class,
                        'selected_intensity3': selected_intensity,
                        'selected_action3': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/satisfaction4")

    # If the request method is GET, return the form template
    return render_template('EN_part3.html', child_url=child_url, username=username, progress=progress, text=text)


@app.route('/satisfaction4', methods=['GET', 'POST'])
@login_required
def groupDEN4():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 80

    child_url = "/iframeen4"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "Yeah, we could do with the same amount of black rapists as the Nordic countries are privileged enough to have"
    texts = get_similarity_text(Text, "English", 1)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        # do something with the form data
        print('Selected class:', selected_class)
        print('Selected intensity:', selected_intensity)
        print('Selected intensity:', selected_action)

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text4': Text,
                        'selected_class4': selected_class,
                        'selected_intensity4': selected_intensity,
                        'selected_action4': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/satisfaction5")

    # If the request method is GET, return the form template
    return render_template('EN_part4.html', child_url=child_url, username=username, progress=progress, text=text)


@app.route('/satisfaction5', methods=['GET', 'POST'])
@login_required
def groupDEN5():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 100

    child_url = "/iframeen5"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "Absolutely, whenever i see a dirty white coon with dreadlocks i get the urge to grab him by his flea blanket head and head butt him senseless"
    texts = get_similarity_text(Text, "English", 1)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        # do something with the form data
        print('Selected class:', selected_class)
        print('Selected intensity:', selected_intensity)
        print('Selected intensity:', selected_action)

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text5': Text,
                        'selected_class5': selected_class,
                        'selected_intensity5': selected_intensity,
                        'selected_action5': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/thank-you")

    # If the request method is GET, return the form template
    return render_template('EN_part5.html', child_url=child_url, username=username, progress=progress, text=text)

''' Get Texts and similarity'''
@app.route("/get_text_EN1")
def get_text_EN1():
    Text = "Seems like you cant get away from these parasites anymore its happening and getting worse everywhere "

    texts = get_similarity_text(Text, "English", 2)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})


@app.route("/get_text_EN2")
def get_text_EN2():
    Text = "They only know how to destory our civilization"

    texts = get_similarity_text(Text, "English", 1)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})


@app.route("/get_text_EN3")
def get_text_EN3():
    Text = "The White race is best because when the Creator made Whites , He made them better than He made the other races"

    texts = get_similarity_text(Text, "English", 2)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})


@app.route("/get_text_EN4")
def get_text_EN4():
    Text = "Yeah, we could do with the same amount of black rapists as the Nordic countries are privileged enough to have"

    texts = get_similarity_text(Text, "English", 1)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})


@app.route("/get_text_EN5")
def get_text_EN5():
    Text = "Absolutely, whenever i see a dirty white coon with dreadlocks i get the urge to grab him by his flea blanket head and head butt him senseless"

    texts = get_similarity_text(Text, "English", 2)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})

''' German dashboard Group D'''

@app.route('/glee', methods=['GET', 'POST'])
@login_required
def groupDDE():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 20

    child_url = "/iframe1"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "Oh Nein, die wollen auf unbewaffnete Schießen, die in der kälte stehen und deutsch können."

    texts = get_similarity_text(Text, "German", 0)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        # do something with the form data
        print('Selected class:', selected_class)
        print('Selected intensity:', selected_intensity)
        print('Selected intensity:', selected_action)

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text': Text,
                        'selected_class': selected_class,
                        'selected_intensity': selected_intensity,
                        'selected_action': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/glee2")

    # If the request method is GET, return the form template
    return render_template('DE_part1.html', child_url=child_url, username=username, progress=progress, text=text)


@app.route('/glee2', methods=['GET', 'POST'])
@login_required
def groupDDE2():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 40

    child_url = "/iframe2"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "Bei den geistigen Wegbereitern des IS wird keiner vorzeitig entlassen, denn ohne Kopf kommt man nicht weit. "

    print("debugging", Text)
    texts = get_similarity_text(Text, "German", 1)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        # do something with the form data
        print('Selected class:', selected_class)
        print('Selected intensity:', selected_intensity)
        print('Selected intensity:', selected_action)

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text2': Text,
                        'selected_class2': selected_class,
                        'selected_intensity2': selected_intensity,
                        'selected_action2': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/glee3")

    # If the request method is GET, return the form template
    return render_template('DE_part2.html', child_url=child_url, username=username, progress=progress, text=text)


@app.route('/glee3', methods=['GET', 'POST'])
@login_required
def groupDDE3():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 60

    child_url = "/iframe3"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "Der lasche Laschet ist und bleibt eine Lasche."

    print("debugging", Text)
    texts = get_similarity_text(Text, "German", 2)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        # do something with the form data
        print('Selected class:', selected_class)
        print('Selected intensity:', selected_intensity)
        print('Selected intensity:', selected_action)

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text3': Text,
                        'selected_class3': selected_class,
                        'selected_intensity3': selected_intensity,
                        'selected_action3': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/glee4")

    # If the request method is GET, return the form template
    return render_template('DE_part3.html', child_url=child_url, username=username, progress=progress, text=text)


@app.route('/glee4', methods=['GET', 'POST'])
@login_required
def groupDDE4():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 80

    child_url = "/iframe4"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "Ein Schwachkopf.Der gehört in die geschlossene."

    print("debugging", Text)
    texts = get_similarity_text(Text, "German", 2)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text4': Text,
                        'selected_class4': selected_class,
                        'selected_intensity4': selected_intensity,
                        'selected_action4': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/glee5")

    # If the request method is GET, return the form template
    return render_template('DE_part4.html', child_url=child_url, username=username, progress=progress, text=text)


@app.route('/glee5', methods=['GET', 'POST'])
@login_required
def groupDDE5():
    if 'current_user' not in session:
        return redirect('/')

    if 'logged_in' not in session:
        return redirect('/')

    progress = 100

    child_url = "/iframe5"

    getusername = session['current_user']
    username = getusername.get('username')

    Text = "Ach so- wenn im Namen des 'Islam' Menschen erniedrigt, gefoltert und getötet werden, dann sind das 'Rechte' der Muslime. Wenn aber islamistische Terror- Brüder wegen ihrer Verbrechen exekutiert werden, dann soll das ein Problem sein? Bevor jemand Al Sisi kritisiert, sollte er mal erst den eigenen Saustall ausmisten!"

    print("debugging", Text)
    texts = get_similarity_text(Text, "German", 2)

    text = random.choice(texts)

    if request.method == 'POST':

        selected_class = request.form.get('class')
        selected_intensity = request.form.get('intensity')
        selected_action = request.form.get('action')

        # do something with the form data
        print('Selected class:', selected_class)
        print('Selected intensity:', selected_intensity)
        print('Selected intensity:', selected_action)

        evaluations = db.child("evaluation_user").get()
        if evaluations.val() is None:
            db.child('evaluation_user').push({
                'Username': username,
                'text': Text,
                'selected_class': selected_class,
                'selected_intensity': selected_intensity,
                'selected_action': selected_action
            })
        else:
            user_found = False
            for evaluation in evaluations.each():
                if evaluation.val()["Username"] == username:
                    # if user already has an evaluation, update it
                    db.child("evaluation_user").child(evaluation.key()).update({
                        'text5': Text,
                        'selected_class5': selected_class,
                        'selected_intensity5': selected_intensity,
                        'selected_action5': selected_action,
                    })
                    user_found = True
                    break
            if not user_found:
                # if user not found, create a new evaluation
                db.child('evaluation_user').push({
                    'Username': username,
                    'text': Text,
                    'selected_class': selected_class,
                    'selected_intensity': selected_intensity,
                    'selected_action': selected_action
                })

        # render the template
        return redirect("/thank-you")

    # If the request method is GET, return the form template
    return render_template('DE_part5.html', child_url=child_url, username=username, progress=progress, text=text)

''' Get Texts and similarity'''

@app.route("/get_text_DE1")
def get_text_DE1():
    Text = "Oh Nein, die wollen auf unbewaffnete Schießen, die in der kälte stehen und deutsch können."

    texts = get_similarity_text(Text, "German", 0)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})


@app.route("/get_text_DE2")
def get_text_DE2():
    Text = "Bei den geistigen Wegbereitern des IS wird keiner vorzeitig entlassen, denn ohne Kopf kommt man nicht weit. "

    texts = get_similarity_text(Text, "German", 2)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})


@app.route("/get_text_DE3")
def get_text_DE3():
    Text = "Der lasche Laschet ist und bleibt eine Lasche."

    texts = get_similarity_text(Text, "German", 2)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})


@app.route("/get_text_DE4")
def get_text_DE4():
    Text = "Ein Schwachkopf.Der gehört in die geschlossene."

    texts = get_similarity_text(Text, "German", 2)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})


@app.route("/get_text_DE5")
def get_text_DE5():
    Text = "Ach so- wenn im Namen des 'Islam' Menschen erniedrigt, gefoltert und getötet werden, dann sind das 'Rechte' der Muslime. Wenn aber islamistische Terror- Brüder wegen ihrer Verbrechen exekutiert werden, dann soll das ein Problem sein? Bevor jemand Al Sisi kritisiert, sollte er mal erst den eigenen Saustall ausmisten!"

    texts = get_similarity_text(Text, "German", 2)
    current_index = session.get("current_index", 0)
    text = texts[current_index]
    session["current_index"] = (current_index + 1) % len(texts)
    # text = random.choice(texts)
    return jsonify({"text": text})


''' here are the I frames for the german language defined '''


@app.route('/iframe1')
@login_required
def iframeDE1():
    return render_template('DE_iframe_1.html')


@app.route('/iframe2')
@login_required
def iframeDE2():
    return render_template('DE_iframe_2.html')


@app.route('/iframe3')
@login_required
def iframeDE3():
    return render_template('DE_iframe_3.html')


@app.route('/iframe4')
@login_required
def iframeDE4():
    return render_template('DE_iframe_4.html')


@app.route('/iframe5')
@login_required
def iframeDE5():
    return render_template('DE_iframe_5.html')


''' here are the I frames for the english language defined '''


@app.route('/iframeen1')
@login_required
def iframeEN1():
    return render_template('EN_iframe_2.html')


@app.route('/iframeen2')
@login_required
def iframeEN2():
    return render_template('EN_iframe_2_1.html')


@app.route('/iframeen3')
@login_required
def iframeEN3():
    return render_template('EN_iframe_3.html')


@app.route('/iframeen4')
@login_required
def iframeEN4():
    return render_template('EN_iframe_4.html')


@app.route('/iframeen5')
@login_required
def iframeEN5():
    return render_template('EN_iframe_5.html')

''' Terms and conditions '''
@app.route('/terms')
@login_required
def terms():
    return render_template('terms.html')

''' Thumbs up and down '''
@app.route('/glee/<string:rating>/<string:action>', methods=['POST'])
def thumbs_action(rating, action):
    rating_ref = db.child('UserReview').child(
        session['current_user']['username']).child(rating)
    if action == 'up':
        rating_ref.set('helpful')
    elif action == 'down':
        rating_ref.set('not helpful')
    return '', 204

''' User review '''
@app.route('/glee', methods=['POST'])
def review():
    review_data = request.form.to_dict()
    username = session['current_user']['username']
    db.child('UserReview').child(username).set(review_data)
    return '', 204
