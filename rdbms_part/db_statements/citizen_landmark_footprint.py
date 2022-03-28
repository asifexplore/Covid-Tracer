'''
This module encapulsates all functions needed for SQL queries regarding 
citizen landmark footprint to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import random
import mysql.connector

from constants import *


def create_table(database_client):
    ''' Create the citizen landmark footprint table.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    # Statement to create the citizen landmark footprint table.
    database_client.execute_statement(f'''CREATE TABLE {CITIZEN_LANDMARK_FOOTPRINT_TABLE_NAME}
                    (id INT(8) NOT NULL AUTO_INCREMENT,
                    citizen_id INT(8) NOT NULL,
                    landmark_id INT(8) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    FOREIGN KEY (citizen_id) REFERENCES citizens(id),
                    FOREIGN KEY (landmark_id) REFERENCES landmarks(id)
                    )''')


def generate_landmark_footprints(database_client, citizen_ids, landmark_ids, t_range):
    ''' Insert landmark footprints of citizens with landmarks ids. There can be
    be mulitple landmark citizen have travel in a time range, t_range.
    Each citizen will generate 3 footprints.
    Args:
        database_client (DatabaseClient): database client object.
        citizen_ids (list): list of citizens ids to generate from.
        landmark_ids (list): list of landmark ids to generate from.
        t_range (int): day,week,month or year, will generate footprint randomly
        within t_range.

    Returns:
        bool: status of insert query.
    '''
    print('generate_landmark_footprints')
    # Get seconds from range.
    if t_range == YEAR_UNIT:
        seconds_in_range = SECOND_IN_YEAR
    elif t_range == MONTH_UNIT:
        seconds_in_range = SECOND_IN_MONTH
    elif t_range == WEEK_UNIT:
        seconds_in_range = SECOND_IN_WEEK
    elif t_range == DAY_UNIT:
        seconds_in_range = DAY_IN_DAY
    else:
        seconds_in_range = SECOND_IN_WEEK

    # For each citizen generate 3 footprint from 3 different landmark.
    insert_data = []
    insert_str = ''

    for citizen_id in citizen_ids:
        random_landmark_ids = random.sample(landmark_ids, 3)
        for landmark_id in random_landmark_ids:
            insert_data.append(
                (f'''({citizen_id},{landmark_id}, 
                FROM_UNIXTIME(UNIX_TIMESTAMP(NOW()) + FLOOR(0 - (RAND() * {seconds_in_range}))), 
                FROM_UNIXTIME(UNIX_TIMESTAMP(NOW()) + FLOOR(0 - (RAND() * {seconds_in_range}))))'''))

    insert_str += ','.join(insert_data)
    try:
        cursor = database_client.execute_statement(f'''
            INSERT INTO
                {CITIZEN_LANDMARK_FOOTPRINT_TABLE_NAME}(citizen_id, landmark_id, created_at, updated_at)
            VALUES
                {insert_str}
            ''')
        database_client.db.commit()
        return True
    except Exception as e:
        print(e)
        return False
