'''
This app has two types of users: regular users and an admin
To login as the administrator, the user name is admin and the password is 123
as an admin you will find an extra link the /menu route and others

In the /add_product route to add an image to your product you must type the name of the image and filetype of a file in the 
static folder eg. Salmon.jpg . To use the default image leave the box blank

If a regular user tries to access an admin only area by knowing the they will be redirected to the menu

Choose register in the /menu route to register as a regular user 

In the /checkout route you will be asked if you want to pay with cash or card, you can pick either as they only change what
is written on the receipt 
'''
from flask import Flask, render_template, request, session, redirect, url_for, g
from database import get_db, close_db
from forms import RegistrationForm, FilterForm, LoginForm, CheckoutForm, AddProductForm, UpdatePriceForm
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.teardown_appcontext(close_db)
Session(app)

@app.before_request
def load_logged_in_user():
    g.user = session.get('user_id', None)
    g.admin = session.get('admin', None)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.admin is None:
            return redirect( url_for('menu') )
        return view(*args, **kwargs)
    return wrapped_view

@app.errorhandler(404)
def error(error):
    return render_template('errors.html', stylesheet=url_for('static', filename='register_stylesheet.css')), 404

@app.route('/')
def mainPage():
    return render_template('opening_page.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        conflict_user = db.execute(
            '''SELECT * FROM users
               WHERE user_id = ?;''', (user_id,)).fetchone()
        if conflict_user is not None:
            form.user_id.errors.append('User name taken')
        else:
            db.execute(
                '''INSERT INTO users (user_id, password)
                   VALUES (?, ?);''',
                   (user_id, generate_password_hash(password)))
            db.commit()
            return redirect( url_for('login') )
    return render_template('register.html', form=form, title='Register', stylesheet=url_for('static', filename='register_stylesheet.css'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data 
        db = get_db()
        user = db.execute(
            '''SELECT * FROM users
               WHERE user_id = ?;''', (user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append('No such user name!')
        elif not check_password_hash(user['password'], password):
            form.password.errors.append('Incorrect password!')
        else:
            session.clear()
            if user['admin'] == 1:
                session['admin'] = user['admin']
            session['user_id'] = user_id
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('menu')
            return redirect(next_page)
    return render_template('login.html', form=form, title='Login', stylesheet=url_for('static', filename='login_stylesheet.css'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect( url_for('menu') )

@app.route('/menu' , methods=['GET', 'POST'])
def menu():
    form = FilterForm()
    db = get_db()
    variety = form.variety.data
    alcoholic = form.alcoholic.data
    if form.validate_on_submit():
        if alcoholic == 'Both' and variety == 'Both':
            menu = db.execute('''SELECT * FROM menu''').fetchall()
        elif alcoholic == 'Both':
            menu = db.execute('''
                            SELECT * FROM menu
                            WHERE type = ?;''', (variety,)).fetchall() 
        elif alcoholic == 'Alcoholic':
            if variety == 'Both':
                menu = db.execute('''
                                SELECT * FROM menu
                                WHERE alcoholic = ?;''', (alcoholic,)).fetchall() 
            else:
                 menu = db.execute('''
                                SELECT * FROM menu
                                WHERE type = ? 
                                AND alcoholic = ?;''', (variety, alcoholic)).fetchall() 
        else:
            if variety == 'Both':
                menu = db.execute('''
                                SELECT * FROM menu
                                WHERE alcoholic = ?;''', (alcoholic,)).fetchall() 
            else:
                 menu = db.execute('''
                                SELECT * FROM menu
                                WHERE type = ? 
                                AND alcoholic = ?;''', (variety, alcoholic)).fetchall()
    else:
        menu = db.execute('''SELECT * FROM menu''').fetchall()
    return render_template('menu.html', menu=menu, form=form, title='Menu', stylesheet=url_for('static', filename='menu_stylesheet.css'))

@app.route('/cart')
@login_required
def cart():
    if 'cart' not in session:
        session['cart'] = {}
    names = {}
    price = 0
    db = get_db()
    for item_id in session['cart']:
        item = db.execute('''SELECT * FROM menu
                             WHERE item_id = ?;''', (item_id,)).fetchone()
        name = item['name']
        names[item_id] = name
        price += round(float(item['price']) * session['cart'][item_id], 2)
    price = round(price, 2)

    return render_template('cart.html', cart=session['cart'], names=names, total=price, title='Cart', stylesheet=url_for('static', filename='cart_stylesheet.css'))

@app.route('/add_to_cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    if 'cart' not in session:
        session['cart'] = {}
    if item_id not in session['cart']:
        session['cart'][item_id] = 1
    else:
        session['cart'][item_id] = session['cart'][item_id] + 1
    session.modified = True
    return redirect( url_for('cart') )

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    session['cart'][item_id] -= 1
    if session['cart'][item_id] <= 0:
        del session['cart'][item_id]
    session.modified = True

    return redirect( url_for('cart') )

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if 'cart' not in session:
        session['cart'] = {}
    form = CheckoutForm()
    #show total
    price = 0
    names = {}
    db = get_db()
    for item_id in session['cart']: 
        item = db.execute('''SELECT * FROM menu
                             WHERE item_id = ?;''', (item_id,)).fetchone()
        price += round(float(item['price']) * session['cart'][item_id], 2)
        name = item['name']
        names[item_id] = name
    price = round(price, 2)
    if form.validate_on_submit():
        if 'order' not in session:
            session['order'] = {}
        session['order']['tableNumber'] = form.table_number.data
        session['order']['paymentMethod'] = form.payment_method.data
        session['order']['cart'] = session['cart'] 
        session['cart'] = {}       
        return render_template('receipt.html', order=session['order'], names=names, total=price, title='Receipt', stylesheet=url_for('static', filename='receipt_stylesheet.css'))
    return render_template('checkout.html', cart=session['cart'], names=names, total=price, form=form, title='Checkout', stylesheet=url_for('static', filename='checkout_stylesheet.css'))
    
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        alcoholic = form.alcoholic.data
        type = form.type.data
        if form.picture.data == '':
            picture = 'default.jpeg' 
        else:
            picture = form.picture.data

        db = get_db()
        db.execute(
                '''INSERT INTO menu (name, price, alcoholic, type, picture)
                   VALUES (?, ?, ?, ?, ?);''',
                   (name, price, alcoholic, type, picture))
        db.commit()

    return render_template('add_product.html', form=form, title='Add Product', stylesheet=url_for('static', filename='add_product_stylesheet.css')) 

@app.route('/admin_console')
@login_required
@admin_required
def admin_console():
    db = get_db()
    menu = db.execute('''SELECT * FROM menu''').fetchall()
    item_id = db.execute('''SELECT item_id FROM menu''').fetchall()
    return render_template('admin_console.html', menu=menu, item_id=item_id, title='Admin Console', stylesheet=url_for('static', filename='admin_console_stylesheet.css'))

@app.route('/remove_product/<int:item_id>')
@login_required
@admin_required
def remove_product(item_id):
    db = get_db()
    db.execute('''DELETE FROM menu 
                WHERE item_id = ?;''', (item_id, ))
    db.commit()

    return redirect( url_for('admin_console') )

@app.route('/update_price/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_product(item_id):
    form = UpdatePriceForm()     
    if form.validate_on_submit():
        price = form.price.data
        db = get_db()
        db.execute('''UPDATE menu Set price = ?
                    WHERE item_id = ?''', (price, item_id))
        db.commit()
        return redirect( url_for('admin_console') )
    return render_template('update_price.html', form=form, title='Update Price', stylesheet=url_for('static', filename='update_price_stylesheet.css'))