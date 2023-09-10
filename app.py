from flask import Flask, jsonify, request
from selenium import webdriver
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello Aifone API'

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    try:
        url = request.args.get('url')  # Lấy URL từ tham số truy vấn
        # Khởi tạo trình duyệt Selenium
        driver = webdriver.Chrome('./chromedriver')
        driver.get(url)  # Mở URL trong trình duyệt

        # Thực hiện các tác vụ Selenium ở đây
        # Ví dụ: Lấy tiêu đề của trang
        title = driver.title

        driver.quit()

        return jsonify({'title': title})
    except Exception as e:
        return jsonify({'error': str(e)})
