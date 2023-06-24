from functools import wraps

import pandas as pd
import pyrebase
from flask import redirect, url_for, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

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
db = firebase.database()

''' Check if the user is already in the database '''
def check_username_and_token(username, token):
    users = db.child("User").get().val()
    if users is None:
        return False
    for user in users:
        if users[user]["username"] == username and users[user]["token"] == token:
            return True
    return False


''' Move the User to the corresponding case study '''
def redirect_to_case_study(group, language):
    if group == 'A' and language == 'English':
        return redirect("/Joi")
    elif group == 'B' and language == 'English':
        return redirect("/cheer")
    elif group == 'C' and language == 'English':
        return redirect("/blessedness")
    elif group == 'D' and language == 'English':
        return redirect("/satisfaction")
    elif group == 'A' and language == 'German':
        return redirect("/Love")
    elif group == 'B' and language == 'German':
        return redirect("/Happiness")
    elif group == 'C' and language == 'German':
        return redirect("/enjoyment")
    elif group == 'D' and language == 'German':
        return redirect("/glee")

''' Check if the user is logged in '''
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            # User is logged in, execute the function
            return f(*args, **kwargs)
        else:
            # User is not logged in, redirect to login page
            return redirect(url_for('/'))

    return decorated_function

''' Load the dataset for the corresponding language '''

def load_dataset(language):
    if language == 'English':
        dataset = pd.read_excel(
            'static/data/english_intens_noTest.xlsx').dropna()
        return dataset
    elif language == 'German':
        dataset = pd.read_excel(
            'static/data/german_intens_noTest.xlsx').dropna()
        return dataset

''' Get the similarity of the text '''
def get_similarity_text(Text: str, language: str, intensity: int):
    data = load_dataset(language)
    data_int = data[data['Label'] == intensity]
    dataset = data_int['Text'].tolist()
    input_texts = [Text]

    vec = TfidfVectorizer(max_features=10_000)
    features = vec.fit_transform(data_int['Text'])
    knn = NearestNeighbors(n_neighbors=3, metric='euclidean')
    knn.fit(features)
    knn.kneighbors(features[0:1], return_distance=True)
    input_features = vec.transform(input_texts)

    D, N = knn.kneighbors(input_features, n_neighbors=20, return_distance=True)
    nearest = []
    for input_text, distances, neighbors in zip(input_texts, D, N):
        for dist, neighbor_idx in zip(distances, neighbors):
            text = dataset[neighbor_idx]
            words = text.split()
            # Only append text with more than three words
            if len(words) > 3:
                nearest.append(text)

    unique_list = [x for i, x in enumerate(nearest) if x not in nearest[:i]]
    nearest_text = unique_list[:10]
    return nearest_text
