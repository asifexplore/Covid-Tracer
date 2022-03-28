import csv
import random
import datetime
from bson import ObjectId
from random_object_id import generate
from faker import Faker
import json
import pymongo
import mongo_client

fake = Faker()


def random_dose():
    # random dose.
    dose_type = random.randint(0, 2)
    if dose_type == 0:
        dose_type = 'booster'
    elif dose_type == 1:
        dose_type = 'second_dose'
    else:
        dose_type = 'first_dose'
    return dose_type


def random_status():
    status = random.randint(0, 2)
    if status == 0:
        status = 'healthy'
    elif status == 1:
        status = 'infected'
    else:
        status = 'healthy'
    return status


def random_admin():
    updated_by = random.randint(0, 4)
    if updated_by == 0:
        updated_by_name = 'gerald'
        updated_by_id = '619dc5d1a3b5e8ecfe7b6c71'
    elif updated_by == 1:
        updated_by_name = 'adam'
        updated_by_id = '619dc5d1a3b5e8ecfe7b6c72'
    elif updated_by == 2:
        updated_by_name = 'asif'
        updated_by_id = '619dc5d1a3b5e8ecfe7b6c73'
    elif updated_by == 3:
        updated_by_name = 'yuhui'
        updated_by_id = '619dc5d1a3b5e8ecfe7b6c74'
    else:
        updated_by_name = 'jingyong'
        updated_by_id = '619dc5d1a3b5e8ecfe7b6c75'

    return updated_by_name, updated_by_id


def random_vaccine():
    updated_by = random.randint(0, 6)
    if updated_by == 0:
        updated_by_name = 'Sinovac'
        updated_by_id = '619dc9d6b7f87307e3d920e4'
    elif updated_by == 1:
        updated_by_name = 'Sinopharm'
        updated_by_id = '619dc9debd3aa4f669a85881'
    elif updated_by == 2:
        updated_by_name = 'Pfizer-BioNTech'
        updated_by_id = '619dc9e589a802c43625c438'
    elif updated_by == 3:
        updated_by_name = 'Moderna'
        updated_by_id = '619dc9ea1a2b949c4c4ec38e'
    elif updated_by == 4:
        updated_by_name = 'Oxford-AstraZeneca'
        updated_by_id = '619dc9ee50c4010c20f79539'
    elif updated_by == 5:
        updated_by_name = 'Sputnik V'
        updated_by_id = '619dc9f277c8999f3dedd2f9'
    else:
        updated_by_name = 'Novavax'
        updated_by_id = '61a0380720a6c042b96e9d03'

    return updated_by_name, updated_by_id


mongo_db_client = mongo_client.MongoDBClient(
    'mongodb+srv://admin:tJbJLK8YiYkDKYg@cluster0.96usv.mongodb.net/?retryWrites=true&w=majority')
mongo_db_client.connect_to_client()
mongo_db_client.connect_to_database('2103_covid_tracer')

citizens = mongo_db_client.db['citizens'].find()

for citizen in citizens:
    for i in range(random.randint(1, 3)):
        dose_type = random_dose()
        status = random_status()
        updated_by_health = random_admin()
        updated_by_vacc = random_admin()
        vaccine = random_vaccine()

        print(updated_by_health[1])

        count = 1
        result = mongo_db_client.db['citizens'].update_one(
            {'_id': citizen['_id']},
            {
                '$push': {
                    'health_historys': {'status': status,
                                        'updated_by_id': ObjectId(updated_by_health[1]),
                                        'updated_by_name': updated_by_health[0],
                                        'updated_at': fake.date_time_between(start_date='-1y', end_date='now')},
                    'vaccination_historys': {'dose_type': dose_type,
                                             'updated_by_id': ObjectId(updated_by_vacc[1]),
                                             'updated_by_name': updated_by_vacc[0],
                                             'vaccine_id': ObjectId(vaccine[1]),
                                             'updated_at': fake.date_time_between(start_date='-1y', end_date='now')}
                }
            }
        )
        print(count)
        count += 1
