from flask import Flask, send_file
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import io

db = SQLAlchemy()
DB_NAME = "database.db"

#app setup
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cokolwiek'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    db.init_app(app)

    from .models import User, Table

    create_database(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    login_menager = LoginManager()
    login_menager.login_view = 'auth.login' 
    login_menager.init_app(app)
    
    @login_menager.user_loader 
    def load_user(id):
        return User.query.get(int(id))

    return app

#formating titles
def clean(title):
    title = title.replace('(','').replace(')','')
    if '[' in title:
        return title[:title.index('[')]
    else:
        return title

#scraping taples
def get_tables(url):
    
    site = requests.get(url)
    bf_site = BeautifulSoup(site.text, "html")
    tables = []
    tables = bf_site.find_all('table', class_='wikitable')
    s_title = bf_site.find('span', class_='mw-page-title-main').text
    n_tables = len(tables)
    df_tables = []
    df_titles = []

    
    for table in tables:
        
        #scraping title
        if len(tables) > 1:
            t_title = table.find_previous('h2').text
        else:
            t_title = bf_site.find('h1').text
        df_titles.append(clean(t_title))
            
        #reading and cleaning table
        raw_df = pd.read_html(str(table))
        df = pd.DataFrame(raw_df[0]).replace(r'^\s*$', np.nan, regex=True).dropna(how='all', axis=1)
        df_tables.append(df)

    return {'tables':df_tables, 'titles':df_titles, 'site':s_title, 'n_tables':n_tables}


def create_database(app):
    if not path.exists('website' + DB_NAME):

        with app.app_context():
            db.create_all()
            print('Created Database')

#sending table in chosen file format
def send_table(df, downloadFormat):
    file = io.BytesIO()
    if downloadFormat == 'csv':
        df.to_csv(file, index=False)
        file.seek(0)
        return send_file(file, as_attachment=True, download_name='table.csv')

    if downloadFormat == 'xlsx':
        df.to_excel(file, index=False)
        file.seek(0)
        return send_file(file, as_attachment=True, download_name='table.xlsx')

    if downloadFormat == 'json':
        df.to_json(file)
        file.seek(0)
        return send_file(file, as_attachment=True, download_name='table.json')