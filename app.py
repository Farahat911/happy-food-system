import os # مكتبة بنستخدمها عشان نتعامل مع الملفات والفولدرات على الجهاز
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename # مكتبة بنستخدمها لتأمين اسم الملف اللي العميل بيرفعه

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.secret_key = 'happy_food_secret_key_123' 

# -------------------------------------------------------------
# نوت ليا: بحدد المسار اللي هحفظ فيه صور التحويلات وأنواع الملفات المسموح بيها
# -------------------------------------------------------------
UPLOAD_FOLDER = 'static/uploads' # الفولدر اللي لسه عاملينه
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # الأنواع المسموح برفعها
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# -------------------------------------------------------------
# نوت ليا: دالة مساعدة بتتأكد إن الملف اللي العميل رفعه امتداده مسموح بيه
# -------------------------------------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# -------------------------------------------------------------
# نوت ليا: عدلت جدول الأوردرات عشان أخزن طريقة الدفع (payment_method)
# وصورة التحويل (transaction_screenshot) ورقم اللي حول منه (sender_phone)
# -------------------------------------------------------------
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending') # pending يعنى لسه ماتأكدش
    
    payment_method = db.Column(db.String(50), nullable=False, default='COD') # طريقة الدفع (COD أو Online)
    transaction_screenshot = db.Column(db.String(100), nullable=True) # اسم ملف الصورة (اختياري لو الدفع كاش)
    sender_phone_number = db.Column(db.String(20), nullable=True) # رقم الموبايل اللي حول منه (اختياري)

class PaidOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_order_id = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_details = db.Column(db.Text, nullable=False)
    
    # ضيفت الحقول دي هنا كمان للأرشيف
    payment_method = db.Column(db.String(50), nullable=True)
    transaction_screenshot = db.Column(db.String(100), nullable=True)
    sender_phone_number = db.Column(db.String(20), nullable=True)

with app.app_context():
    db.create_all()
    # تأكد من وجود ملفات MenuItem مبدئية لو الداتا بيز فاضية
    if not MenuItem.query.first():
        item1 = MenuItem(name='LASAL CHEESE', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=18.00, image_file='food1.png')
        item2 = MenuItem(name='JUMBO CRAB SHRIMP', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=24.00, image_file='food2.png')
        item3 = MenuItem(name='KOKTAIL JUCIE', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=12.00, image_file='food3.png')
        item4 = MenuItem(name='CAPO STEAK', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=60.00, image_file='food4.png')
        item5 = MenuItem(name='ORGANIC FRUIT SALAD', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=8.00, image_file='food5.png')
        item6 = MenuItem(name='CHEESE PIZZA', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=18.00, image_file='food6.png')
        item7 = MenuItem(name='KOFTA MEAT', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=40.00, image_file='food7.jpeg')
        item8 = MenuItem(name='SPANISH PIES', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=14.00, image_file='food8.jpeg')
        item9 = MenuItem(name='CHEESE TOST', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=6.00, image_file='food9.jpeg')
        item10 = MenuItem(name='FRUIT SALAD', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=14.00, image_file='food10.jpeg')
        item11 = MenuItem(name='CHICKEN SHAWARMA', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=20.00, image_file='food11.jpeg')
        item12 = MenuItem(name='MEGA CHEESE PIZZA', description='Lorem ipsum dolor sit amet consectetur adipisicing elit.', price=30.00, image_file='food12.jpeg')
        db.session.add_all([item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11, item12])
        db.session.commit()

# =========================================================
# مسارات العميل (Front-end Routes)
# =========================================================

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
# نظام السلة (Cart System)
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
    if 'cart' in session:
        session['cart'].append(item_id)
        session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/remove_all/<int:item_id>')
def remove_all(item_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item != item_id]
        session.modified = True
        flash('Item removed completely!', 'success')
    return redirect(url_for('view_cart'))

