'''
This module encapulsates all functions needed for SQL queries regarding 
vaccine to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import mysql.connector

from constants import *


def create_table(database_client):
    ''' Create the vaccine table.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    database_client.execute_statement(f'''CREATE TABLE {VACCINE_TABLE_NAME}
                    (id INT(8) NOT NULL AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id)
                    )''')


def insert_initial_data(database_client):
    ''' Insert vaccine data into the table.
    Args:
        database_client (DatabaseClient): database client object.

    Returns:
        List: all the rows inserted into db.
    '''
    # Default data of vaccines.
    vaccine_data = [
        ('Sinovac', 'WHOLE VIRUS VACCINE'),
        ('Sinopharm', 'WHOLE VIRUS VACCINE'),
        ('Pfizer-BioNTech', 'RNA or mRNA VACCINE'),
        ('Moderna', 'RNA or mRNA VACCINE'),
        ('Oxford-AstraZeneca', 'NON-REPLICATING VIRAL VECTOR'),
        ('Sputnik V', 'NON-REPLICATING VIRAL VECTOR'),
        ('Novavax', 'PROTEIN SUBUNIT')
    ]

    return create_multiple_vaccines(database_client, vaccine_data)


def create_vaccine(database_client, name, v_type):
    ''' Create one vaccine.
    Args:
        database_client (DatabaseClient): database client object.
        name (str): name of vaccine.
        v_type (str): type of vaccine.

    Returns:
        bool: result of row inserted into db.
    '''
    result = database_client.create(
        VACCINE_TABLE_NAME,
        VACCINE_EDITABALE_COLUMNS,
        (name, v_type))

    return result


def create_multiple_vaccines(database_client, vaccines):
    ''' Create many vaccines.
    Args:
        database_client (DatabaseClient): database client object.
        vaccines (list): list of tuples of vaccines to insert into db.

    Returns:
        bool: result of row inserted into db.
    '''
    result = database_client.create_many(
        VACCINE_TABLE_NAME,
        VACCINE_EDITABALE_COLUMNS,
        vaccines)

    return result


def get_all_vaccines(database_client):
    '''Get all vaccines in db.
    Args:
        database_client (DatabaseClient): database client object.

    Returns:
        list: list of tuples of vaccines read from the db.
    '''
    # Fetch all vaccine data.
    rows = database_client.select_all(VACCINE_TABLE_NAME)

    return rows


def update_vaccine(database_client, v_id, change_columns, new_values):
    ''' Update vaccine by id using changed_columns and new_values.
    Args:
        database_client (DatabaseClient): database client object.
        v_id (int): vaccine id row to update.
        changed_columns (list): the list of columns names to be updated.
        new_values (list): the list of values to update with.

    Returns:
        bool: result of update.
    '''
    # TODO: check if there is bugs with int.
    result = database_client.update_by_id(
        VACCINE_TABLE_NAME, v_id, change_columns, new_values)

    return result


def delete_vaccine(database_client, v_id):
    '''Delete vaccine by id.
    Args:
        database_client (DatabaseClient): database client object.
        v_id (int): vaccine id row to update.

    Returns:
        bool: result of delete.
    '''
    result = database_client.delete_by_id(VACCINE_TABLE_NAME, v_id)

    return result
