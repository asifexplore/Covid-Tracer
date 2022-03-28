'''
This module encapulsates all functions needed for SQL queries regarding 
health history to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import mysql.connector
import db_statements.db_statements as db_statement
from constants import *


def create_table(database_client):
    ''' Create the health history table.
    Args:
        database_client (DatabaseClient): database client object.
    '''
    database_client.execute_statement(f'''CREATE TABLE {HEALTH_HISTORY_TABLE_NAME}
                    (id INT(8) NOT NULL AUTO_INCREMENT,
                    citizen_id INT(8) NOT NULL,
                    updated_by_id INT(8) NOT NULL,
                    status ENUM('healthy', 'infected', 'dead') NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    FOREIGN KEY (citizen_id) REFERENCES citizens(id),
                    FOREIGN KEY (updated_by_id) REFERENCES admins(id)
                    )''')


def create_health_history(database_client, admin_id, citizen_id, status):
    ''' Create a new row of health history.
    Args:
        database_client (DatabaseClient): database client object.
        admin_id (int): id of admin that created, act a foreign key to health 
        history.
        citizen_id (int): id of citizen, act a foreign key to health history.
        status (str): status DEAD/HEALTHY/INFECTED, act a foreign key to health
        history.

    Returns:
        bool: status of insert query.
    '''
    try:
        cursor = database_client.execute_statement(
            f'''INSERT INTO {HEALTH_HISTORY_TABLE_NAME}
                    (`citizen_id`, `updated_by_id`, `status`) 
                    VALUES 
                    ({citizen_id}, {admin_id}, '{status}')
            ''')

        database_client.db.commit()
        return True

    except Exception as e:
        print(e)
        database_client.db.rollback()
        return False


'''
function that get count and percentage of infected based on ALL
function return both count [0] and percentage [1]
'''


# def getAllInfected_Count_Percent(database_client):
#     # Reference to db_statements.py
#     resultCount = db_statement.select_Count_Vaccinated_Infected_Range(database_client, "Infected", "All")
#     resultPercent = db_statement.select_Percentage_Vaccinated_Infected_Range(database_client, "Infected", "All")

#     # formula to get %
#     for x in resultPercent:
#         percentage = (x[0] / x[1]) * 100

#     return resultCount, str(round(percentage))


'''
function that get count and percentage of infected based on DATE RANGE
selectedValue = 1,2,3,4 based dropdown list on screen
function return both count [0] and percentage [1]
'''


# def getInfectedRange_Count_Percent(database_client, selectedValue):
#     # get the enums to filteredDateRange based on selectedValue
#     if selectedValue == "1":
#         filteredDateRange = dateRange.PAST_24_HOURS
#     if selectedValue == "2":
#         filteredDateRange = dateRange.PAST_7_DAYS
#     if selectedValue == "3":
#         filteredDateRange = dateRange.PAST_1_MONTH
#     if selectedValue == "4":
#         filteredDateRange = dateRange.PAST_1_YEAR

#     # reference to db_statements.py
#     resultCount = db_statement.select_Count_Vaccinated_Infected_Range(database_client, "Infected", filteredDateRange.value)
#     resultPercent = db_statement.select_Percentage_Vaccinated_Infected_Range(database_client, "Infected", filteredDateRange.value)

#     # formula to get %
#     for x in resultPercent:
#         percentage = (x[0] / x[1]) * 100

#     return resultCount, str(round(percentage))
