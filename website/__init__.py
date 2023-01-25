from flask import Flask
import requests
from bs4 import BeautifulSoup
import pandas as pd

def create_app():
    app = Flask(__name__)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    return app

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
        
        if len(tables) > 1:
            t_title = table.find_previous('h2').text
        else:
            t_title = bf_site.find('h1').text
        df_titles.append(clean(t_title))
            
        raw_df = pd.read_html(str(table))
        df = pd.DataFrame(raw_df[0]).replace(r'^\s*$', np.nan, regex=True).dropna(how='all', axis=1)
        df_tables.append(df)
        
    return {'tables':df_tables, 'titles':df_titles, 'site':s_title, 'n_tables':n_tables}
