'''
This module encapulsates all functions needed for SQL queries regarding area
to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import csv
import mysql.connector

from constants import *


class Area:
    def __init__(self, area_id, name, region, created_at, updated_at):
        self.id = area_id
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at


def create_table(database_client):
    ''' Create the area table.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    # Statement to create the area table.
    database_client.execute_statement(f'''CREATE TABLE {AREA_TABLE_NAME}
                    (id INT(8) NOT NULL AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    region ENUM('central', 'east', 'north', 'north-east', 'west', 'south','north-west', 'south-east','south-west') NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    UNIQUE (name, region)
                    )''')


def insert_initial_data(database_client):
    ''' Insert area data into the table.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    area_data = []

    # Get areas from csv for db population.
    with open('data/areas.csv') as area_file:
        csv_reader = csv.reader(area_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                name = row[0]
                region = row[1].replace(' ', '-')
                area_data.append((name, region))

    return createMultipleAreas(database_client, area_data)


def create_multiple_areas(database_client, areas):
    ''' Create many areas.
    Args:
        database_client (DatabaseClient): database client object.
        areas (list of tuple): areas data to insert into db.

    Returns:
        bool: result of query.
    '''
    result = database_client.create_many(
        AREA_TABLE_NAME,
        AREA_EDITABALE_COLUMNS,
        areas)

    return result


def get_all_areas(database_client):
    '''Get all areas in db.
    Args:
        database_client (DatabaseClient): database client object.

    Returns:
        list: all rows in area table.
    '''
    # Fetch all area data.
    rows = database_client.select_all(AREA_TABLE_NAME)

    return rows


# def updateVaccine(database_client, v_id, change_columns, new_values):
#     '''
#     Update vaccine by id using changed_columns and new_values.
#     '''
#     # TODO: check if there is bugs with int.
#     result = database_client.updateById(
#         VACCINE_TABLE_NAME, v_id, change_columns, new_values)

#     return result


# def deleteVaccine(database_client, v_id):
#     '''
#     Delete vaccine by id.
#     '''
#     result = database_client.deleteById(VACCINE_TABLE_NAME, v_id)

#     return result
