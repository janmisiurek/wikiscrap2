from flask import render_template, Blueprint, request, send_file, flash, redirect
from flask_login import LoginManager, UserMixin, login_required, current_user
import pandas as pd
import io
import json
from .import db, send_table, get_tables
from .models import Table, User

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

        global tableID
        tableID = request.form.get('tableID')
        if tableID is not None:
            tableView = tablesHTML[int(tableID)]
            global df
            df = tables[int(tableID)]
            global name
            name = tablesTitles[int(tableID)]
            global data
            data = df.to_json()
        else:
            tableView =''

        downloadFormat = request.form.get('downloadFormat')
        if downloadFormat is not None:
                return send_table(df, downloadFormat)

        saveTable = request.form.get('saveTable')
        if saveTable is not None:
            new_table = Table(name=name, data=data, user_id=current_user.id)
            db.session.add(new_table)
            db.session.commit()
            flash('Table saved successfully', category='success')
                    
        return render_template(
                "home.html",
                tablesAmount = tablesAmount,
                pageTitle = pageTitle,
                tables = tablesHTML,
                tablesTitles = tablesTitles,
                tableView = tableView,
                user = current_user
                )

    else:
        return render_template("home.html", user=current_user, isWiki=False)



@views.route('/my-tables', methods=['GET', 'POST'])
@login_required
def my_tables():
    if request.method == 'POST':

        #getting id for table to edit, and redirect to edit page
        global editID
        editID = request.form.get('editID')
        if editID is not None:
            return redirect('/edit')

        #menaging dowload
        downloadFormat = request.form.get('downloadFormat')
        if downloadFormat is not None:
            id = request.form.get('id')
            tableToDownload = Table.query.get(id)
            data = tableToDownload.data
            df = pd.DataFrame.from_dict(json.loads(data))
            return send_table(df, downloadFormat)
        

    else:
        return render_template("my_tables.html", user=current_user)


@views.route('delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    tableToDelete = Table.query.get(id)
    try:
        db.session.delete(tableToDelete)
        db.session.commit()
        return redirect('/my-tables')
    except:
        return 'error'

@views.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():

    #loading table chosen from my-tables page, set up the view of tabe
    if request.method == 'GET':
        global tableToEdit
        tableToEdit = Table.query.get(editID)
        data = tableToEdit.data
        global dfEdit
        dfEdit = pd.DataFrame.from_dict(json.loads(data))
        global title
        title = tableToEdit.name
        global table
        table = dfEdit.to_html()
        global tableView
        tableView = dfEdit.head().to_html()
        global columns
        columns = dfEdit.columns.to_list()
        view = 'head'

        return render_template('edit.html', table=tableView, title=title, columns=columns, view=view, user=current_user)

    if request.method == 'POST':
        
        #editing title of table
        newTitle = request.form.get('newTitle')
        if newTitle:
            title=newTitle

        #editing names of columns
        for i in range(len(columns)+1):
            columnName = request.form.get(f"column{i}")
            newColumnName = request.form.get(f"newColumnName{i}")
            if newColumnName:
                dfEdit.rename(columns={columnName: newColumnName}, inplace=True)
                table = dfEdit.to_html()
                columns = dfEdit.columns.to_list()
                tableView = dfEdit.head().to_html()

        #deleting columns
        columnToDelete = request.form.get('delete')
        if columnToDelete:
            dfEdit.drop(columnToDelete, axis=1, inplace=True)
            table = dfEdit.to_html()
            columns = dfEdit.columns.to_list()
            tableView = dfEdit.head().to_html()

        #menaging the view of table
        view = request.form.get('view')
        if view == 'all':
            tableView = table
        if view == 'head':
            tableView = dfEdit.head().to_html()

        #fixing view parameter after editing
        if tableView == table:
            view = 'all'
        if tableView == dfEdit.head().to_html():
            view = 'head'
        
        #dowlaod section
        downloadFormat = request.form.get('downloadFormat')
        if downloadFormat is not None:
            df = dfEdit
            return send_table(df, downloadFormat)


        #saving as new table
        saveTableAsNew = request.form.get('saveTableAsNew')
        if saveTableAsNew:
            data = dfEdit.to_json()
            new_table = Table(name=title, data=data, user_id=current_user.id)
            db.session.add(new_table)
            db.session.commit()
            flash('Table saved successfully', category='success')

        #saving changes 
        saveTable = request.form.get('saveTable')
        if saveTable:
            tableToEdit = Table.query.get(editID)
            tableToEdit.name = title
            tableToEdit.data = dfEdit.to_json()
            try:
                db.session.commit()
                flash('Table saved successfully', category='success')
            except:
                flash('Ups.. somthing went wrong :(', category='error')

            
        return render_template('edit.html', table=tableView, title=title, columns=columns, view=view, user=current_user)
