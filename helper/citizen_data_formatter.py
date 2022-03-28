import csv
import random
import datetime
from bson import ObjectId
from random_object_id import generate
from faker import Faker
import json
fake = Faker()

# def object_id_from_int(n):
#     s = str(n)
#     s = '0' * (24 - len(s)) + s
#     return bson.ObjectId(s)

# def random_date(start, end):
#     """Generate a random datetime between `start` and `end`"""
#     return start + datetime.timedelta(
#         # Get a random amount of seconds between `start` and `end`
#         seconds=random.randint(0, int((end - start).total_seconds())),
#     )


citizen_rows = []
with open('neo4j_citizens.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            # read rows.
            citizen_rows.append(row)
            print(row)
            # line_count += 1

# print(citizen_rows)

with open('neo4j_citizens2.json', mode='w') as citizen_file:
    citizen_writer = csv.writer(
        citizen_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    citizen_writer.writerow(['_id', 'address', 'date_of_birth', 'full_name',
                             'gender', 'mobile', 'nric',
                             'health_historys', 'vaccination_historys'])

    for citizen_row in citizen_rows:
        vaccination_historys = []
        health_historys = []
        for i in range(random.randint(1, 3)):
            # random dose.
            dose_type = random.randint(0, 2)
            if dose_type == 0:
                dose_type = 'booster'
            elif dose_type == 1:
                dose_type = 'second_dose'
            else:
                dose_type = 'first_dose'

            # random status.
            status = random.randint(0, 2)
            if status == 0:
                status = 'healthy'
            elif status == 1:
                status = 'infected'
            else:
                status = 'healthy'

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

            vaccination_historys.append(
                {"dose_type": dose_type,
                 "updated_by_id": {"$oid": updated_by_id},
                 "updated_by_name": updated_by_name,
                 "vaccine_id": {"$oid": "619dc9d6b7f87307e3d920e4"},
                 "updated_at": {"$date": fake.date_time_between(start_date='-1y', end_date='now')
                                }
                 },
            )

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

            health_historys.append(
                {"status": status,
                 "updated_by_id": {"$oid": updated_by_id},
                 "updated_by_name": updated_by_name,
                 "updated_at": {"$date": fake.date_time_between(start_date='-1y', end_date='now')}}
            )

        citizen_row.append(health_historys)
        citizen_row.append(vaccination_historys)
        citizen_writer.writerow(
            citizen_row)
