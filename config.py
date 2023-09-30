from flask import Flask
from flask_login import LoginManager
import boto3
from boto3.dynamodb.conditions import Attr

login_manager = LoginManager()
login_manager.login_view = 'login'

class DynamoDBManager:
    def __init__(self, app):
        self.app = app
        self.app.secret_key = 'facebook_tool_secret_key'
        login_manager.init_app(self.app)

        # DynamoDB Configuration
        boto3.setup_default_session(region_name='ap-southeast-1')
        # self.session = boto3.Session(
        #     aws_access_key_id='ASIA2POOKCXIF3ZYAFK5',
        #     aws_secret_access_key='Kw4xD46NxaoBBZYjzZ1Dhwu08I1TZ4qr5Rhu1Oik',
        #     aws_session_token='IQoJb3JpZ2luX2VjENT//////////wEaCmFwLXNvdXRoLTEiRzBFAiAe5oqkxEl4qbRnUtXrBg+GeyMCU2s3yDJaoXOt7pDWZwIhANUBdFZkGEs/+5SBPTqxUEh2LnLJGXotOzdn9lgPLn4WKrcCCM3//////////wEQABoMNzIwMzc2NTY3MjQ4IgziEKesbRGajo6PKU8qiwJTyIZWkPE37X974cJpzBS5X9wuqyGuPwmfI3uZMNjizDVNH8lfZDPe+SNLLp34DPS4kwecGe0SqB68OXJa6Tzf5/lmEJ35Awm8Jil4AlZwJkhRLo2ZvuEXeiCOiJlM01JuhZB8i26HVFXgYNkNg4FXg+EaHKfmA7HB3KBxBI+UwiHRyxP88xfKUYf9dZxScmVOm0qZG4XHcCP2WvoJehMDEBxHi/T31NY/sUmTyijQq03pdUVRpv+wVrRaVF+Sgb0B/EapwG0qlPDDo90GFDigzDKT7D/ycQdZsY7By7DINvBu9StkmaqfkSM/XTQNAixH83LhKvV/a9k920RDXLQc7ElZUORTbIeXfkMwgLfeqAY6nQHfEtgilr0s/76hIXGwyk5K4BI0H0ujijyyZ1qPb3aYdQR0Ag7oZtDGOnks0srH9A03O4yKUsVbfhwUm7C9lz9TscGVVGIkmd1MoSUI7FHbwMYkBWgs0VUwTJY1HmOHHSY+j6fTkIoMAyZflWl40jLQMfsoLi9PD4OEwy+ptk6ytXMdwksWqIDXk3ckId/cdVarEo5pQOtIYsF6tfpW',
        #     region_name='ap-southeast-1'
        # )
        # self.dynamodb = self.session.resource('dynamodb')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('yellow-springbok-fezCyclicDB')

    def find_user(self, field, value):    
        response = self.table.query(
            KeyConditionExpression='pk = :val1',
            ExpressionAttributeValues={
                ':val1': 'users',
            },
            FilterExpression=Attr(field).eq(value)
        )
        if response:
            return response['Items'][0]
        return None
    
    def load_user(self, user_id):
        response = self.table.query(
            KeyConditionExpression='pk = :val1',
            ExpressionAttributeValues={
                ':val1': 'users',
            },
        )
        for item in response["Items"]:
            if item["sk"] == user_id:
                return item
        return None
    
    def get_owner_facebook_accounts(self, user_id):
        response = self.table.query(
            KeyConditionExpression='pk = :val1',
            ExpressionAttributeValues={
                ':val1': 'facebook_account_manager',
            },
            FilterExpression=Attr('manager_id').eq(user_id)
        )
        if response['Items']:
            return response['Items']
        return None
    
    def add_facebook_account(self, new_account):
        response = self.table.put_item(Item=new_account)

        httpStatusCode = response['ResponseMetadata']['HTTPStatusCode']

        if httpStatusCode == 200:
            return "success"
        else:
            return httpStatusCode
        
    def update_facebook_account(self, data):
        key = {
            'pk': 'facebook_account_manager',
            'sk': data.get('id')
        }
        # Define the updates you want to apply
        update_expression = "SET account_name = :val1, account_token = :val2, account_cookie = :val3"
        expression_attribute_values = {
            ':val1': data.get('account_name'),
            ':val2': data.get('account_token'),
            ':val3': data.get('account_cookie')
        }

        response = self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            # ReturnValues="UPDATED_NEW"  # If you want to get the updated attributes in the response
        )

        httpStatusCode = response['ResponseMetadata']['HTTPStatusCode']

        if httpStatusCode == 200:
            return "success"
        else:
            return httpStatusCode
        
    def delete_facebook_account(self, account_id):
        key = {
            'pk': 'facebook_account_manager',
            'sk': account_id
        }

        response = self.table.delete_item(Key=key)

        httpStatusCode = response['ResponseMetadata']['HTTPStatusCode']

        if httpStatusCode == 200:
            return "success"
        else:
            return httpStatusCode
        
    def get_owner_check_new_post_schedules(self, user_id):
        response_schedule = self.table.query(
            KeyConditionExpression='pk = :val1',
            ExpressionAttributeValues={
                ':val1': 'fb_check_new_post_scheduler',
            },
            FilterExpression=Attr('manager_id').eq(user_id)
        )

        response_fb_account = self.table.query(
            KeyConditionExpression='pk = :val1',
            ExpressionAttributeValues={
                ':val1': 'facebook_account_manager',
            },
            FilterExpression=Attr('manager_id').eq(user_id)
        )

        # Tạo một từ điển (dictionary) để ánh xạ các mục trong list1 theo 'id'
        mapping_dict = {item['sk']: item for item in response_fb_account['Items']}

        # Kết hợp danh sách list2 dựa trên 'id' và thêm các thông tin từ list1
        combined_list = []

        for item in response_schedule['Items']:
            item_id = item['account_id']

            if item_id in mapping_dict:
                combined_item = {
                    **item, 
                    'account_name': mapping_dict[item_id]['account_name'],
                    'account_token': mapping_dict[item_id]['account_token'], 
                    'account_cookie': mapping_dict[item_id]['account_cookie'],
                }
                combined_list.append(combined_item)
            else:
                combined_item = {
                    **item, 
                    'account_name': '',
                    'account_token': '',
                    'account_cookie': '',
                }
                combined_list.append(combined_item)

        if len(combined_list) > 0:
            return combined_list
        return None
    
    def find_facebook_account(self, manager_id, account_id):
        response = self.table.query(
            KeyConditionExpression='pk = :val1 AND sk = :val2',
            ExpressionAttributeValues={
                ':val1': 'facebook_account_manager',
                ':val2': account_id,
            },
            FilterExpression=Attr('manager_id').eq(manager_id)
        )
        if response['Items']:
            return response['Items'][0]
        return None
    
    def add_check_new_post_schedule(self, new_schedule):
        response = self.table.put_item(Item=new_schedule)

        httpStatusCode = response['ResponseMetadata']['HTTPStatusCode']

        if httpStatusCode == 200:
            return "success"
        else:
            return httpStatusCode
        
    def delete_check_new_post_schedule(self, schedule_id):
        key = {
            'pk': 'fb_check_new_post_scheduler',
            'sk': schedule_id
        }

        response = self.table.delete_item(Key=key)

        httpStatusCode = response['ResponseMetadata']['HTTPStatusCode']

        if httpStatusCode == 200:
            return "success"
        else:
            return httpStatusCode

    def toggle_check_new_post_schedule(self, data):
        key = {
            'pk': 'fb_check_new_post_scheduler',
            'sk': data.get('scheduleId')
        }
        # Define the updates you want to apply
        update_expression = "SET active = :val1"
        expression_attribute_values = {
            ':val1': data.get('newStatus')
        }

        response = self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            # ReturnValues="UPDATED_NEW"  # If you want to get the updated attributes in the response
        )

        httpStatusCode = response['ResponseMetadata']['HTTPStatusCode']

        if httpStatusCode == 200:
            return "success"
        else:
            return httpStatusCode

    def find_check_new_post_schedule(self, schedule_id):
        response = self.table.query(
            KeyConditionExpression='pk = :val1 AND sk = :val2',
            ExpressionAttributeValues={
                ':val1': 'fb_check_new_post_scheduler',
                ':val2': schedule_id,
            },
        )
        if response['Items']:
            return response['Items'][0]
        return None