import json
import os

from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Необходимо для использования сессий

# Директория для хранения файлов истории поиска пользователей
history_dir = 'user_histories'

if not os.path.exists(history_dir):
    os.makedirs(history_dir)

def get_user_history_file(username):
    return os.path.join(history_dir, f'{username}_history.json')

def read_search_history(username):
    history_file = get_user_history_file(username)
    try:
        with open(history_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def write_search_history(username, history):
    history_file = get_user_history_file(username)
    with open(history_file, 'w') as file:
        json.dump(history, file)

def add_to_search_history(username, query):
    history = read_search_history(username)
    history.append(query)
    write_search_history(username, history)

def search(query):
    search_url = f"https://www.google.com/search?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    response = requests.get(search_url, headers=headers)  # Исправлено на requests.get
    soup = BeautifulSoup(response.text, 'html.parser')

    results = soup.find_all('div', class_='tF2Cxc')
    links = []

    for result in results:
        link_tag = result.find('a')
        if link_tag:
            link = link_tag['href']
            links.append(link)

    return links

@app.route('/')
def index():
    if 'username' in session:
        history = read_search_history(session['username'])
        return render_template('index.html', history=history, username=session['username'])
    return redirect(url_for('login'))

@app.route('/search', methods=['POST'])
def search_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    query = request.form['query']
    add_to_search_history(session['username'], query)
    results = search(query)
    return render_template('results.html', query=query, results=results, username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
