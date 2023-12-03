from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__, static_folder='static')


# 连接到 MySQL 数据库
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="abcd1234",
    database="weiqi"
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    name = request.form['name'].strip()  # 获取前端输入的姓名

    # 执行数据库查询

    if not name.strip():  # 如果輸入是空白字串
        # 返回一個空列表
        return render_template('index.html', data=[], search_name=name)

    # 执行数据库模糊查询
    cursor = db_connection.cursor(dictionary=True)
    query = "SELECT * FROM your_table WHERE 姓名 LIKE %s"
    cursor.execute(query, ('%' + name + '%',))
    data = cursor.fetchall()
    cursor.close()

    # 返回查询结果到前端页面，直接传递 JSON 格式的数据
    return render_template('index.html', data=data, search_name=name)
# 新增段位統計的路由函數


@app.route('/dan')
def show_dan_statistics():
    # 在这里执行数据库查询，获取棋力统计数据
    cursor = db_connection.cursor()
    query = "SELECT 棋力, COUNT(*) AS count FROM your_table GROUP BY 棋力 ORDER BY 棋力"
    cursor.execute(query)
    statistics = cursor.fetchall()
    cursor.close()

    # 将查询结果传递给 dan.html 模板
    return render_template('dan.html', statistics=statistics)


@app.route('/kk')
def show_kk_statistics():
    cursor = db_connection.cursor()
    # 執行 SQL 查詢以獲取甲組到丁組的數據，調整你的查詢語句以符合你的資料表結構
    query = "SELECT 棋力, COUNT(*) AS count FROM your_table GROUP BY 棋力 ORDER BY 棋力"
    cursor.execute(query)
    statistics = cursor.fetchall()
    cursor.close()

    return render_template('kk.html', statistics=statistics)


if __name__ == '__main__':
    app.run(debug=True)
