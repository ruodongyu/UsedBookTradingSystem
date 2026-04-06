# 📚 二手书交易平台
一个基于 **Flask** 的轻量级二手书交易 Web 应用，支持用户注册、登录、书籍发布、搜索、删除（仅发布者）以及数据可视化分析。

## ✨ 功能特点

- 用户注册（含密码确认校验）
- 用户登录（Session 管理登录状态）
- 发布二手书（仅登录用户可发布）
- 首页展示所有在售书籍（含发布者信息）
- 删除书籍（仅发布者本人可删除，前端+后端双重权限控制）
- 搜索书籍（按书名或作者模糊匹配）
- 数据分析（书籍数量、价格统计、价格分布直方图）
- 退出登录
- 响应式页面设计（简单 CSS 美化）
## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | Flask |
| 数据库 | SQLite + Flask-SQLAlchemy |
| 模板引擎 | Jinja2 |
| 前端 | HTML, CSS |
| 开发环境 | Python 3.11 |

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ruodongyu/UsedBookTradingSystem.git
cd UsedBookTradingSystem
```

### 2. 创建虚拟环境（可选但推荐）

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. 安装依赖

```bash
pip install flask flask-sqlalchemy
```

### 4. 初始化数据库

```python
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 5. 运行应用

```bash
python app.py
```

然后访问 `http://127.0.0.1:5000`

## 📁 项目结构
```
UsedBookTradingSystem/
├── app.py
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── publish.html
│   ├── search_results.html
│   └── analysis.html
├── instance/
├── static/
└── README.md
```
## 👥 权限说明

- 只有**登录用户**才能发布书籍。
- 只有**书籍发布者**才能删除自己的书籍。
- 搜索功能仅限登录用户（可按需开放）。
  


## 📝 后续计划

- 增加编辑书籍功能
- 增加“我的发布”页面
- 增加分页功能
- 密码哈希加密存储
- 部署到云服务器

## 🙏 致谢

本项目为个人学习 Flask 框架的练习作品，参考了 Flask 官方文档及相关教程。

## 📄 许可证

MIT License
