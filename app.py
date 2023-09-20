import signal
import subprocess
import sys
import threading
import time
from flask import Flask, jsonify, redirect, request, render_template, url_for
import os
import platform
import psutil
import requests
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.secret_key = 'facebook_tool_secret_key'

login_manager = LoginManager()
login_manager.login_view = 'login'  # Set the view function for login
login_manager.init_app(app)

# Sample list of valid usernames and passwords (for demonstration purposes)
valid_users = {
    'user1': 'password1',
    'user2': 'password2',
    'user3': 'password3'
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check credentials (you can implement your own logic here)
        if check_credentials(request.form['username'], request.form['password']):
            user = User(id=request.form['username'])
            login_user(user)
            return redirect(url_for('homepage'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

def check_credentials(username, password):
    # Check if the provided username exists in the valid_users dictionary
    if username in valid_users:
        # Check if the provided password matches the stored password for the username
        if password == valid_users[username]:
            return True  # Authentication successful
    return False  # Authentication failed

@app.route('/protected')
@login_required
def protected():
    return "This page is protected. You can only access it if you are logged in."

@app.route('/profile')
@login_required
def profile():
    return f"Hello, {current_user.id}! This is your profile page."


@app.route('/facebook')
@login_required
def facebookpage():
    return render_template('facebook.html')

@app.route('/facebook/getcookie')
@login_required
def getcookie():
    return render_template('getcookie.html')

@app.route('/checkos')
@login_required
def check_os():
    # Get the operating system name
    os_name = platform.system()

    # Get the operating system version
    os_version = platform.uname()

    print(f"Operating System: {os_name}")
    print(f"Operating System Version: {os_version}")
    
    return(f'Operating System: {os_name} \n Operating System Version: {os_version}')

@app.route('/check_ip')
@login_required
def check_ip():
    res = requests.get("https://api64.ipify.org?format=json")
    return res.content
    
@app.route('/crawl')
@login_required
def crawl():
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
@login_required
def reset_app():
    def restart_server():
        subprocess.run(['./bin/start'])

    def kill_python_processes():
        time.sleep(1)
        # Tìm tất cả các tiến trình Python
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if "python" in process.info['name']:
                pid = process.info['pid']
                print(f"Killing Python process with PID {pid}")
                try:
                    psutil.Process(pid).terminate()
                except psutil.NoSuchProcess:
                    pass

    thread1 = threading.Thread(target=restart_server)
    thread2 = threading.Thread(target=kill_python_processes)
    # Bắt đầu chạy các luồng
    thread1.start()
    thread2.start()

    # Chờ cho đến khi cả hai luồng hoàn thành
    thread1.join()
    thread2.join()

    return 'Đã hoàn thành.'

if __name__ == '__main__':
    app.run()