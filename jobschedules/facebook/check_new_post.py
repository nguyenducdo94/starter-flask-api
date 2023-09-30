from apscheduler.schedulers.background import BackgroundScheduler
import requests

class FacebookCheckNewPostScheduler():
    def __init__(self, dynamodb_manager):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.dynamodb_manager = dynamodb_manager

    def addJob(self, schedule_id, interval):
        self.scheduler.add_job(lambda: self.check_new_post(schedule_id), 'interval', seconds=int(interval), id=schedule_id)

    def removeJob(self, schedule_id):
        self.scheduler.remove_job(schedule_id)

    def check_new_post(self, schedule_id):

        bot_token ='5368023757:AAGUecLZVcbvyJYHfHzmBHn9JY88poBfCeU'
        bot_chatID = '1659449821'
        send_text ='https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' \
            + bot_chatID + '&parse_mode=MarkdownV2&text=' + 'SEND TEST'
        response = requests.get(send_text)
        # print(response.json)

        # telegram_bot_sendtext('SEND TEST')
