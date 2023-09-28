import signal
import subprocess
import sys
import threading
import time
from flask import Flask, jsonify, redirect, request, render_template, url_for
import os
import platform
import psutil
import pymongo
import requests
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from bson import ObjectId
from models import User
from config import app, login_manager, users_collection, facebook_account_manager_collection, fb_check_new_post_scheduler_collection

#----------------------------------PAGE APIs--------------------------------------#
@app.route('/')
@login_required
def homepage():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Implement your authentication logic here (e.g., check_credentials function)
        if check_credentials(username, password):
            return redirect(url_for('homepage'))  # Redirect to the homepage after successful login

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

def check_credentials(username, password):
    # Retrieve user data from MongoDB based on the username
    user_data = users_collection.find_one({"username": username})

    if user_data and user_data["password"] == password:
        user = User(user_data['_id'], user_data['username'])
        login_user(user)
        return redirect(url_for('homepage'))
    
    return False  # Authentication failed

@login_manager.user_loader
def load_user(user_id):
    user_data = user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        user = User(user_id, user_data['username'])
        return user
    else:
        return None

@app.route('/protected')
@login_required
def protected():
    return "This page is protected. You can only access it if you are logged in."

@app.route('/profile')
@login_required
def profile():
    # Retrieve user data from MongoDB based on the username
    user_data = users_collection.find_one({"_id": ObjectId(current_user.id)})
    print(current_user.id)
    print(user_data)
    return f"Hello, {user_data['username']}! This is your profile page."


@app.route('/facebook')
@login_required
def facebookpage():
    return render_template('facebook/facebook.html')

#----------------------------------FACEBOOK ACCOUNT MANAGER APIs--------------------------------------#
@app.route('/facebook/accountmanager')
@login_required
def facebook_account_manager():
    current_user_id = current_user.id

    accounts = list(facebook_account_manager_collection.find({'manager_id': current_user_id}))

    return render_template('facebook/account_manager.html', accounts=accounts)


@app.route('/facebook/add_account', methods=['POST'])
def facebook_add_account():
    try:
        # Nhận dữ liệu tài khoản từ yêu cầu POST
        data = request.json

        current_user_id = current_user.id

        # Tạo một bản ghi tài khoản mới
        new_account = {
            'name': data.get('name'),
            'token': data.get('token'),
            'cookie': data.get('cookie'),
            'manager_id': current_user_id
        }

        # Lưu thông tin tài khoản vào cơ sở dữ liệu
        facebook_account_manager_collection.insert_one(new_account)

        # Trả về phản hồi thành công
        response = {
            'success': True,
            'message': 'Tài khoản đã được thêm thành công.'
        }
        return jsonify(response), 200
    
    except Exception as e:
        # Xử lý lỗi (nếu có)
        response = {
            'success': False,
            'message': 'Đã xảy ra lỗi khi thêm tài khoản.',
            'error': str(e)
        }
        return jsonify(response), 500
    

@app.route('/facebook/update_account', methods=['PUT'])
def facebook_update_account():
    try:
        data = request.json
        # Xác định điều kiện để tìm tài khoản cần cập nhật
        query = {'_id': ObjectId(data.get('id'))}

        # Xác định thông tin cập nhật
        update_data = {
            '$set': {
                'name': data.get('name'),
                'token': data.get('token'),
                'cookie': data.get('cookie')
            }
        }

        # Thực hiện cập nhật tài khoản trong cơ sở dữ liệu
        result = facebook_account_manager_collection.update_one(query, update_data)

        if result.modified_count > 0:
            # Cập nhật thành công
            response = {
                'success': True,
                'message': 'Tài khoản đã được cập nhật thành công.'
            }
            return jsonify(response), 200
        else:
            # Không tìm thấy hoặc không có sự thay đổi
            response = {
                'success': False,
                'message': 'Không tìm thấy hoặc không có sự thay đổi trong tài khoản.'
            }
            return jsonify(response), 404

    except Exception as e:
        # Xử lý lỗi (nếu có)
        response = {
            'success': False,
            'message': 'Đã xảy ra lỗi khi cập nhật tài khoản.',
            'error': str(e)
        }
        return jsonify(response), 500


@app.route('/facebook/delete_account/<account_id>', methods=['DELETE'])
def facebook_delete_account(account_id):
    try:
        print(account_id)
        result = facebook_account_manager_collection.delete_one({'_id': ObjectId(account_id)})

        if result.deleted_count > 0:
            response = {
                'success': True,
                'message': 'Tài khoản đã được xóa thành công.'
            }
            return jsonify(response), 200
        else:
            response = {
                'success': False,
                'message': 'Không tìm thấy tài khoản có ID này.'
            }
            return jsonify(response), 404
            
    except Exception as e:
        response = {
            'success': False,
            'message': 'Đã xảy ra lỗi khi xóa tài khoản.',
            'error': str(e)
        }
        return jsonify(response), 500

@app.route('/facebook/getcookie')
@login_required
def facebook_get_cookie():
    return render_template('facebook/getcookie.html')


@app.route('/facebook/get_owner_facebook_accounts')
@login_required
def facebook_get_owner_facebook_accounts():
    current_user_id = current_user.id
    accounts = list(facebook_account_manager_collection.find({'manager_id': current_user_id}))
    print(accounts)
    for account in accounts:
        account["_id"] = str(account["_id"])
    return jsonify(accounts)

#----------------------------------FACEBOOK CHECK NEW POST APIs--------------------------------------#
@app.route('/facebook/checknewpost')
@login_required
def facebook_check_new_post():
    current_user_id = current_user.id

    schedules = list(fb_check_new_post_scheduler_collection.find({'fb_account_id': current_user_id}))

    return render_template('facebook/check_new_post.html', schedules=schedules)


#----------------------------------ANOTHER APIs--------------------------------------#
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