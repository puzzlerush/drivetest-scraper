import os
import datetime
from pymongo import MongoClient

from dtbot.drivetestbot import DriveTestBot

MONGODB_PWD = os.environ.get('MONGODB_PWD')
MONGODB_DBNAME = os.environ.get('MONGODB_DBNAME')

mongoDB = 'mongodb+srv://kevin:' + MONGODB_PWD + '@cluster0.nunf5.mongodb.net/' + MONGODB_DBNAME + '?retryWrites=true&w=majority'

client = MongoClient(mongoDB)

db = client.drivetest_openings

instances = db.instances
openings = db.openings

def create_instance():
    inst_details = {'time_updated': datetime.datetime.utcnow()}
    inst = instances.insert_one(inst_details)
    return inst

def create_opening(inst, location, date):
    op_details = {'instance': inst.inserted_id,
          'location': location,
          'date': date}
    op = openings.insert_one(op_details)
    return op

def get_available_dates():
    DT_EMAIL = os.environ.get('DT_EMAIL')
    DT_EMAIL_PWD = os.environ.get('DT_EMAIL_PWD')
    DT_LICENCE = os.environ.get('DT_LICENCE')
    DT_EXPIRY = os.environ.get('DT_EXPIRY')
    
    bot = DriveTestBot()
    bot.log_in(DT_EMAIL, DT_LICENCE, DT_EXPIRY)
    available_dates_all = bot.check_locations(["Kitchener", "Guelph", "Brantford", "Stratford"], 3)
    bot.pretty_print(available_dates_all)
    bot.notify(available_dates_all, DT_EMAIL, DT_EMAIL, DT_EMAIL_PWD)
    bot.stop()
    return available_dates_all

def insert_data(dictionary):
    instance = create_instance()
    
    for location, months in dictionary.items():
        for month, dates in months.items():
            for date in dates:
                date_string = f"{date} {month}"
                date_opening = datetime.datetime.strptime(date_string, '%d %B %Y')
                create_opening(instance, location, date_opening)

def job():
    all_openings = get_available_dates()
    insert_data(all_openings)

from apscheduler.schedulers.blocking import BlockingScheduler

SCRAPE_INTERVAL = int(os.environ.get('SCRAPE_INTERVAL'))

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', minutes=SCRAPE_INTERVAL)
    scheduler.start()
    job()

    
