'''
This module contains all routes.
@Author: Team 22 ICT2103 2021
'''
import json
import random
import functools
import mongo_client
import neo4j_client
import hashlib
import pymongo

from math import floor, ceil
from constants import *
from helper import *
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from bson.json_util import dumps, default

# Init Flask and secret key.
app = Flask(__name__)
app.secret_key = '2103'


def parse_json(data):
    return json.loads(dumps(data))


def login_required(func):
    ''' Username in session is required for certain routes.
    Args:
        func (Flask func): put this function above a route function to work.

    Returns:
        function: return function if username is not in session.
    '''
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    return secure_function


@app.route('/', methods=['GET', 'POST'])
def index():
    ''' / Route. Home screen of the webpage.

    Returns:
        render_template: HTML webpage.
    '''
    # Get unit from arguments.
    if request.args.get('unit') is None:
        unit = WEEK_UNIT
    else:
        unit = request.args.get('unit')

    # Get day in unit. eg. 1 week have 7 days.
    if unit == DAY_UNIT:
        days_in_unit = DAY_IN_DAY
    elif unit == WEEK_UNIT:
        days_in_unit = DAY_IN_WEEK
    elif unit == MONTH_UNIT:
        days_in_unit = DAY_IN_MONTH
    elif unit == YEAR_UNIT:
        days_in_unit = DAY_IN_YEAR
    else:
        days_in_unit = 0

    if unit == ALL_UNIT:
        infected_vaccinated_count = count_infected_vaccinated_all()
        total_infected = infected_vaccinated_count['infected_count']
        total_vaccinated = infected_vaccinated_count['vaccinated_count']
    else:
        infected_vaccinated_count = count_infected_vaccinated_daterange(
            days_in_unit)
        total_infected = infected_vaccinated_count['infected_count']
        total_vaccinated = infected_vaccinated_count['vaccinated_count']

    youngest = get_youngest_oldest_infected(YOUNGEST, unit)
    oldest = get_youngest_oldest_infected(OLDEST, unit)

    no_of_infected_data = get_infected_number_by_date_range(days_in_unit)
    no_of_infected_data.reverse()

    no_of_vaccinated_data = get_vaccinated_number_by_date_range(days_in_unit)
    no_of_vaccinated_data.reverse()
    count = 0
    for data in no_of_vaccinated_data:
        count += data['numberOfCount']
        data['numberOfCount'] = count

    return render_template('dashboard.html',
                           name=session.get('username', None),
                           admin_id=session.get(
                               "id", None),
                           unit=unit,
                           oldest=oldest,
                           youngest=youngest,
                           total_vaccinated=total_vaccinated,
                           total_infected=total_infected,
                           oldest_change='0',
                           youngest_change='0',

                           noOfInfectedData=no_of_infected_data,
                           noOfVaccinatedData=no_of_vaccinated_data,

                           percent_vaccinated_change='0',
                           percent_infected_change='0',
                           )
    # return session.get("id", None)


def count_infected_vaccinated_all():
    # counting of infected and vaccinated - based on health_historys and vaccination_historys doc
    return_data = {}

    # query for infected count - status: infected
    citizens_infected_count_all = mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
        [{'$unwind': "$health_historys"},
         {'$match': {"health_historys.status": "infected"}},
         {'$count': "health_historys"}
         ]
    )
    # query for vaccinated count - dose_type: first_dose, second_dose, booster
    citizens_vaccinated_count_all = mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
        [{'$unwind': "$vaccination_historys"},
         {'$match': {
             '$or': [{"vaccination_historys.dose_type": 'first_dose'},
                     {'vaccination_historys.dose_type': 'second_dose'},
                     {'vaccination_historys.dose_type': 'booster'}]
         }},
         {'$count': "vaccination_historys"}
         ]
    )
    return_data['infected_count'] = list(citizens_infected_count_all)[
        0]['health_historys']
    return_data['vaccinated_count'] = list(citizens_vaccinated_count_all)[
        0]['vaccination_historys']

    return return_data


