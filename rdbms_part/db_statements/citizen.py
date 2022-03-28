'''
This module encapulsates all functions needed for SQL queries regarding 
citizen to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import math
import mysql.connector

from constants import *


def create_table(database_client):
    ''' Create the citizen table.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    # Statement to create the citizen table.
    database_client.execute_statement(f'''CREATE TABLE {CITIZEN_TABLE_NAME}
                    (id INT(8) NOT NULL AUTO_INCREMENT,
                    full_name VARCHAR(255) NOT NULL,
                    nric CHAR(9) NOT NULL,
                    address VARCHAR(255) NOT NULL,
                    mobile CHAR(8) NOT NULL,
                    date_of_birth DATE NOT NULL,
                    gender ENUM('male', 'female', 'others') NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    UNIQUE (nric)
                    )''')


def get_all_citizens(database_client, page=-1, search=''):
    ''' Get all citizen in db with their recent vaccination and health history.
    Args:
        database_client (DatabaseClient): database client object.
        page (int): page of data you want to get from. Each page have 8 rows.
        search (str): filter rows with search string.

    Returns:
        list: all the rows in a list of tuples.
    '''
    # Stucture search query.
    if search != '':
        search = 'WHERE C.full_name LIKE "%'+search+'%"'

    # Stucture pagination query.
    if page == -1:
        page_str = ''
    else:
        page_str = f'LIMIT {(page-1) * NUM_ROW_PER_PAGE},{NUM_ROW_PER_PAGE}'

    # Execute statement.
    cursor = database_client.execute_statement(
        f'''
        SELECT C.nric, C.full_name,
        CASE VH.most_recent_dose
            WHEN "first_dose" THEN "First Dose"
            WHEN "second_dose" THEN "Second Dose"
            WHEN "booster" THEN "Booster"
            ELSE "Nil"
        END AS "most_recent_dose",
        CASE 
            WHEN VH.time_since_dose< 24   THEN concat(FLOOR(VH.time_since_dose), " hours ago")
            WHEN VH.time_since_dose<730 THEN concat(FLOOR(VH.time_since_dose/24), " days ago")
            WHEN VH.time_since_dose< 8760 THEN concat(FLOOR(VH.time_since_dose/730), " months ago")
            ELSE concat(FLOOR(VH.time_since_dose/8760), " year ago")
        END AS "time",
        CONCAT(UPPER(SUBSTRING(HH.most_recent_status,1,1)),LOWER(SUBSTRING(HH.most_recent_status,2))) 
        as 'most_recent_status', C.address, C.mobile, DATE_FORMAT(C.date_of_birth, "%d %M %Y"),
        CONCAT(UPPER(SUBSTRING(C.gender,1,1)),LOWER(SUBSTRING(C.gender,2))) as 'gender', C.id
        FROM {CITIZEN_TABLE_NAME} C

        INNER JOIN(SELECT citizen_id, dose_type as 'most_recent_dose', timestampdiff(HOUR, created_at, now()) as 'time_since_dose'
        FROM {VACCINATION_HISTORY_TABLE_NAME}
        WHERE created_at in (SELECT MAX(created_at) from {VACCINATION_HISTORY_TABLE_NAME} GROUP BY citizen_id)) VH
        ON VH.citizen_id = C.id

        INNER JOIN(SELECT citizen_id, status as 'most_recent_status'
        FROM {HEALTH_HISTORY_TABLE_NAME}
        WHERE created_at in (SELECT MAX(created_at) from {HEALTH_HISTORY_TABLE_NAME} GROUP BY citizen_id)) HH
        ON HH.citizen_id = C.id
        {search}
        ORDER BY nric
        {page_str}
                            ''')

    # Get result and return.
    result = cursor.fetchall()
    return result


def get_citizen_page_count(database_client, search=''):
    '''Get count of pages in citizens. Each page is 8 rows.
    Args:
        database_client (DatabaseClient): database client object.
        search (str): filter rows with search string.

    Returns:
        int: count of number of pages in db for rows.
    '''
    # Stucture search query.
    if search != '':
        search = 'WHERE C.full_name LIKE "%'+search+'%"'

    # Execute statement.
    cursor = database_client.execute_statement(
        f'''
        select count(*) from citizens C {search}
                            ''')

    # Get result and return.
    result = cursor.fetchone()
    return math.ceil(int(result[0]) / NUM_ROW_PER_PAGE)


