from app import app
from flask import render_template

@app.route('/')
def index():
    user = {
        'name':'Zoe'
    }
    return render_template('index.html')