from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from werkzeug.security import generate_password_hash, check_password_hash

plt.switch_backend('Agg')  # 避免在服务器端报错

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 建议改成一个随机字符串
# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(80))
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('books', lazy=True))
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        hashed_pw = generate_password_hash(password)
        if password != confirm_password:
            return '两次输入的密码不一致，请重新输入'
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return '用户名已存在，请重新注册。'

        # 创建新用户并存入数据库
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        return '注册成功！<a href="/login">去登录</a>'

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):  #哈希密码
            session['user_id'] = user.id
            return redirect(url_for('publish'))  # 跳转到发布书籍页面
        else:
            return '用户名或密码错误，请重新登录。'
    return render_template('login.html')


@app.route('/publish', methods=['GET', 'POST'])
def publish():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = float(request.form['price'])
        description = request.form['description']
        # 需要先定义 Book 模型，下面会给出
        new_book = Book(title=title, author=author, price=price, description=description, user_id=session['user_id'])
        db.session.add(new_book)
        db.session.commit()
        return '书籍发布成功！<a href="/">返回首页</a>'

    return render_template('publish.html')
@app.route('/about')
def about():
    return '这是一个基于python和flask框架的二手书交易平台，作者：若冬渝'


@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    # 检查用户是否登录
    if 'user_id' not in session:
        return redirect(url_for('login'))

    book = Book.query.get_or_404(book_id)
    # 检查是否是发布者
    if book.user_id != session['user_id']:
        return "你没有权限删除这本书。", 403

    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/analysis')
def analysis():
    books = Book.query.all()
    if not books:
        return "暂无书籍信息，无法分析"

    data = {
        'title': [book.title for book in books],
        'author': [book.author for book in books],
        'price': [book.price for book in books]
    }
    df = pd.DataFrame(data)
    avg_price = df['price'].mean().round(2)
    max_price = df['price'].max()
    min_price = df['price'].min()
    book_count = len(df)

    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']   # 用于 Windows
    plt.rcParams['axes.unicode_minus'] = False

    img = BytesIO()
    plt.figure(figsize=(8, 5))
    plt.hist(df['price'], bins=10, color='#4CAF50', edgecolor='black')
    plt.title('二手书价格分布')
    plt.xlabel('价格（元）')
    plt.ylabel('书籍数量')
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('analysis.html',
                           avg_price=avg_price,
                           max_price=max_price,
                           min_price=min_price,
                           book_count=book_count,
                           plot_url=plot_url)


@app.route('/search', methods=['POST'])
def search():

    if 'user_id' not in session:
        return redirect(url_for('login'))
    key_word = request.form.get('search_content', '').strip()

    if key_word:
        # 使用 or_ 进行书名或作者模糊匹配
        from sqlalchemy import or_
        books = Book.query.filter(
            or_(
                Book.title.contains(key_word),
                Book.author.contains(key_word)
            )
        ).all()
    else:
        books = []  # 关键词为空时返回空列表

    # 渲染搜索结果页面，传递 books 和关键词
    return render_template('search_results.html', books=books, keyword=key_word)

if __name__ == '__main__':
    app.run(debug=True)
