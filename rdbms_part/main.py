'''
This module contains all routes.
@Author: Team 22 ICT2103 2021
'''
import db
import math
import random
import datetime
import functools
import mysql.connector
import db_statements.area as area_statements
import db_statements.admin as admin_statements
import db_statements.citizen as citizen_statements
import db_statements.vaccine as vaccine_statements
import db_statements.cluster as cluster_statements
import db_statements.db_statements as db_statements
import db_statements.landmark as landmark_statements
import db_statements.health_history as health_history_statements
import db_statements.vaccination_history as vaccination_history_statements
import db_statements.citizens_in_clusters as citizens_in_clusters_statements
import db_statements.citizen_landmark_footprint as citizen_landmark_footprint_statements

from constants import *
from datetime import datetime, timedelta
from flask import Flask, request, render_template, session, redirect, url_for, jsonify

# Init Flask and secret key.
app = Flask(__name__)
app.secret_key = '2103'


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
        day_in_unit = DAY_IN_DAY
    elif unit == WEEK_UNIT:
        day_in_unit = DAY_IN_WEEK
    elif unit == MONTH_UNIT:
        day_in_unit = DAY_IN_MONTH
    elif unit == YEAR_UNIT:
        day_in_unit = DAY_IN_YEAR
    else:
        # ALL.
        day_in_unit = 0

    # Get oldest and youngest infected over a daterange. card 1 and 2.
    oldest = db_statements.get_youngest_oldest_infected(
        database_client, OLDEST, unit)
    youngest = db_statements.get_youngest_oldest_infected(
        database_client, YOUNGEST, unit)
    oldest_change = db_statements.youngest_oldest_change(
        database_client, OLDEST, unit, oldest)
    youngest_change = db_statements.youngest_oldest_change(
        database_client, YOUNGEST, unit, youngest)

    # Get total infected over a date range. card 3.
    total_infected = db_statements.select_count_vaccinated_infected_range(
        database_client, INFECTED, day_in_unit)

    # Get infected change over a date range. card 3.
    percent_infected_change = 0
    for x in db_statements.select_percentage_vaccinated_infected_range(
            database_client, INFECTED, day_in_unit):
        percent_infected_change = (x[0] / x[1]) * 100
    percent_infected_change = str(round(percent_infected_change))

    # Get total vaccinated over a date range. card 4.
    total_vaccinated = db_statements.select_count_vaccinated_infected_range(
        database_client, VACCINATED, day_in_unit)

    # Get vaccinated change over a date range. card 4.
    percent_vaccinated_change = 0
    for x in db_statements.select_percentage_vaccinated_infected_range(
            database_client, VACCINATED, day_in_unit):
        percent_vaccinated_change = (x[0] / x[1]) * 100
    percent_vaccinated_change = str(round(percent_vaccinated_change))

    # Get no of infected data for chart 1.
    no_of_infected_data = db_statements.get_infected_number_by_date_range(
        database_client, day_in_unit * HOUR_IN_DAY)

    # Get vaccine distrubution data. chart 2.
    no_of_vaccine_distributed_raw_data = db_statements.get_vaccine_number_by_date_range(
        database_client, day_in_unit * HOUR_IN_DAY)

    # Init vaccine distrubution data labels and data.
    no_of_vaccine_distributed_labels = []
    no_of_vaccine_distributed_data = []
    total_count = 0

    # Sort vaccine distrubution data for chart 2.
    for vaccine_distributed_row in no_of_vaccine_distributed_raw_data:
        if unit == ALL_UNIT or unit == YEAR_UNIT:
            date = vaccine_distributed_row[1]
            count = vaccine_distributed_row[0]
        else:
            date = vaccine_distributed_row[0]
            count = vaccine_distributed_row[1]

        no_of_vaccine_distributed_labels.append(date)
        total_count += count
        no_of_vaccine_distributed_data.append(total_count)

    return render_template('dashboard.html',
                           unit=unit,
                           name=session.get("username", None),

                           oldest=oldest,
                           youngest=youngest,
                           oldest_change=oldest_change,
                           youngest_change=youngest_change,

                           total_vaccinated=total_vaccinated,
                           total_infected=total_infected,
                           percent_vaccinated_change=percent_vaccinated_change,
                           percent_infected_change=percent_infected_change,

                           noOfInfectedData=no_of_infected_data,

                           noOfVaccineDistributedLabels=no_of_vaccine_distributed_labels,
                           noOfVaccineDistributedData=no_of_vaccine_distributed_data,
                           )


