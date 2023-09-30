import subprocess
import threading
import time
from flask import Flask, jsonify, redirect, request, render_template, url_for
import platform
import psutil
import requests
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from config import DynamoDBManager,login_manager
import uuid
from jobschedules.facebook.check_new_post import FacebookCheckNewPostScheduler

app = Flask(__name__)
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
    user_data = dynamodb_manager.find_user("username", username)

    if user_data and user_data["password"] == password:
        user = User(user_data['sk'], user_data['username'])
        login_user(user)
        return redirect(url_for('homepage'))
    
    return False  # Authentication failed

@login_manager.user_loader
def load_user(user_id):
    user_data = dynamodb_manager.load_user(user_id)
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
    user_data = dynamodb_manager.find_user("sk", current_user.id)
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

    accounts = dynamodb_manager.get_owner_facebook_accounts(current_user_id)

    return render_template('facebook/account_manager.html', accounts=accounts)


@app.route('/facebook/accountmanager/add_account', methods=['POST'])
def facebook_add_account():
    # Nhận dữ liệu tài khoản từ yêu cầu POST
    data = request.json

    current_user_id = current_user.id
    unique_key = str(uuid.uuid4())

    new_account = {
        'pk': 'facebook_account_manager',
        'sk': unique_key,
        'account_name': data.get('account_name'),
        'account_token': data.get('account_token'),
        'account_cookie': data.get('account_cookie'),
        'manager_id': current_user_id
    }

    # Lưu thông tin tài khoản vào cơ sở dữ liệu
    result = dynamodb_manager.add_facebook_account(new_account)

    if result == 'success':
        response = {
            'success': True,
            'message': 'Tài khoản đã được thêm thành công.'
        }
        return jsonify(response), 200

    response = {
        'success': False,
        'message': 'Đã xảy ra lỗi khi thêm tài khoản.',
        'error': str(result)
    }
    return jsonify(response), 500
    

@app.route('/facebook/accountmanager/update_account', methods=['PUT'])
def facebook_update_account():
    data = request.json

    result = dynamodb_manager.update_facebook_account(data)

    if result == 'success':
        response = {
            'success': True,
            'message': 'Tài khoản đã được thêm thành công.'
        }
        return jsonify(response), 200

    response = {
        'success': False,
        'message': 'Đã xảy ra lỗi khi thêm tài khoản.',
        'error': str(result)
    }
    return jsonify(response), 500


@app.route('/facebook/accountmanager/delete_account/<account_id>', methods=['DELETE'])
def facebook_delete_account(account_id):
    result = dynamodb_manager.delete_facebook_account(account_id)

    if result == 'success':
        response = {
            'success': True,
            'message': 'Đã xoá tài khoản.'
        }
        return jsonify(response), 200

    response = {
        'success': False,
        'message': 'Đã xảy ra lỗi khi xoá tài khoản.',
        'error': str(result)
    }
    return jsonify(response), 500


@app.route('/facebook/accountmanager/get_owner_facebook_accounts')
@login_required
def facebook_get_owner_facebook_accounts():
    current_user_id = current_user.id
    accounts = dynamodb_manager.get_owner_facebook_accounts(current_user_id)

    return accounts

#----------------------------------FACEBOOK CHECK NEW POST APIs--------------------------------------#
@app.route('/facebook/checknewpost')
@login_required
def facebook_check_new_post():
    current_user_id = current_user.id
    schedules = dynamodb_manager.get_owner_check_new_post_schedules(current_user_id)

    return render_template('facebook/check_new_post.html', schedules=schedules)


@app.route('/facebook/checknewpost/add_schedule', methods=['POST'])
def facebook_add_check_new_post_schedule():
    # Nhận dữ liệu tài khoản từ yêu cầu POST
    data = request.json

    current_user_id = current_user.id

    unique_key = str(uuid.uuid4())

    new_schedule = {
        'pk': 'fb_check_new_post_scheduler',
        'sk': unique_key,
        'account_id': data.get('account_id'),
        'group_id': data.get('group_id'),
        'interval': data.get('interval'),
        'active': False,
        'manager_id': current_user_id
    }

    # Lưu thông tin tài khoản vào cơ sở dữ liệu
    result = dynamodb_manager.add_check_new_post_schedule(new_schedule)

    if result == 'success':
        response = {
            'success': True,
            'message': 'Tài khoản đã được thêm thành công.'
        }
        return jsonify(response), 200

    response = {
        'success': False,
        'message': 'Đã xảy ra lỗi khi thêm tài khoản.',
        'error': str(result)
    }
    return jsonify(response), 500


@app.route('/facebook/checknewpost/delete_schedule/<schedule_id>', methods=['DELETE'])
def facebook_delete_check_new_post_schedule(schedule_id):
    result = dynamodb_manager.delete_check_new_post_schedule(schedule_id)

    if result == 'success':
        response = {
            'success': True,
            'message': 'Đã xoá nhiệm vụ.'
        }
        return jsonify(response), 200

    response = {
        'success': False,
        'message': 'Đã xảy ra lỗi khi xoá nhiệm vụ.',
        'error': str(result)
    }
    return jsonify(response), 500


@app.route('/facebook/checknewpost/toggle_schedule', methods=['POST'])
def facebook_toggle_check_new_post_schedule():
    data = request.json
    result = dynamodb_manager.toggle_check_new_post_schedule(data)

    schedule_id = data.get('scheduleId')

    if data.get('newStatus') == True:
        interval = dynamodb_manager.find_check_new_post_schedule(schedule_id)['interval']
        fb_check_new_post_scheduler.addJob(schedule_id, interval)

    elif data.get('newStatus') == False:
        fb_check_new_post_scheduler.removeJob(data.get('scheduleId'))

    if result == 'success':
        response = {
            'success': True,
            'message': 'Đã đổi trạng thái.'
        }
        return jsonify(response), 200

    response = {
        'success': False,
        'message': 'Đã xảy ra lỗi.',
        'error': str(result)
    }
    return jsonify(response), 500

#----------------------------------FACEBOOK GET COOKIE APIs--------------------------------------#
@app.route('/facebook/getcookie')
@login_required
def facebook_get_cookie():
    return render_template('facebook/getcookie.html')


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

dynamodb_manager = DynamoDBManager(app)
fb_check_new_post_scheduler = FacebookCheckNewPostScheduler(dynamodb_manager)

if __name__ == '__main__':
    app.run()