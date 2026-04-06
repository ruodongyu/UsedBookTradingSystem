from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

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
        if password != confirm_password:
            return '两次输入的密码不一致，请重新输入'
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return '用户名已存在，请重新注册。'

        # 创建新用户并存入数据库
        new_user = User(username=username, password=password)
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
        if user and user.password == password:  # 暂用明文对比，以后改为哈希
            session['user_id'] = user.id
            session['username'] = user.username
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

if __name__ == '__main__':
    app.run(debug=True)