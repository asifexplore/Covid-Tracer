'''
This module encapulsates all functions needed for SQL queries regarding admin
to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import hashlib
import mysql.connector

from constants import *


class Admin:
    def __init__(self, admin_id, username, password, role, created_at, updated_at):
        self.id = admin_id
        self.username = username
        self.password = password
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at


def create_table(database_client):
    ''' Create the landmark table.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    # Statement to create the admin table.
    database_client.execute_statement(f'''CREATE TABLE {ADMIN_TABLE_NAME}
                    (id INT(8) NOT NULL AUTO_INCREMENT,
                    username VARCHAR(50) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    UNIQUE (username)
                    )''')


def insert_initial_data(database_client):
    '''Insert admin data into the table.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    # Default data to access the sys securely.
    admin_data = [('gerald', hashlib.sha512('pass1'.encode('utf-8')).hexdigest(), 'admin'),
                  ('adam', hashlib.sha512('pass2'.encode(
                      'utf-8')).hexdigest(), 'admin'),
                  ('asif', hashlib.sha512('pass3'.encode(
                      'utf-8')).hexdigest(), 'admin'),
                  ('yuhui', hashlib.sha512('pass4'.encode(
                      'utf-8')).hexdigest(), 'admin'),
                  ('jingyong', hashlib.sha512('pass5'.encode('utf-8')).hexdigest(), 'admin')]

    return create_multiple_admins(database_client, admin_data)


def create_multiple_admins(database_client, admins):
    '''Create many admins.
    Args:
        database_client (DatabaseClient): database client object.
        admins (list of tuple): admins data to insert into db.

    Returns:
        bool: result of query.
    '''
    result = database_client.create_many(
        ADMIN_TABLE_NAME,
        ADMIN_EDITABALE_COLUMNS,
        admins)

    return result


def authenticate_admin(database_client, username, password):
    '''Authenticate username and password.
    Args:
        database_client (DatabaseClient): database client object.
        username (str): username to recognise user.
        password (str): password to authentic user.

    Returns:
        str: id of user.
        OR
        bool: if login is false, will return False instead.
    '''
    password = hashlib.sha512(password.encode('utf-8')).hexdigest()
    cursor = database_client.execute_statement(f'''SELECT * FROM {ADMIN_TABLE_NAME}
                            WHERE username='{username}' AND password='{password}'
                            ''')

    result = cursor.fetchone()
    if result is None:
        return False
    return result[0]
