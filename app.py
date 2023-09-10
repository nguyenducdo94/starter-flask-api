from flask import Flask, jsonify, request
from selenium import webdriver
import os
import platform


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello Aifone API'

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    try:
        url = request.args.get('url')  # Lấy URL từ tham số truy vấn

        print(f'gotta url {url}')
        # Khởi tạo trình duyệt Selenium
        driver = webdriver.Chrome('./chromedriver.exe')
        print(f'created driver')
        driver.get(url)  # Mở URL trong trình duyệt
        print(f'gotta to {url}')
        # Thực hiện các tác vụ Selenium ở đây
        # Ví dụ: Lấy tiêu đề của trang
        title = driver.title

        print("title")

        driver.quit()

        return jsonify({'title': title})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/checkos')
def check_os():
    # Kiểm tra hệ điều hành
    system_info = platform.system()
    print(f'Hệ điều hành: {system_info}')

    # Kiểm tra phiên bản hệ điều hành (chỉ áp dụng cho Linux)
    if system_info == 'Linux':
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('PRETTY_NAME='):
                        _, os_name = line.split('=', 1)
                        os_name = os_name.strip().strip('"')
                        print(f'Phiên bản hệ điều hành: {os_name}')
                        break
        except FileNotFoundError:
            pass
