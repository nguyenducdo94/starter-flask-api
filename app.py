import signal
import subprocess
import sys
import time
from flask import Flask, jsonify, request, render_template
import os
import platform
import psutil
import requests


app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/facebook')
def facebookpage():
    return render_template('facebook.html')

@app.route('/facebook/getcookie')
def getcookie():
    return render_template('getcookie.html')

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

@app.route('/check_ip')
def check_ip():
    res = requests.get("https://api64.ipify.org?format=json")
    return res.content
    
@app.route('/crawl')
def scrape_and_render():
    # url = request.args.get("link")

    # Create a string containing the cookie data
    cookie_string = "wd=1920x931; datr=Y-D-ZIKxQXk1OXOM3LSKhaRq; sb=6bj_ZJ2mhN1QcYWnM8yoEae4; c_user=100002244977876; xs=27%3AY4h3YKNAhuDmlA%3A2%3A1694531343%3A-1%3A6381; fr=09HoYKJd0rVC7X3Vv.AWUxJv5WuccIKmyC3ScY9E956tQ.Bk_7jp.Fs.AAA.0.0.BlAH8S.AWVebDTlM8Y; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1694531352842%2C%22v%22%3A1%7D; useragent=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE"
    # You can add more cookies as needed

    # Split the cookie string into individual cookies
    cookie_list = cookie_string.split('; ')

    # Create a dictionary to store the cookies
    cookies = {}

    # Convert the list of cookies into a dictionary
    for cookie in cookie_list:
        key, value = cookie.split('=', 1)  # Split at the first '=' character
        cookies[key] = value

    # Make the request with the cookies
    response = requests.get("https://facebook.com", cookies=cookies)

    # Gửi yêu cầu đến trang web
    html_content = response.text
    
    # Return the HTML content
    return html_content

@app.route('/reset_app')
def reset_app():
    # Iterate through all running processes
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            print(process.info['name'])
            # Check if the process name matches the target
            if process.info['name'] == 'python':
                print(process.info['pid'])
                # Terminate the process
                pid = process.info['pid']
                psutil.Process(pid).terminate()
                print(f"Terminated {'python'} with PID {pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


# if __name__ == '__main__':
#     app.run()