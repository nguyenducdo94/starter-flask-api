from apscheduler.schedulers.background import BackgroundScheduler
from config import fb_check_new_post_scheduler_collection

interval_seconds = 60

fb_check_new_post_scheduler = BackgroundScheduler()

def getjob():
    allJobs = fb_check_new_post_scheduler_collection.find()

fb_check_new_post_scheduler.add_job(getjob, 'interval', seconds=interval_seconds)

fb_check_new_post_scheduler.start()