def get_citizen_history(database_client, citizen_id):
    '''Get all history of a citizen, will have both vaccination and health
    history since the beginning.
    Args:
        database_client (DatabaseClient): database client object.
        citizen_id (int): id of citizen to get row from.

    Returns:
        list: all history data of user.
    '''
    cursor = database_client.execute_statement(
        f'''
        SELECT 
        CASE hh.status
            WHEN "healthy" THEN "Healthy"
            WHEN "infected" THEN "Infected"
            WHEN "dead" THEN "Dead"
            ELSE "Nil"
        END AS "status",
        a.username, hh.created_at, 'health',
        IF(hh.created_at LIKE (select max(created_at) from health_historys WHERE citizen_id = {citizen_id}
        ), 'active', 'past')
        FROM health_historys hh, admins a
        WHERE hh.citizen_id = {citizen_id} and a.id = hh.updated_by_id
        UNION
        SELECT 
        CASE vh.dose_type
            WHEN "first_dose" THEN "First Dose"
            WHEN "second_dose" THEN "Second Dose"
            WHEN "booster" THEN "Booster"
            ELSE "Nil"
        END AS "status",
        a.username, vh.created_at, 'vaccination',
        IF(vh.created_at LIKE (select max(created_at) from vaccination_historys WHERE citizen_id = {citizen_id}
        ), 'active', 'past')
        FROM vaccination_historys vh, admins a
        WHERE vh.citizen_id = {citizen_id} and a.id = vh.updated_by_id
        ORDER BY created_at DESC
                            ''')

    result = cursor.fetchall()
    return result


def get_citizen_footprints(database_client, citizen_id):
    '''Get all citizen footprints of a citizen.
    Args:
        database_client (DatabaseClient): database client object.
        citizen_id (int): id of citizen to get row from.

    Returns:
        list: all footprint data of user.
    '''
    cursor = database_client.execute_statement(
        f'''
        SELECT L.name, A.name, CLF.created_at 
        FROM {CITIZEN_LANDMARK_FOOTPRINT_TABLE_NAME} CLF, {LANDMARK_TABLE_NAME} L, {AREA_TABLE_NAME} A
        WHERE CLF.landmark_id = L.id 
        AND A.id = L.area_id 
        AND CLF.citizen_id = {citizen_id}
        ORDER BY created_at DESC
                            ''')

    result = cursor.fetchall()
    return result

# def delete(mydb, mycursor):
#     username = input("Enter username to delete: ")
#     mycursor.execute("SELECT * FROM users WHERE username='" + username + "'")
#     myresult = mycursor.fetchone()
#     if myresult == None:
#         print("Username to delete incorrect!\n")
#     else:
#         print("User deleted: ", myresult)
#         mycursor.execute("DELETE FROM users WHERE username='" + username + "'")
#         mydb.commit()


# def edit(mydb, mycursor):
#     username = input("Enter username to update: ")
#     mycursor.execute("SELECT * FROM users WHERE username='" + username + "'")
#     myresult = mycursor.fetchone()
#     if myresult == None:
#         print("Username to update incorrect!\n")
#     else:
#         exit = False
#         while not exit:
#             choice = int(
#                 input(
#                     "1. Change username\n2. Change password\n3. Change email\n0. exit\n=> "
#                 ))
#             if choice == 1:
#                 new_username = input("enter new username: ")
#                 mycursor.execute("UPDATE users SET username='" + new_username +
#                                  "' WHERE username='" + username + "'")
#                 username = new_username
#             elif choice == 2:
#                 new_password = input("Enter new password: ")
#                 mycursor.execute("UPDATE users SET password='" + new_password +
#                                  "' WHERE username='" + username + "'")
#             elif choice == 3:
#                 new_email = input("enter new email: ")
#                 mycursor.execute("UPDATE users SET email='" + new_email +
#                                  "' WHERE username='" + username + "'")
#             elif choice == 0:
#                 print("Exit")
#                 exit = True
#             else:
#                 print("Enter wrong number")
#             mydb.commit()
#             print("User updated!\n")


# def show_all(mycursor):
#     mycursor.execute("SELECT id, username, email FROM users")
#     myresult = mycursor.fetchall()
#     for i in myresult:
#         print(i)


# def search(mycursor):
#     choice = int(input("1. Find username\n2. find email\n=> "))
#     if choice == 1:
#         username = input("Input username: ")
#         mycursor.execute(
#             "SELECT id, username, email FROM users WHERE username='" +
#             username + "'")
#         myresult = mycursor.fetchone()
#     elif choice == 2:
#         email = input("Input email: ")
#         mycursor.execute(
#             "SELECT id, username, email FROM users WHERE email='" + email +
#             "'")
#         myresult = mycursor.fetchone()
#     else:
#         print("R.T.F.M")
#     if myresult == None:
#         print("Username or email not found!\n")
#     else:
#         print("User found! Some info about = > ", myresult)
