from apscheduler.schedulers.background import BackgroundScheduler

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
        # self.dynamodb_manager.find_check_new_post_schedule
        print(schedule_id)
