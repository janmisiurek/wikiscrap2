from flask import render_template, Blueprint, request

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        from . import get_tables
        
        url = request.form.get('url')
        if url is not None:

            global pageTables 
            pageTables = get_tables(url)
            global tablesAmount
            tablesAmount = pageTables['n_tables']
            global pageTitle
            pageTitle = pageTables['site']
            global tables
            tables = pageTables['tables']
            global tablesTitles
            tablesTitles = pageTables['titles']
            global tablesHTML
            tablesHTML = []
            global tableView
            tableView = ''
            
            for table in tables:
                tablesHTML.append(table.to_html())


        tableID = request.form.get('tableID')
        if tableID is not None:
            tableView = tablesHTML[int(tableID)]

        return render_template(
            "home.html",
            tablesAmount = tablesAmount,
            pageTitle = pageTitle,
            tables = tablesHTML,
            tablesTitles = tablesTitles,
            tableView = tableView
        )
    else:
        return render_template("home.html")