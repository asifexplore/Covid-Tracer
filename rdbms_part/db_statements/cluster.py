'''
This module encapulsates all functions needed for SQL queries regarding 
cluster to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import math

from constants import *


def create_table(database_client):
    '''
    This function helps to create the clusters table.
    Status and date formed were set with default values to facilitate the insertion process.
    This is because any insert into the cluster table would mean that the cluster is currently active at the time it is
    detected.
    '''
    database_client.execute_statement(
        # TODO: Redo db as landmark_id is link to CLF.
        f'''
        CREATE TABLE {CLUSTER_TABLE_NAME}
        (id INT(8) NOT NULL AUTO_INCREMENT,
        landmark_id INT(8) NOT NULL,
        status ENUM('active', 'closed') DEFAULT 'active' NOT NULL,
        date_formed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        date_closed TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (id, date_formed),
        FOREIGN KEY (landmark_id) REFERENCES {LANDMARK_TABLE_NAME}(id))
        )
        ''')
    '''
    Create clusters table working query
    CREATE TABLE clusters
    (id INT(8) NOT NULL AUTO_INCREMENT,
    landmark_id INT(8) NOT NULL,
    status ENUM('active', 'closed') DEFAULT 'active' NOT NULL,
    date_formed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_closed TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id, date_formed),
    FOREIGN KEY (landmark_id) REFERENCES landmarks(id))
    '''


def detect_clusters(database_client):
    '''
    Detect new clusters based on current database data. If the number of infected at each landmark >50,
    an active cluster is inserted into the landmark table.
    '''
    # get current date and date 14 days ago, to be used as date range for SQL query
    # execute SQL query to find clusters:
    # find the landmark_ids of landmarks which have 50 or more infected citizens in the past 14 days
    try:
        cursor = database_client.execute_statement(
            f'''
            INSERT INTO clusters (landmark_id) 
            SELECT CLF.landmark_id 
            FROM {CITIZEN_LANDMARK_FOOTPRINT_TABLE_NAME} CLF, {HEALTH_HISTORY_TABLE_NAME} HH 
            WHERE CLF.citizen_id = HH.citizen_id AND HH.status = 'infected' AND (CLF.updated_at BETWEEN DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND NOW())
            AND NOT EXISTS(SELECT C1.landmark_id 
                        FROM clusters C1, clusters C2 
                        WHERE C1.landmark_id = C2.landmark_id AND C1.status = 'active')
            GROUP BY CLF.landmark_id 
            HAVING COUNT(CLF.landmark_id)>=10
            ''')
        database_client.db.commit()
        return True

    except Exception as e:
        print(e)
        return False
    

    '''
    detect cluster WORKING QUERY
    INSERT INTO clusters (landmark_id) 
    SELECT CLF.landmark_id 
    FROM citizen_landmark_footprints CLF, health_historys HH 
    WHERE CLF.citizen_id = HH.citizen_id AND HH.status = 'infected' AND (CLF.updated_at BETWEEN DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND NOW())
    AND NOT EXISTS(SELECT C1.landmark_id 
                   FROM clusters C1, clusters C2 
                   WHERE C1.landmark_id = C2.landmark_id AND C1.status = 'active')
    GROUP BY CLF.landmark_id 
    HAVING COUNT(CLF.landmark_id)>=1
    '''


def update_clusters(database_client):
    '''
    check on the active clusters. If the number of infected at each landmark <50, the cluster is closed.
    Note that the update query here is only for closing the cluster.
    Re-opening a cluster would mean that data of past clusters at the same landmark would be lost.
    In order to keep better track of clusters in covid data, it was decided that clusters detected at the same landmark
    would be opened and inserted as a new cluster if it has already been closed. This ensures that past history of
    clusters detected at the same landmark would be kept and stored in the database.
    '''
    try:
        cursor = database_client.execute_statement(
        f'''
            UPDATE {CLUSTER_TABLE_NAME}
            SET status = 'closed', date_closed = NOW()
            WHERE {CLUSTER_TABLE_NAME}.landmark_id IN (
                 SELECT CLF.landmark_id
                 FROM citizen_landmark_footprints CLF, health_historys HH
                 WHERE CLF.citizen_id = HH.citizen_id AND HH.status = 'infected' AND (HH.updated_at BETWEEN DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND NOW())
                 GROUP BY CLF.landmark_id
                 HAVING COUNT(CLF.landmark_id)<10
                 )
        ''')
        database_client.db.commit()
        return True

    except Exception as e:
        print(e)
        return False
   

    '''cluster update working query
    UPDATE clusters
    SET status = 'closed', date_closed = NOW()
    WHERE clusters.landmark_id IN(
        SELECT CLF.landmark_id
        FROM citizen_landmark_footprints CLF, health_historys HH 
        WHERE CLF.citizen_id = HH.citizen_id AND HH.status = 'infected' AND (CLF.updated_at BETWEEN DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND NOW())
        GROUP BY CLF.landmark_id
        HAVING COUNT(CLF.landmark_id)<3)
    '''


def get_all_clusters(database_client, page=1):
    ''' Get all clusters in db.
    Args:
        database (int): database client object.
        page (int): page of data you want to get from. Each page have 8 rows.

    Returns:
        list: all the rows in a list of tuples.
    '''
    cursor = database_client.execute_statement(
        f'''
        SELECT L.name AS 'Landmark Name', 
        CSR.status AS 'Cluster Status', 
        CSR.date_formed AS 'Date Formed', 
        IFNULL(CSR.date_closed, '-') AS 'Date Closed', 
        COUNT(L.name) AS 'No. Citizens in Cluster',
        CSR.id
            FROM clusters CSR, citizens_in_clusters CIC, landmarks L, citizens C
            WHERE CSR.landmark_id = L.id AND CIC.cluster_id = CSR.id AND CIC.citizen_id = C.id
            GROUP BY CSR.id
        LIMIT {(page-1) * NUM_ROW_PER_PAGE},{NUM_ROW_PER_PAGE}
        ''')
    result = cursor.fetchall()
    return result

    '''
    working query for get all clusters
    SELECT L.name AS 'Landmark Name', CSR.status AS 'Cluster Status', CSR.date_formed AS 'Date Formed', IFNULL(CSR.date_closed, '-') AS 'Date Closed', COUNT(L.name) AS 'No. Citizens in Cluster'
    FROM clusters CSR, landmarks L, citizen_landmark_footprints CLF
    WHERE CSR.landmark_id = L.id AND CLF.landmark_id = CSR.landmark_id
    GROUP BY L.name

    SELECT L.name AS 'Landmark Name', 
    CSR.status AS 'Cluster Status', 
    CSR.date_formed AS 'Date Formed', 
    IFNULL(CSR.date_closed, '-') AS 'Date Closed', 
    COUNT(L.name) AS 'No. Citizens in Cluster',
    CSR.id
        FROM clusters CSR, citizens_in_clusters CIC, landmarks L, citizens C
        WHERE CSR.landmark_id = L.id AND CIC.cluster_id = CSR.id AND CIC.citizen_id = C.id
        GROUP BY CSR.id
    '''


def get_cluster_page_count(database_client):
    ''' Get count of pages in clusters. Each page is 8 rows.
    Args:
        database_client (DatabaseClient): database client object.

    Returns:
        int: count of number of pages in db for rows.
    '''
    cursor = database_client.execute_statement(
        f'''
            select count(*) from clusters CSR
                                ''')

    result = cursor.fetchone()
    return math.ceil(int(result[0]) / NUM_ROW_PER_PAGE)
