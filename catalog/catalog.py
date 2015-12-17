import flask
from sqlalchemy import create_engine, asc
from database import Base, Category, Item, get_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# Create Flask app object
app = flask.Flask(__name__)

# Get database session
session = get_session()

#
# PAGE TEMPLATE BUILDING
#

# Builds entire page based on provided page name
def build_page(page_name, params = {}):
    html = ''

    # Get start of page
    html = html + flask.render_template('page_start.html')

    # Get title bar
    html = html + build_title_bar()

    # Get requested page's content
    html = html + globals()['build_' + page_name + '_content'](params)

    # Get end of page
    html = html + flask.render_template('page_end.html')

    return html

# Builds title bar of page
def build_title_bar():
    html = ''

    # Generate HTML for title bar
    html = flask.render_template('title.html', email=get_email())

    return html

# Builds 'access_denied' page
def build_access_denied_content(params):
    html = ''
    item = ''
    item_name = ''

    # Build HTML
    html = flask.render_template('access_denied.html', message=params)

    return html

# Builds 'catalog' page
def build_catalog_content(params):
    html = ''

    # Get list of all categories
    categories = get_all_categories()

    # Get items created latest in the system
    latest_items = get_latest_items()

    # Render HTML
    html = flask.render_template('catalog.html', categories=categories, latest_items=latest_items)

    return html

# Builds 'category' page
def build_category_content(params):
    html = ''
    items = ''

    # Get category data
    category = get_category_by_name(params["category_name"])

    # Get items for category
    if category:
        items = get_items_by_category_id(category.id)

    # Build HTML
    html = flask.render_template('category.html', email=get_email(), category=category, items=items)

    return html

# Builds 'item' page
def build_item_content(params):
    html = ''
    item = ''

    # Get category data
    category = get_category_by_name(params["category_name"])

    # Get item data
    if category:
        item = get_item_by_name(category.id, params["item_name"])

    # Build HTML
    html = flask.render_template('item.html', email=get_email(), category=category, item=item)

    return html

# Builds 'item_editor' page
def build_item_editor_content(params):
    html = ''
    item = ''
    item_name = ''

    # Get category data
    category = get_category_by_name(params["category_name"])

    # Get list of all categories
    categories = get_all_categories()

    # Get item data
    if category and 'item_name' in params:
        item_name = params["item_name"]
        item = get_item_by_name(category.id, params["item_name"])

    # Build HTML
    html = flask.render_template('item_editor.html', email=get_email(), item_name=item_name, categories=categories, category=category, item=item)

    return html

# Builds 'item_delete' page
def build_item_delete_content(params):
    html = ''
    item = ''
    item_name = ''

    # Get category data
    category = get_category_by_name(params["category_name"])

    # Get list of all categories
    categories = get_all_categories()

    # Get item data
    if category and 'item_name' in params:
        item_name = params["item_name"]
        item = get_item_by_name(category.id, params["item_name"])

    # Build HTML
    html = flask.render_template('item_delete.html', email=get_email(), item_name=item_name, categories=categories, category=category, item=item)

    return html

#
# ACCOUNT HANDLING
#

# Returns true if user is logged in via Google
def is_logged_in():
    if 'credentials' in flask.session:
        return True
    else:
        return False

# Returns email address of logged in user
def get_email():
    if 'credentials' in flask.session:
        return flask.session['credentials']['id_token']['email']
    else:
        return ''

#
# CATEGORY HANDLING
#

# Returns list of categories in db, sorted by name of category
def get_all_categories():
    return session.query(Category).order_by(Category.name.asc()).all()

# Return data for requested category
def get_category_by_name(name):
    return session.query(Category).filter_by(name = name).first()


#
# ITEM HANDLING
#

# Returns list of latest items by created datetime
def get_latest_items():
    return session.query(Item).order_by(Item.created.desc()).all()

# Returns item from database by category and item name
def get_item_by_name(category_id, item_name):
    return session.query(Item).filter_by(category_id = category_id, name = item_name).first()

# Returns all items in category
def get_items_by_category_id(category_id):
    return session.query(Item).filter_by(category_id = category_id).order_by(Item.name.asc()).all()

# Handle adding/editing of items
# Returns true if item is successfully added/edited.  False (with Flash messages) otherwise
def handle_item_editor_form(category_name, item_name, form_data):
    item_being_edited = ''
    item_to_add = ''

    # Make sure form field was filled out properly.  All fields are required
    # If a field is blank, inform user and do not save
    if flask.request.form['name'] == '' or flask.request.form['category'] == '' or flask.request.form['desc'] == '':
        flask.flash('An error occured when attempting to save data:')
        flask.flash('A field was blank. All fields are required')
        return False

    # Get category data for provided category name
    cat_data = get_category_by_name(flask.request.form['category'])

    # Are we editing an existing item?  Get existing item data
    if flask.request.form['item_id'] != '':
        item_being_edited = get_item_by_name(cat_data.id, item_name)

    # Search for item in DB that has the same name as the name from the form
    item_with_form_name = get_item_by_name(cat_data.id, flask.request.form['name'])

    # Is name from form the same name as an existing item in the category (and we aren't just editing that item)?  Complain
    if (item_with_form_name and (item_being_edited == '' or item_being_edited.id != item_with_form_name.id)):
        flask.flash('Item not added! An item with name \'' + flask.request.form['name'] + '\' already exists in category \'' + category_name + '\'')
        return False

    # Build item to add to database
    # Is item being edited?
    if item_being_edited:
        session.query(Item).filter_by(id=item_being_edited.id).update({'name': flask.request.form['name'], 'category_id': cat_data.id, 'desc': flask.request.form['desc']})

    # Item is being added
    else:
        item_to_add = Item(name=flask.request.form['name'], category_id=cat_data.id, desc=flask.request.form['desc'], creator=get_email())
        session.add(item_to_add)
        session.commit()

    # Inform user of success
    if item_being_edited:
        flask.flash("Successfully updated!")
    else:
        flask.flash("Successfully added!")

    return True