def count_infected_vaccinated_daterange(days_in_unit):
    # counting of infected and vaccinated - based on date range
    return_data = {}
    print(days_in_unit, 'days in unit')
    citizens_infected_count_daterange = mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
        [{'$unwind': "$health_historys"},
         {'$match': {
             '$and': [{"health_historys.status": "infected"},
                      {'health_historys.updated_at': {'$gte': datetime.now() - timedelta(days=int(days_in_unit)),
                                                      '$lt': datetime.now()
                                                      }}]
         }},
         {'$count': "health_historys"}
         ]
    )

    citizens_vaccinated_count_daterange = mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
        [{'$unwind': "$vaccination_historys"},
         {'$match': {
             '$and': [
                 {'$or': [
                     {"vaccination_historys.dose_type": 'first_dose'},
                     {'vaccination_historys.dose_type': 'second_dose'},
                     {'vaccination_historys.dose_type': 'booster'}
                 ]
                 },
                 {'vaccination_historys.updated_at': {'$gte': datetime.now() - timedelta(days=int(days_in_unit)),
                                                      '$lt': datetime.now()}}
             ]
         }},
         {'$count': "vaccination_historys"}
         ]
    )

    infected_data = list(citizens_infected_count_daterange)
    print(infected_data)
    if len(infected_data) > 0:
        return_data['infected_count'] = infected_data[0]['health_historys']
    else:
        return_data['infected_count'] = 0

    vaccinated_data = list(citizens_vaccinated_count_daterange)
    if len(vaccinated_data) > 0:
        return_data['vaccinated_count'] = vaccinated_data[0]['vaccination_historys']
    else:
        return_data['vaccinated_count'] = 0

    return return_data


def get_youngest_oldest_infected(youngest_oldest, unit):
    if unit == ALL_UNIT:
        get_age_pipeline = mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
            [
                {'$project':
                 {'date_of_birth': 1,
                  'health_historys': 1,
                  'age': 1
                  }
                 },
                #  This is to calculated the age of citizen.
                {'$addFields':
                 {'age':
                  {'$subtract':
                   [
                       {'$subtract': [
                           {'$year': '$$NOW'},
                           {'$year': '$date_of_birth'}]
                        },
                       {'$cond':
                        [{'$gt': [0,
                                  {'$subtract': [
                                      {'$dayOfYear': '$$NOW'},
                                      {'$dayOfYear': '$date_of_birth'}]}]},
                         1,
                         0]
                        }
                   ]
                   }
                  }},
                {'$unwind': {'path': '$health_historys'}},
                {'$match': {'health_historys.status': 'infected'}},
                # $min=youngest, $max=oldest
                {'$group': {'_id': 1, 'age': {youngest_oldest: '$age'}}}
            ]
        )
        for doc in get_age_pipeline:
            age = doc.get('age')

        return age

    elif unit == DAY_UNIT:
        count = DAY_IN_DAY
    elif unit == WEEK_UNIT:
        count = DAY_IN_WEEK
    elif unit == MONTH_UNIT:
        count = DAY_IN_MONTH
    elif unit == YEAR_UNIT:
        count = DAY_IN_YEAR

    start_date = datetime.now() - timedelta(days=count)
    get_age_pipeline = mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
        [
            {'$project': {'date_of_birth': 1,
                          'health_historys': 1,
                          'age': 1}},
            #  This is to calculated the age of citizen.
            {'$addFields': {'age':
                            {'$subtract':
                             [{'$subtract': [
                                 {'$year': '$$NOW'},
                                 {'$year': '$date_of_birth'}]
                               },
                              {'$cond':
                               [{'$gt': [0,
                                         {'$subtract': [{'$dayOfYear': '$$NOW'},
                                                        {'$dayOfYear': '$date_of_birth'}]}]},
                                1,
                                0
                                ]
                               }
                              ]
                             }
                            }
             },
            {'$unwind': {'path': '$health_historys'}},
            {'$match': {'health_historys.status': 'infected',
                        'health_historys.updated_at': {'$gt': start_date}}},
            {'$group': {'_id': 1, 'age': {youngest_oldest: '$age'}}}

        ]
    )

    for doc in get_age_pipeline:
        age = doc.get('age')
    return age


