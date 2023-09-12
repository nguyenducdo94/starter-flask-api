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
    url = request.args.get("link")

    content = requests.get(url)

    # Gửi yêu cầu đến trang web
    html_content = content.text
    
    # Return the HTML content
    return html_content