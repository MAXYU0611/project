import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import schedule
import time

# 设置Chrome浏览器的选项
options = Options()
options.chrome_executable_path = r"C:\Users\GoCafeUser\PycharmProjects\pythonProject\chrome-headless-shell.exe"
driver = webdriver.Chrome(options=options)
driver.maximize_window()

# 创建一个空数据列表，用于存储爬取的数据
data = []

# 遍历不同等级的页面
for level in range(-4, 8):
    url = f"https://www.weiqi.org.tw/RosterList.asp?RosterLevel={level}"
    driver.get(url)

    while True:
        # 获取页面的HTML内容
        html = driver.page_source

        # 使用Beautiful Soup解析HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 尝试找到包含个人信息的表格
        table = soup.find('table', width='98%')

        if table is None:
            print(f"No table found on level {level}")
            break  # 如果没有找到表格，退出当前页面的循环

        # 找到表格中的所有行
        rows = table.find_all('tr')

        # 遍历每一行，跳过标题行
        for row in rows[1:]:
            columns = row.find_all('td')
            name_element = columns[1].find('font', color='blue')
            if name_element:
                name = name_element.get_text(strip=True)
                gender = "Male"  # 根据颜色赋予 "Male" 值
            else:
                name_element = columns[1].find('font', color='red')
                if name_element:
                    name = name_element.get_text(strip=True)
                    gender = "Female"  # 根据颜色赋予 "Female" 值
                else:
                    name = "N/A"
                    gender = "N/A"

            birth_year = columns[2].get_text(strip=True)
            rank = columns[3].get_text(strip=True)
            print(f"{name:<8} {birth_year:<8} {rank} {gender}")
            # 添加数据到数据列表
            data.append([name, birth_year, rank, gender])

        try:
            # 模拟点击下一页链接
            next_page_links = driver.find_elements(By.LINK_TEXT, "下一頁")
            if next_page_links:
                next_page_links[0].click()
            else:
                print("未找到下一页链接")
                break
        except NoSuchElementException:
            # 如果没有找到下一页链接，说明已经到达最后一页，退出循环
            break

# 创建一个 pandas 数据框
df = pd.DataFrame(data, columns=["姓名", "出生年", "棋力", "性別"])

# 连接到 MySQL 数据库
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="abcd1234",
    database="weiqi"
)

# 创建一个游标对象
cursor = db_connection.cursor()

# 创建一个表（如果尚未存在）
create_table_query = """
CREATE TABLE IF NOT EXISTS your_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    姓名 VARCHAR(255),
    出生年 INT,
    棋力 VARCHAR(255),
    性別 VARCHAR(255)
)
"""

cursor.execute(create_table_query)

# 插入数据
insert_query = "INSERT INTO your_table (姓名, 出生年, 棋力, 性別) VALUES (%s, %s, %s, %s)"

for row in data:
    if row[1] == '':
        row[1] = None  # 或者设置为默认值
    cursor.execute(insert_query, row)

# 提交更改
db_connection.commit()

# 关闭游标和数据库连接
cursor.close()
db_connection.close()

# 关闭浏览器
driver.quit()

schedule.every(7).days.do(scrape_and_update)

# 開始排程
while True:
    schedule.run_pending()
    time.sleep(1)