# -------------------------------------------------------------
# نوت ليا: عدلت دالة الـ checkout بالكامل عشان تستقبل طريقة الدفع وصورة التحويل
# -------------------------------------------------------------
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your bag is empty! Please add items before checkout.', 'error')
        return redirect(url_for('menu'))

    # بجيب الإجمالي عشان أعرضه للعميل في رسالة الدفع الأون لاين
    cart_item_ids = session.get('cart', [])
    item_counts = {}
    total_price = 0
    for item_id in cart_item_ids:
        item_counts[item_id] = item_counts.get(item_id, 0) + 1
    
    order_details_list = []
    for item_id, quantity in item_counts.items():
        item = MenuItem.query.get(item_id)
        if item:
            total_price += item.price * quantity
            order_details_list.append(f"{quantity}x {item.name}")
    order_details = " | ".join(order_details_list)

    if request.method == 'POST':
        # بجيب بيانات العميل الأساسية
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # بجيب طريقة الدفع
        payment_method = request.form.get('payment_method')
        
        screenshot_filename = None
        sender_phone_number = None

        # لو اختار دفع أون لاين، لازم نستقبل الصورة ورقم اللي حول منه
        if payment_method == 'online':
            # بجيب رقم اللي حول منه
            sender_phone_number = request.form.get('sender_phone_number')
            
            # بتأكد إن الملف اتبعت في الفورم
            if 'transaction_screenshot' not in request.files:
                flash('Please upload your transfer screenshot.', 'error')
                return redirect(request.url)
            
            file = request.files['transaction_screenshot']
            
            # بتأكد إن العميل اختار ملف، وإن امتداده مسموح بيه
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename) # بتأمن اسم الملف
                # بضيف رقم عشوائي لاسم الملف عشان ميتكررش
                unique_filename = f"transfer_{phone}_{filename}"
                # بحفظ الملف في الفولدر اللي عاملينه
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                screenshot_filename = unique_filename
            else:
                flash('Invalid image format. Please use (png, jpg, jpeg, gif).', 'error')
                return redirect(request.url)

        # بسجل الأوردر الجديد بالبيانات الجديدة
        new_order = Order(
            customer_name=name,
            phone=phone,
            address=address,
            total_price=total_price,
            order_details=order_details,
            payment_method=payment_method,
            transaction_screenshot=screenshot_filename,
            sender_phone_number=sender_phone_number
        )
        
        db.session.add(new_order)
        db.session.commit()

        # بفضي السلة بعد تأكيد الأوردر
        session.pop('cart', None)
        
        # بغير رسالة التأكيد بناءً على طريقة الدفع
        if payment_method == 'online':
            flash('Order placed successfully! We will verify your transfer and deliver it soon.', 'success')
        else:
            flash('Order placed successfully! We will deliver it to you soon.', 'success')
            
        return redirect(url_for('home'))

    return render_template('checkout.html', total_price=total_price)

# =========================================================
# نظام الإدارة (Admin Panel Routes)
# =========================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'Admin' and password == 'Admin123':
            session['admin_logged_in'] = True
            flash('Welcome back, Boss!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        flash('Please login first to access the dashboard.', 'error')
        return redirect(url_for('login'))

    pending_orders = Order.query.all()
    paid_orders = PaidOrder.query.all()
    menu_items = MenuItem.query.all()
    
    # السطر ده عشان نسحب كل رسائل العملاء من الداتابيز
    contact_messages = Contact.query.all() 
    
    return render_template('admin.html', 
                           pending_orders=pending_orders, 
                           paid_orders=paid_orders, 
                           menu_items=menu_items,
                           contact_messages=contact_messages)

# دالة جديدة عشان تمسح الرسالة بعد ما تقرأها
@app.route('/delete_message/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    msg = Contact.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/add_item', methods=['POST'])
def add_item():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    name = request.form.get('name')
    description = request.form.get('description')
    price = float(request.form.get('price'))
    
    file = request.files.get('image_file')
    image_filename = 'food1.png'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"menu_{filename}"
        file.save(os.path.join('static/img', unique_filename))
        image_filename = unique_filename
    elif file:
        flash('Invalid image format.', 'error')
        return redirect(url_for('admin'))

    new_item = MenuItem(name=name, description=description, price=price, image_file=image_filename)
    db.session.add(new_item)
    db.session.commit()

    flash('New item added to the menu successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/edit_price/<int:item_id>', methods=['POST'])
def edit_price(item_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    item = MenuItem.query.get_or_404(item_id)
    new_price = float(request.form.get('new_price'))
    item.price = new_price
    db.session.commit()

    flash('Item price updated successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/complete_order/<int:order_id>', methods=['POST'])
def complete_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    order = Order.query.get_or_404(order_id)
    
    # بنقل كل البيانات الجديدة للأرشيف
    paid_order = PaidOrder(
        original_order_id=order.id,
        customer_name=order.customer_name,
        phone=order.phone,
        address=order.address,
        total_price=order.total_price,
        order_details=order.order_details,
        payment_method=order.payment_method,
        transaction_screenshot=order.transaction_screenshot,
        sender_phone_number=order.sender_phone_number
    )
    
    db.session.add(paid_order)
    db.session.delete(order)
    db.session.commit()
    
    flash('Order marked as paid and moved to archive!', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    
    flash('Order canceled and deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    flash('Item deleted from menu successfully!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)