@app.route('/manage-citizen')
@login_required
def manage_citizen():
    ''' /manage-citizen Route. Manage Citizen screen of the webpage. 
    User need to be login.

    Returns:
        render_template: HTML webpage.
    '''
    # For pagination.
    if request.args.get('page') is None or \
            not request.args.get('page').isdigit():
        page = 1
    else:
        page = int(request.args.get('page'))

    # For search.
    if request.args.get('search') is None:
        search = ''
    else:
        search = request.args.get('search')

    # Get all citizens records with latest vaccination and health history.
    citizens = citizen_statements.get_all_citizens(
        database_client, page, search)

    # Get total count of pages by using total citizens / 8.
    num_of_pages = citizen_statements.get_citizen_page_count(
        database_client, search)

    # Get all vaccine for update vaccination history.
    vaccines = vaccine_statements.get_all_vaccines(database_client)

    return render_template('citizenManagement.html',
                           name=session.get('username', None),
                           admin_id=session.get("id", None),
                           citizens=citizens,
                           current_page=page,
                           num_of_pages=num_of_pages,
                           vaccines=vaccines,
                           search=search
                           )


@app.route('/manage-cluster')
@login_required
def manage_cluster():
    ''' /manage-cluster Route. Manage Cluster screen of the webpage. 
    User need to be login.

    Returns:
        render_template: HTML webpage.
    '''
    # For pagination.
    if request.args.get('page') is None or \
            not request.args.get('page').isdigit():
        page = 1
    else:
        page = int(request.args.get('page'))

    num_of_pages = cluster_statements.get_cluster_page_count(
        database_client)

    # Get all clusters in db.
    print(page)
    clusters = cluster_statements.get_all_clusters(database_client, page)
    # print(clusters)

    return render_template('clusterManagement.html',
                           name=session.get("username", None),
                           clusters=clusters,
                           current_page=page,
                           num_of_pages=num_of_pages)


@app.route('/manage-vaccine')
@login_required
def manage_vaccine():
    ''' /manage-vaccine Route. Manage Vaccine screen of the webpage. 
    User need to be login.

    Returns:
        render_template: HTML webpage.
    '''
    # Get all vaccine for update vaccination history.

    vaccines = vaccine_statements.get_all_vaccines(database_client)
    print(vaccines)
    return render_template('vaccineManagement.html',
                           name=session.get('username', None),
                           admin_id=session.get("id", None),
                           vaccines=vaccines,
                           )


@app.route('/manage-landmark')
@login_required
def manage_landmark():
    ''' /manage-landmark Route. Manage Landmark screen of the webpage. 
    User need to be login.

    Returns:
        render_template: HTML webpage.
    '''
    # Get all vaccine for update vaccination history.

    landmarks = landmark_statements.get_all_landmarks(database_client)
    print(landmarks)
    return render_template('landmarkManagement.html',
                           name=session.get('username', None),
                           admin_id=session.get("id", None),
                           landmarks=landmarks,
                           )


@app.route('/detect-update-clusters', methods=['POST'])
def detect_and_update_clusters():
    ''' API. Send a request to detect and update all clusters.

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        detect = cluster_statements.detect_clusters(database_client)
        insert = citizens_in_clusters_statements.insert_citizens_into_cluster(
            database_client)
        update = cluster_statements.update_clusters(database_client)

        if detect and insert and update:
            return "successfully updated", 200
        else:
            return "error", 200

    return 'error', 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' API. Send a request to authethic user.

    Returns:
        HTML: redirect you to the correct page upon authentication.
    '''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_status = admin_statements.authenticate_admin(database_client,
                                                           username,
                                                           password)

        # Redirect user to login if login fail else set session and redirect to
        # home page index.
        if not login_status:
            return redirect(url_for('login'))
        else:
            session['username'] = username
            session['id'] = login_status

    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html', name=session.get('username', None))


@ app.route('/logout')
@ login_required
def logout():
    ''' / API. Log user out.

    Returns:
        HTML: redirect user to correct page.
    '''
    session.clear()
    return redirect(url_for('index'))


