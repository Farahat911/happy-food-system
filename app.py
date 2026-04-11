import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.secret_key = 'happy_food_secret_key_123' 

db = SQLAlchemy(app)

# -------------------------------------------------------------
# نوت ليا: ضفت جدول الرسايل عشان العملاء يقدروا يتواصلوا معانا
# -------------------------------------------------------------
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='food1.png')

with app.app_context():
    db.create_all()
    if not MenuItem.query.first():
        item1 = MenuItem(name='LASAL CHEESE', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=18.00, image_file='food1.png')
        item2 = MenuItem(name='JUMBO CRAB SHRIMP', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=24.00, image_file='food2.png')
        db.session.add_all([item1, item2])
        db.session.commit()

@app.route('/')
def home():
    menu_items = MenuItem.query.all()
    return render_template('index.html', menu_items=menu_items)

@app.route('/menu')
def menu():
    menu_items = MenuItem.query.all()
    return render_template('menu.html', menu_items=menu_items)

@app.route('/contact', methods=['POST'])
def save_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    new_message = Contact(name=name, email=email, subject=subject, message=message)
    db.session.add(new_message)
    db.session.commit()

    flash('Your message has been sent successfully! Thank you for contacting us.', 'success')
    return redirect(url_for('home', _anchor='contact'))

# =========================================================
# نوت ليا: نظام السلة (Cart System) اللي عملناه جديد
# =========================================================

@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append(item_id)
    session.modified = True
    flash('Item added to your bag!', 'success')
    return redirect(url_for('menu'))

@app.route('/cart')
def view_cart():
    cart_item_ids = session.get('cart', [])
    item_counts = {}
    for item_id in cart_item_ids:
        item_counts[item_id] = item_counts.get(item_id, 0) + 1
        
    items_in_cart = []
    total_price = 0
    for item_id, quantity in item_counts.items():
        item = MenuItem.query.get(item_id)
        if item:
            item_data = {
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'quantity': quantity,
                'subtotal': item.price * quantity
            }
            items_in_cart.append(item_data)
            total_price += item_data['subtotal']
            
    return render_template('cart.html', items=items_in_cart, total=total_price)

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    if 'cart' in session:
        cart_list = session['cart']
        if item_id in cart_list:
            cart_list.remove(item_id)
            session.modified = True
            flash('Item quantity decreased!', 'success')
    return redirect(url_for('view_cart'))
@app.route('/add_one/<int:item_id>')
def add_one(item_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(item_id)
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/remove_all/<int:item_id>')
def remove_all(item_id):
    if 'cart' in session:
        session['cart'] = [id for id in session['cart'] if id != item_id]
        session.modified = True
        flash('Item removed completely.', 'success')
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    flash('Order placed successfully!', 'success')
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)