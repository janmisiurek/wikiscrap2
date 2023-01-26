from flask import render_template, Blueprint, request

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        from . import get_tables

        url = request.form.get('url')
        pageTables = get_tables(url)
        tablesAmount = pageTables['n_tables']
        pageTitle = pageTables['site']
        tables = pageTables['tables']
        tablesTitles = pageTables['titles']
        tablesHTML = []
        for table in tables:
            tablesHTML.append(table.to_html())

        return render_template(
            "home.html",
            tablesAmount = tablesAmount,
            pageTitle = pageTitle,
            tables = tablesHTML,
            tablesTitles = tablesTitles
        )
    else:
        return render_template("home.html")