def get_infected_number_by_date_range(days_in_unit):
    # ALL.
    if days_in_unit == 0:
        greater_than_date = datetime(
            2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        date_format = '%Y-%m'
        print('is all')
    else:
        print('days in unit', days_in_unit)
        greater_than_date = datetime.now() - timedelta(days=int(days_in_unit))
        date_format = '%Y-%m-%d'

        if days_in_unit == DAY_IN_YEAR:
            date_format = '%Y-%m'

    # datetime(2020, 1, 1, 0, 0, 0)
    infected_number = mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
        # Health History 24hrs, 7D, 1M
        [
            {
                '$unwind': {
                    'path': '$health_historys'
                }
            }, {
                '$sort': {
                    'health_historys.updated_at': 1
                }
            }, {
                '$match': {
                    '$and': [{"health_historys.status": "infected"},
                             {'health_historys.updated_at': {'$gte': greater_than_date,
                                                             }}]
                }}, {
                '$project': {
                    'day': {
                        '$dateToString': {
                            'format': date_format,
                            'date': '$health_historys.updated_at'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$day',
                    'views': {
                        '$sum': 1
                    }
                }
            }, {
                '$project': {
                    'date': '$_id',
                    'views': '$views'
                }
            }, {
                '$group': {
                    '_id': None,
                    'stats': {
                        '$push': '$$ROOT'
                    }
                }
            }, {
                '$project': {
                    'stats': {
                        '$map': {
                            'input': date_range_obtainer(days_in_unit),
                            'as': 'date',
                            'in': {
                                '$let': {
                                    'vars': {
                                        'dateIndex': {
                                            '$indexOfArray': [
                                                '$stats._id', '$$date'
                                            ]
                                        }
                                    },
                                    'in': {
                                        '$cond': {
                                            'if': {
                                                '$ne': [
                                                    '$$dateIndex', -1
                                                ]
                                            },
                                            'then': {
                                                '$arrayElemAt': [
                                                    '$stats', '$$dateIndex'
                                                ]
                                            },
                                            'else': {
                                                '_id': '$$date',
                                                'date': '$$date',
                                                'views': 0
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }, {
                '$unwind': {
                    'path': '$stats'
                }
            }, {
                '$replaceRoot': {
                    'newRoot': '$stats'
                }
            }
        ]
    )
    return list(infected_number)
    # print(list(infected_number))


def get_vaccinated_number_by_date_range(days_in_unit):
    # ALL.
    if days_in_unit == 0:
        greater_than_date = datetime(
            2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        date_format = '%Y-%m'
        print('is all')
    else:
        print('days in unit', days_in_unit)
        greater_than_date = datetime.now() - timedelta(days=int(days_in_unit))
        date_format = '%Y-%m-%d'

        if days_in_unit == DAY_IN_YEAR:
            date_format = '%Y-%m'

    # datetime(2020, 1, 1, 0, 0, 0)
    vaccinated_number = mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
        # Health History 24hrs, 7D, 1M
        [
            {
                '$unwind': {
                    'path': '$vaccination_historys'
                }
            }, {
                '$sort': {
                    'vaccination_historys.updated_at': -1
                }
            }, {
                '$match': {
                    'vaccination_historys.updated_at': {
                        '$gt': greater_than_date
                    }
                }
            }, {
                '$project': {
                    'month': {
                        '$dateToString': {
                            'format': date_format,
                            'date': '$vaccination_historys.updated_at'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$month',
                    'numberOfCount': {
                        '$sum': 1
                    }
                }
            }, {
                '$sort': {
                    '_id': -1
                }
            }, {
                '$group': {
                    '_id': None,
                    'stats': {
                        '$push': '$$ROOT'
                    }
                }
            }, {
                '$project': {
                    'stats': {
                        '$map': {
                            'input': date_range_obtainer(days_in_unit),
                            'as': 'date',
                            'in': {
                                '$let': {
                                    'vars': {
                                        'dateIndex': {
                                            '$indexOfArray': [
                                                '$stats._id', '$$date'
                                            ]
                                        }
                                    },
                                    'in': {
                                        '$cond': {
                                            'if': {
                                                '$ne': [
                                                    '$$dateIndex', -1
                                                ]
                                            },
                                            'then': {
                                                '$arrayElemAt': [
                                                    '$stats', '$$dateIndex'
                                                ]
                                            },
                                            'else': {
                                                '_id': '$$date',
                                                'date': '$$date',
                                                'numberOfCount': 0
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }, {
                '$unwind': {
                    'path': '$stats'
                }
            }, {
                '$replaceRoot': {
                    'newRoot': '$stats'
                }
            }
        ]
    )
    return list(vaccinated_number)


@ app.route('/login', methods=['GET', 'POST'])
def login():
    ''' API. Send a request to authethic user.

    Returns:
        HTML: redirect you to the correct page upon authentication.
    '''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = mongo_db_client.db[ADMIN_COLLECTION_NAME].find_one({
            "username": username,
            "password": hashlib.md5(password.encode()).hexdigest()})
        print(parse_json(admin))
        admin = parse_json(admin)
        if admin is None:
            return redirect(url_for('login'))
        else:
            session['username'] = username
            session['id'] = admin['_id']['$oid']

        if 'username' in session:
            return redirect(url_for('index'))

        return render_template('login.html', name=session.get('username', None))
    # print(admin)
    # login_status = admin_statements.authenticate_admin(database_client,
    #                                                    username,
    #                                                    password)

    # Redirect user to login if login fail else set session and redirect to
    # home page index.
    # if not login_status:
    #     return redirect(url_for('login'))
    # else:
    #     session['username'] = username
    #     session['id'] = login_status

    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html', name=session.get('username', None))


@ app.route('/manage-citizen')
@ login_required
def manage_citizen():
    ''' / manage-citizen Route. Manage Citizen screen of the webpage.
    User need to be login.

    Returns:
        render_template: HTML webpage.
    '''
    # # For pagination.
    search_pipeline_statement = None
    if request.args.get('page') is None or \
            not request.args.get('page').isdigit():
        page = 1
    else:
        page = int(request.args.get('page'))

    # For search.
    search_pipeline_statement = None
    if request.args.get('search') is None:
        search = ''
    else:
        search = request.args.get('search')
        search_pipeline_statement = {'$match': {
            'full_name': {'$regex': search, '$options': 'i'}}}

    # Get all citizens from mongodb.
    # Get the most recent vaccination and health historys. As vaccination and
    # health historys are array, we unwind all of them first then sort by
    # latest first. We then get the first of each _id value.
    recent_citizens_pipeline = [
        {'$unwind': '$health_historys'},
        {'$unwind': '$vaccination_historys'},
        {'$sort': {'health_historys.updated_at': pymongo.DESCENDING,
                   'vaccination_historys.updated_at': pymongo.DESCENDING}},
        {'$group': {'_id': '$_id',
                    'recent_health': {'$first': '$health_historys'},
                    'recent_vaccination': {'$first': '$vaccination_historys'},
                    'nric': {'$first': '$nric'},
                    'full_name': {'$first': '$full_name'},
                    'address': {'$first': '$address'},
                    'mobile': {'$first': '$mobile'},
                    'date_of_birth': {'$first': '$date_of_birth'},
                    'gender': {'$first': '$gender'},
                    }},
        {'$sort': {'nric': pymongo.ASCENDING}},
    ]

    # For search.
    if search_pipeline_statement is not None:
        recent_citizens_pipeline.append(search_pipeline_statement)

    # For pagination.
    recent_citizens_pipeline.append({
        '$facet': {
            'metadata': [{'$count': 'total'}],
            'data': [{'$skip': (page-1)*8}, {'$limit': 8}]
        }})

    citizen_data = list(mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
        recent_citizens_pipeline))[0]
    print(citizen_data)

    for citizen in citizen_data['data']:
        vaccination_text = ''
        # Fix vaccination text for table.
        if citizen['recent_vaccination']['dose_type'] == 'first_dose':
            vaccination_text += 'First Dose'
        elif citizen['recent_vaccination']['dose_type'] == 'second_dose':
            vaccination_text += 'Second Dose'
        else:
            vaccination_text += 'Booster'

        # Get amount of hours after the recent vaccination.
        hours_ago = floor((datetime.now() -
                           (citizen['recent_vaccination']['updated_at'])).total_seconds() / 3600)
        vaccination_text += (' ' + str(hours_ago) + ' hours ago')

        citizen['recent_vaccination_text'] = vaccination_text
        # fixed_citizens.append(citizen)

    vaccines = mongo_db_client.db[VACCINE_COLLECTION_NAME].find()
    print('--------')
    if len(citizen_data['metadata']) > 0:
        num_of_pages = ceil(citizen_data['metadata'][0]['total']/8)
        total_records = citizen_data['metadata'][0]['total']
    else:
        num_of_pages = 0
        total_records = 0

    return render_template('citizenManagement.html',
                           name=session.get('username', None),
                           admin_id=session.get(
                               "id", None),
                           citizens=citizen_data['data'],
                           num_of_records=len(citizen_data['data']),
                           current_page=page,
                           num_of_pages=num_of_pages,
                           total_records=total_records,
                           vaccines=vaccines,
                           search=search
                           )


@ app.route('/manage-vaccine')
@ login_required
def manage_vaccine():
    ''' / manage-vaccine Route. Manage Vaccine screen of the webpage.
    User need to be login.

    Returns:
        render_template: HTML webpage.
    '''
    # Get all vaccine for update vaccination history.

    # vaccines = vaccine_statements.get_all_vaccines(database_client)
    # vaccine_data = list(mongo_db_client.db[VACCINE_COLLECTION_NAME].aggregate(
    #     vaccine_pipeline))
    # print(vaccine_data)
    vaccine_data = list(mongo_db_client.db[VACCINE_COLLECTION_NAME].find())
    print(vaccine_data)
    return render_template('vaccineManagement.html',
                           name=session.get('username', None),
                           admin_id=session.get("id", None),
                           vaccines=vaccine_data,
                           )


@ app.route('/manage-cluster')
@ login_required
def manage_cluster():
    ''' /manage-cluster Route. Manage Cluster screen of the webpage.
    User need to be login.
    Returns:
        render_template: clusterManagement HTML webpage.
    '''
    data = neo4j_db_client.getClusterInfo()
    return render_template('clusterManagement.html',
                           name=session.get('username', None),
                           admin_id=session.get(
                               "id", None),
                           data=data)


@ app.route('/update-health-history', methods=['POST'])
def update_health_history():
    ''' API. Send a request to update health history using citizen id.

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        citizen_id = request.json['citizen_id']
        admin_id = request.json['admin_id']
        new_status = request.json['new_status']

        if new_status != 'infected' and \
                new_status != 'healthy' and \
                new_status != 'dead':
            return 'error', 200

        # Mongo update.
        result = mongo_db_client.db[CITIZEN_COLLECTION_NAME].update_one(
            {'_id': ObjectId(citizen_id)},
            {
                '$push': {
                    'health_historys': {'status': new_status,
                                        'updated_by_id': ObjectId(admin_id),
                                        'updated_by_name': session.get('username', None),
                                        'updated_at': datetime.now()}
                }
            }
        )

        # Neo4J update.
        neo4j_db_client.update_citizen_status(citizen_id, new_status)

        if result.matched_count > 0:
            return 'success', 200
        return 'error in insert', 200

    return 'no POST', 200


@ app.route('/update-vaccination-history', methods=['POST'])
def update_vaccination_history():
    ''' API. Send a request to update vaccination history using citizen id.

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        citizen_id = request.json['citizen_id']
        admin_id = request.json['admin_id']
        vaccine_id = request.json['vaccine_id']
        new_dose_type = request.json['new_dose_type']

        if new_dose_type != 'first_dose' and \
           new_dose_type != 'second_dose' and \
           new_dose_type != 'booster':
            return 'error', 200

        result = mongo_db_client.db[CITIZEN_COLLECTION_NAME].update_one(
            {'_id': ObjectId(citizen_id)},
            {
                '$push': {
                    'vaccination_historys': {'dose_type': new_dose_type,
                                             'updated_by_id': ObjectId(admin_id),
                                             'updated_by_name': session.get('username', None),
                                             'vaccine_id': ObjectId(vaccine_id),
                                             'updated_at': datetime.now()}
                }
            }
        )

        if result.matched_count > 0:
            return 'success', 200
        return 'error in insert', 200

    return 'no POST', 200


@ app.route('/get-citizens-in-cluster', methods=['POST'])
def get_citizens_in_cluster():
    ''' API. Send a request to get all citizen in cluster using landmark id.
    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        landmark_id = request.json['landmark_id']
        records = neo4j_db_client.getCitizensInCluster(landmark_id)
        return json.dumps(records)
    return 'record not found', 400


@ app.route('/detect-update-clusters', methods=['POST'])
def detect_update_clusters():
    ''' API. Send a request to detect new clusters and also update cluster status.
    Returns:
        record of db data queried through AuraDB
    '''
    if request.method == 'POST':
        detect_update = neo4j_db_client.detect_update_clusters()
        if detect_update:
            return "successfully updated", 200
        else:
            return "error", 200
    return 'error', 200


@ app.route('/get-citizen-history', methods=['POST'])
def get_citizen_history():
    ''' API. Send a request to get all citizen history using citizen id.

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        citizen_id = request.json['citizen_id']
        print(citizen_id)

        citizen_history_pipeline = [
            {'$match': {'_id': ObjectId(citizen_id)}},
            {'$project': {'historys': {
                '$concatArrays': [
                    "$health_historys",
                    "$vaccination_historys"]
            },
                '_id': 0,
            }},
            {'$project': {'historys.status': 1,
                          'historys.dose_type': 1,
                          'historys.updated_at': 1,
                          'historys.updated_by_name': 1
                          }},
            {"$unwind": "$historys"},
            {'$sort': {'historys.updated_at': pymongo.DESCENDING, }},
        ]

        citizen_data = list(mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
            citizen_history_pipeline))
        print(citizen_data)
        # records = citizen_statements.get_citizen_history(
        #     database_client, citizen_id)

        return jsonify(citizen_data)

    return 'record not found', 400


@ app.route('/get-citizen-footprints', methods=['POST'])
def get_citizen_footprints():
    ''' API. Send a request to get all citizen footprint using citizen id.

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        citizen_id = request.json['citizen_id']
        citizen_footprint_pipeline = [
            {'$match': {'_id': ObjectId(citizen_id)}},
            {'$project': {
                '_id': 0,
                'footprints': 1,
            }},
            {'$project': {
                'footprints.landmark_id': 0,
            }},
            {"$unwind": "$footprints"},
            {'$sort': {'footprints.updated_at': pymongo.DESCENDING, }},
        ]

        citizen_data = list(mongo_db_client.db[CITIZEN_COLLECTION_NAME].aggregate(
            citizen_footprint_pipeline))

        print(citizen_data)
        return jsonify(citizen_data)

    return 'record not found', 400


@ app.route('/insert-citizen-footprints', methods=['POST'])
def insert_citizen_footprints():
    ''' API. Send a request to insert citizen footprints within a range.
    Add 3 footprints per citizen

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        insert_range = request.json['range']

        # Get seconds in insert_range.
        if insert_range == DAY_UNIT:
            insert_range_in_seconds = SECOND_IN_DAY
        elif insert_range == WEEK_UNIT:
            insert_range_in_seconds = SECOND_IN_WEEK
        elif insert_range == MONTH_UNIT:
            insert_range_in_seconds = SECOND_IN_MONTH
        else:
            insert_range_in_seconds = SECOND_IN_YEAR

        landmark_data = list(mongo_db_client.db[LANDMARK_COLLECTION_NAME].find(
            {}, {"_id": 1, "name": 1, }))

        citizen_data = list(mongo_db_client.db[CITIZEN_COLLECTION_NAME].find(
            {}, {"_id": 1}))

        for c in citizen_data:
            # Generate 3 landmarks to update each citizen footprints.
            random_landmarks = random.sample(landmark_data, 3)

            push_data = []
            for landmark in random_landmarks:
                # Generate random datetime for updated_at.
                random_datetime = datetime.now() - \
                    timedelta(seconds=random.randint(
                        0, insert_range_in_seconds))

                push_data.append({
                    'landmark_id': landmark['_id'],
                    'landmark_name': landmark['name'],
                    'updated_at': random_datetime})

                neo4j_db_client.insert_landmark_footprint(
                    str(c['_id']), str(landmark['_id']))

            # Update citizen footprints with more footprints.
            # Mongo insert into array.
            result = mongo_db_client.db[CITIZEN_COLLECTION_NAME].update_one(
                {'_id': c['_id']},
                {'$push': {
                    'footprints': {
                        '$each': push_data}}})

        if result.matched_count > 0:
            return 'success', 200

        return 'error in insert', 200

    return 'no POST', 200


@ app.route('/vaccines', methods=['POST'])
def create_vaccine(v_id=None):
    ''' API. Send a request to creates vaccine.

    Returns:
        JSON: response and status code back to requester.
    '''
    # Create
    if request.method == 'POST':
        name = request.json['name']
        v_type = request.json['type']
        print(name, v_type)

        result = mongo_db_client.db[VACCINE_COLLECTION_NAME] \
            .insert_one({'name': name, 'type': v_type})
        # db_status = vaccine_statements.create_vaccine(
        #     database_client, name, v_type)

        # mydict = { "name": "John", "address": "Highway 37" }

        # x = mycol.insert_one(mydict)

        if result.inserted_id is not None:
            return 'success', 200
        return 'error in insert', 200


@ app.route('/vaccines/<v_id>', methods=['PUT', 'DELETE'])
def update_delete_vaccine(v_id=None):
    ''' API. Send a request to update or delete vaccine.

    Returns:
        JSON: response and status code back to requester.
    '''
    # Update.
    if request.method == 'PUT':
        print('is in put rn', v_id)
        name = request.json['name']
        v_type = request.json['type']
        print(name, v_type)
        result = mongo_db_client.db[VACCINE_COLLECTION_NAME] \
            .update_one(
                {'_id': ObjectId(v_id)},
                {'$set': {'name': name, 'type': v_type}})

        if result.matched_count > 0:
            return 'success', 200
        return 'error in update', 200

    # Delete
    elif request.method == 'DELETE':
        result = mongo_db_client.db[VACCINE_COLLECTION_NAME].delete_one({
            '_id': ObjectId(v_id)})

        if result.deleted_count > 0:
            return 'success', 200
        return 'error in delete', 200

    return 'no such method', 200


@ app.route('/logout')
@ login_required
def logout():
    ''' / API. Log user out.

    Returns:
        HTML: redirect user to correct page.
    '''
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Connect to mongo db client.
    mongo_db_client = mongo_client.MongoDBClient(
        'mongodb+srv://admin:tJbJLK8YiYkDKYg@cluster0.96usv.mongodb.net/?retryWrites=true&w=majority')
    mongo_db_client.connect_to_client()
    mongo_db_client.connect_to_database('2103_covid_tracer')

    # Connect to neo4j client.
    neo4j_db_client = neo4j_client.Neo4JDBClient(
        'neo4j+s://c6e9b0ba.databases.neo4j.io',
        'neo4j',
        'ookMFGysaMn9Iwy80SFMPKQazP1BSehgn1ocB4AWiig')
    neo4j_db_client.connect_to_client()

    app.run(debug=True, port=3000)
