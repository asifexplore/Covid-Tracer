'''
This module encapulsates all functions needed for SQL queries regarding 
landmark to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import random
import mysql.connector
import db_statements.area as area_statements

from constants import *


def create_table(database_client):
    ''' Create the landmark table.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    # Statement to create the citizen table.
    database_client.execute_Statement(f'''CREATE TABLE {LANDMARK_TABLE_NAME}
                    (id INT(8) NOT NULL AUTO_INCREMENT,
                    area_id INT(8) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    latitude FLOAT(10,6) NOT NULL,  
                    longitude FLOAT(10,6) NOT NULL,
                    danger_level INT(1) DEFAULT 0 CHECK(danger_level >= 0 AND danger_level <= 5),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    FOREIGN KEY (area_id) REFERENCES areas(id),
                    UNIQUE (latitude, longitude)
                    )''')


def insert_initial_data(database_client):
    '''
    Insert area data into the table.
    '''
    landmark_data = []

    # Generate landmark data.
    for area in area_statements.getAllAreas(database_client):
        for i in range(1, 3):
            rand_lat = str(round(random.uniform(1.283920, 1.414346), 6))
            rand_lng = str(round(random.uniform(103.763548, 103.878083), 6))
            landmark_data.append(
                (area[0], area[1] + ' landmark ' + str(i), rand_lat, rand_lng))

    return create_multiple_landmarks(database_client, landmark_data)


def create_multiple_landmarks(database_client, landmarks):
    '''
    Create many landmarks.
    '''
    result = database_client.createMany(
        LANDMARK_TABLE_NAME,
        LANDMARK_EDITABALE_COLUMNS,
        landmarks)

    return result


def get_all_landmarks(database_client):
    '''Get all landmarks in db.
    Args:
        database_client (DatabaseClient): database client object.

    Returns:
        list: list of tuples of landmarks read from the db.
    '''
    # Fetch all vaccine data.
    cursor = database_client.execute_statement(
        f'''
        SELECT L.id, L.name, 
        CONCAT_WS(', ', L.latitude, L.longitude) AS coordinates,
        L.danger_level, A.name
        FROM landmarks L, areas A
        WHERE L.area_id = A.id
                            ''')

    result = cursor.fetchall()
    return result
    # rows = database_client.select_all(LANDMARK_TABLE_NAME)

    # return rows