@ app.route('/get-citizens-in-cluster', methods=['POST'])
def get_citizens_in_cluster():
    ''' API. Send a request to get all citizen in cluster using cluster id.

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        cluster_id = request.json['cluster_id']
        records = citizens_in_clusters_statements.get_citizens_in_cluster(
            database_client, cluster_id)
        return jsonify(records)

    return 'record not found', 400


@ app.route('/get-citizen-history', methods=['POST'])
def get_citizen_history():
    ''' API. Send a request to get all citizen history using citizen id.

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        citizen_id = request.json['citizen_id']

        records = citizen_statements.get_citizen_history(
            database_client, citizen_id)

        return jsonify(records)

    return 'record not found', 400


@ app.route('/get-citizen-footprints', methods=['POST'])
def get_citizen_footprints():
    ''' API. Send a request to get all citizen footprint using citizen id.

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        citizen_id = request.json['citizen_id']
        records = citizen_statements.get_citizen_footprints(
            database_client, citizen_id)

        return jsonify(records)

    return 'record not found', 400


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

        db_status = health_history_statements.create_health_history(
            database_client, admin_id, citizen_id, new_status)

        if db_status:
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

        db_status = vaccination_history_statements.create_vaccination_history(
            database_client, admin_id, citizen_id, vaccine_id, new_dose_type)

        if db_status:
            return 'success', 200
        return 'error in insert', 200

    return 'no POST', 200


@ app.route('/insert-citizen-footprints', methods=['POST'])
def insert_citizen_footprints():
    ''' API. Send a request to insert citizen footprints within a range.
    Add 3 footprints per citizen

    Returns:
        JSON: status and status code back to requester.
    '''
    if request.method == 'POST':
        insert_range = request.json['range']
        citizen_ids = [c[9]
                       for c in citizen_statements.get_all_citizens(database_client)]

        landmark_ids = [l[0]
                        for l in landmark_statements.get_all_landmarks(database_client)]

        db_status = citizen_landmark_footprint_statements.generate_landmark_footprints(
            database_client, citizen_ids, landmark_ids, insert_range)

        # for citizen_id in citizen_ids:
        # insert_range, tuple of landmark ids

        # Pick 3 random landmark id from all landmark ids.
        # print(random.sample(landmark_ids, 3))
        # print(citizen_id)

        if db_status:
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

        db_status = vaccine_statements.create_vaccine(
            database_client, name, v_type)

        if db_status:
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
        db_status = vaccine_statements.update_vaccine(database_client, v_id,
                                                      ('name', 'type'), (name, v_type))

        if db_status:
            return 'success', 200
        return 'error in update', 200

    # Delete
    elif request.method == 'DELETE':
        print('is in delete rn', v_id)

        db_status = vaccine_statements.delete_vaccine(database_client, v_id)

        if db_status:
            return 'success', 200
        return 'error in delete', 200

    return 'no such method', 200


def init_all_tables(database_client):
    ''' Create all tables in db.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    try:
        admin_statements.create_table(database_client)
        citizen_statements.create_table(database_client)
        vaccine_statements.create_table(database_client)
        area_statements.create_table(database_client)
        landmark_statements.create_table(database_client)
        health_history_statements.create_table(database_client)
        vaccination_history_statements.create_table(database_client)
        citizen_landmark_footprint_statements.create_table(database_client)
        cluster_statements.create_table(database_client)
        citizens_in_clusters_statements.create_table(database_client)

        print('done')

    except Exception as e:
        print(e)


def init_all_tables_data(database_client):
    ''' Initialize all data into all tables.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    try:
        vaccine_statements.insert_initial_data(database_client)
        area_statements.insert_initial_data(database_client)
        landmark_statements.insert_initial_data(database_client)

        print('initial data created')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    database_client = db.DatabaseClient(
        '31.220.110.79',
        # '104.21.45.22',
        # '31.220.110.51',
        'u696578939_2103_admin',
        'jDHKIXZb+U0',
        'u696578939_2103_covid'
    )

    # Connect to the db.
    database_client.connect()
    # print(database_client.db)
    # print('connected')
    # admin_statements.insertInitialData(database_client)
    # initAllTables(database_client)
    # initAllTablesData(database_client)

    app.run(debug=True, port=3000)
