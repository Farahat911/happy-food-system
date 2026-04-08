import os 
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# إعدادات قاعدة البيانات والسيرفر
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'happy_food_secret_key_123' 

db = SQLAlchemy(app)

# موديل المنيو
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='food1.png')

# إنشاء قاعدة البيانات وإضافة البيانات التجريبية
with app.app_context():
    db.create_all()
    if MenuItem.query.count() < 12:
        MenuItem.query.delete() 
        items = [
            MenuItem(name='LASAL CHEESE', description='Delicious cheese pasta.', price=18.00, image_file='food1.png'),
            MenuItem(name='JUMBO CRAB SHRIMP', description='Fresh seafood platter.', price=24.00, image_file='food2.png'),
            MenuItem(name='CHICKEN PIZZA', description='Italian style pizza.', price=20.00, image_file='food1.png'),
            MenuItem(name='BEEF BURGER', description='Double beef burger.', price=15.00, image_file='food2.png'),
            MenuItem(name='VEGGIE SALAD', description='Healthy green salad.', price=10.00, image_file='food1.png'),
            MenuItem(name='PASTA BOLOGNESE', description='Classic beef pasta.', price=17.00, image_file='food2.png'),
            MenuItem(name='GRILLED CHICKEN', description='Roasted chicken breast.', price=22.00, image_file='food1.png'),
            MenuItem(name='FISH AND CHIPS', description='Crispy fried fish.', price=19.00, image_file='food2.png'),
            MenuItem(name='CLUB SANDWICH', description='Triple layer sandwich.', price=12.00, image_file='food1.png'),
            MenuItem(name='MUSHROOM SOUP', description='Creamy mushroom soup.', price=8.00, image_file='food2.png'),
            MenuItem(name='STEAK DINNER', description='Premium beef steak.', price=35.00, image_file='food1.png'),
            MenuItem(name='CHOCO DESSERT', description='Sweet chocolate cake.', price=9.00, image_file='food2.png')
        ]
        db.session.add_all(items)
        db.session.commit()

# --- المسارات (Routes) ---

@app.route('/')
def home():
    menu_items = MenuItem.query.all()
    return render_template('index.html', menu_items=menu_items)

@app.route('/menu')
def menu():
    menu_items = MenuItem.query.all()
    return render_template('menu.html', menu_items=menu_items)

@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    item = MenuItem.query.get_or_404(item_id)
    if 'cart' not in session:
        session['cart'] = []
    
    # تحديث السلة وحفظ التغييرات
    cart = session['cart']
    cart.append({'id': item.id, 'name': item.name, 'price': item.price, 'image': item.image_file})
    session['cart'] = cart
    session.modified = True 
    
    flash(f'Added {item.name} to bag!', 'success')
    return redirect(url_for('menu'))

@app.route('/cart')
def view_cart():
    # هذا هو الـ endpoint المسؤول عن عرض الشنطة
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', items=cart, total=total)

if __name__ == '__main__':
    app.run(debug=True)