#
# APP ROUTING
#

# Root, redirects to /catalog
@app.route('/')
def index():

    # Get full HTML for index page
    return flask.redirect('/catalog')

# Catalog, displays the main catalog page including list of categories and the latest items in the database
@app.route('/catalog/')
def catalog():

    # Get full HTML for index page
    return build_page('catalog')

# Exports database to JSON
@app.route('/catalog/json/')
def exportToJson():
    catalog_data = {'Category': []}

    # Get all categories
    categories = get_all_categories()

    # Spin through categories
    for category in categories:
        category_data = {'id': category.id, 'name':category.name, 'items':[]}

        # Get items for category
        cat_items = get_items_by_category_id(category.id)

        # Spin through items
        for item in cat_items:
            category_data['items'].append({'id': item.id, 'name': item.name, 'desc': item.desc})

        # Add category data to catalog data
        catalog_data['Category'].append(category_data)

    # Send JSON to browser
    return json.dumps(catalog_data)

# Display items in category, giving logged-in users a link to add items
@app.route('/catalog/<category_name>/')
def category(category_name):

    # Show logged in page which will close window and refresh parent page
    return build_page('category', {'category_name': category_name})

# Displays screen to add item to category
@app.route('/catalog/<category_name>/add/', methods=['GET', 'POST'])
def addItem(category_name):

    # User must be logged in to see this page
    if is_logged_in() == False:
      return build_page('access_denied')

    # Did user submit editor form?
    if flask.request.method == 'POST':

        # Add/edit item
        result = handle_item_editor_form(category_name, '', flask.request.form)

        # Success?  Show item page
        if result == True:
            return build_page('item', {'category_name': flask.request.form['category'], 'item_name': flask.request.form['name']})

    # Show logged in page which will close window and refresh parent page
    return build_page('item_editor', {'category_name': category_name})

# Shows item details
@app.route('/catalog/<category_name>/<item_name>/')
def item(category_name, item_name):

    # Show logged in page which will close window and refresh parent page
    return build_page('item', {'category_name': category_name, 'item_name': item_name})

# Displays item editor page, allowing them to change properties of an item they created
@app.route('/catalog/<category_name>/<item_name>/edit/', methods=['GET', 'POST'])
def editItem(category_name, item_name):

    # Get category data
    cat_data = get_category_by_name(category_name)

    # Get item user is trying to delete
    item = get_item_by_name(cat_data.id, item_name)

    # User must be logged in to see this page
    if is_logged_in() == False:
      return build_page('access_denied')

    # User must be the creator to edit
    if item.creator != get_email():
        return build_page('access_denied', 'You can only edit items that you created.')

    # Did user submit editor form?
    if flask.request.method == 'POST':

        # Add/edit item
        result = handle_item_editor_form(category_name, item_name, flask.request.form)

        # Success?  Show item page
        if result == True:
            return build_page('item', {'category_name': flask.request.form['category'], 'item_name': flask.request.form['name']})

    # Show logged in page which will close window and refresh parent page
    return build_page('item_editor', {'category_name': category_name, 'item_name': item_name})

# Displays item deletion page, allowing users to delete items that they created
@app.route('/catalog/<category_name>/<item_name>/delete/', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):

    # Get category data
    cat_data = get_category_by_name(category_name)

    # Get item user is trying to delete
    item = get_item_by_name(cat_data.id, item_name)

    # User must be logged in to see this page
    if is_logged_in() == False:
      return build_page('access_denied')

    # User must be the creator to delete
    if item.creator != get_email():
        return build_page('access_denied', 'You can only delete items that you created.')

    # Did user submit editor form?
    if flask.request.method == 'POST':

        session.delete(item)
        session.commit()

        # Let user know deletion was successful
        flask.flash("Successfully deleted!")

        # Send user to category page
        return build_page('category', {'category_name': category_name})

    # Show logged in page which will close window and refresh parent page
    return build_page('item_delete', {'category_name': category_name, 'item_name': item_name})

# Performs Google authentication
@app.route('/gauth')
def gauth():
    
    # Create OAUTH2 flow
    #   - Redirects back here to provide us with the authentication code that we would then turn into credentials
    flow = flow_from_clientsecrets('client_secrets.json', scope='openid email', redirect_uri=flask.url_for('gauth', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = json.loads(credentials.to_json())

        # Let user know they were logged in
        flask.flash('Successfully logged in!')
        return flask.redirect(flask.url_for('logged_in'))

# User is logged in
#   - Closes google auth window and refreshes parent window to reflect logged-in status
@app.route('/logged_in')
def logged_in():

    # Show logged in page which will close window and refresh parent page
    return flask.render_template('logged_in.html')

# Logs user out of server
@app.route('/logout')
def logout():
    
    # Clear session
    flask.session.clear()

    # Inform user they were logged out
    flask.flash('Successfully logged out!')
    
    # Send them back to the index
    return flask.redirect(flask.url_for('index'))


# Start web server
if __name__ == '__main__':
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug = False
    app.run(host='0.0.0.0', port=5000)




