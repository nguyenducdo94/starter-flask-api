from flask import Flask, jsonify, request, render_template
import os
import platform
import requests


app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

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

    
    return(f'Hệ điều hành: {system_info}')

@app.route('/crawl')
def scrape_and_render():
    # Gửi yêu cầu đến trang web
    url = request.args.get("link")  # Thay đổi URL thành trang web bạn muốn gửi yêu cầu đến

    response = requests.get(url)

    if response.status_code == 200:
        # Lưu nội dung HTML vào một tệp
        with open('response.html', 'w', encoding='utf-8') as html_file:
            html_file.write(response.text)

        # Trả về nội dung HTML dưới dạng template
        return render_template('response.html')
    else:
        return "Không thể tải trang web."