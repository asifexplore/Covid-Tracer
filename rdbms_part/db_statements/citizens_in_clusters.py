'''
This module encapulsates all functions needed for SQL queries regarding 
citizen in cluster to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import math

from constants import *


def create_table(database_client):
    '''Create the citizens_in_clusters table.
    This table keeps a history of which citizens were part of what clusters detected.
    Citizens can be part of multiple classes if they are still travelling around.
    Citizens are identified as super spreaders if they are part of multiple clusters.
    '''
    database_client.execute_statement(
        f'''
        CREATE TABLE {CITIZENS_IN_CLUSTER_TABLE_NAME}
        (id INT(8) NOT NULL AUTO_INCREMENT,
        citizen_id INT(8) NOT NULL,
        cluster_id INT(8) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (citizen_id) REFERENCES {CITIZEN_TABLE_NAME}(id),
        FOREIGN KEY (cluster_id) REFERENCES {CLUSTER_TABLE_NAME}(id))
        ''')

    # SQL statement.
    '''
    Create citizens_in_clusters table
    CREATE TABLE citizens_in_clusters
    (id INT(8) NOT NULL AUTO_INCREMENT,
    citizen_id INT(8) NOT NULL,
    cluster_id INT(8) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id),
    FOREIGN KEY (cluster_id) REFERENCES clusters(id))
    '''


def insert_citizens_into_cluster(database_client):
    '''
    Insert the relevant citizens part of the cluster.
    This statement should be run whenever a cluster is detected or updated.
    A citizen is not inserted into the same cluster if they are already part of it while the cluster is active.
    A citizen however can be part of a different cluster at the same landmark the cluster was detected. This is keeping
    in mind that the data tracked includes the past history of a landmark being detected as a cluster.
    Running this statement upon cluster update will check and insert new citizens part of active clusters.
    '''
    try:
        cursor = database_client.execute_statement(
            f'''
            INSERT INTO citizens_in_clusters (citizen_id, cluster_id)
            SELECT DISTINCT CLF.citizen_id, CSR.id
            FROM citizen_landmark_footprints CLF, clusters CSR, health_historys HH
            WHERE CSR.status = 'active' AND CSR.landmark_id = CLF.landmark_id AND CLF.citizen_id = HH.citizen_id AND HH.status = 'infected'  
            AND NOT EXISTS(
                SELECT DISTINCT CC1.citizen_id, CC1.cluster_id
                FROM citizens_in_clusters CC1
                WHERE CC1.citizen_id = CLF.citizen_id AND CC1.cluster_id = CSR.id)
            ''')
        #    AND NOT EXISTS(
        #     SELECT CC1.citizen_id, CC2.citizen_id
        #     FROM citizens_in_clusters CC1, citizens_in_clusters CC2
        #     WHERE CC1.citizen_id = CC2.citizen_id AND CC1.cluster_id = CC2.cluster_id)
        database_client.db.commit()
        return True

    except Exception as e:
        print(e)
        return False

    # SQL statement.
    '''
    working query for insertCitizens into cluster
    INSERT INTO citizens_in_clusters (citizen_id, cluster_id)
SELECT DISTINCT CLF.citizen_id, CSR.id
FROM citizen_landmark_footprints CLF, clusters CSR, health_historys HH
WHERE CSR.status = 'active' AND CSR.landmark_id = CLF.landmark_id AND CLF.citizen_id = HH.citizen_id AND HH.status = 'infected'  
AND NOT EXISTS(
    SELECT DISTINCT CC1.citizen_id, CC1.cluster_id
    FROM citizens_in_clusters CC1
    WHERE CC1.citizen_id = CLF.citizen_id AND CC1.cluster_id = CSR.id
)
    '''


def get_citizens_in_cluster(database_client, cluster_id):
    '''
    Get the details of citizens who have history being part of the specific cluster detected.
    Select the details of citizens who are part of the specific cluster detected.
    '''
    cursor = database_client.execute_statement(
        f'''
        SELECT DISTINCT L.name AS 'Landmark Name', C.nric AS 'NRIC', C.full_name AS 'Full Name', VH.most_recent_dose, 
        HH.most_recent_status, C.address AS 'Address', C.mobile AS 'Mobile', C.date_of_birth AS 'DoB', C.gender AS 'Gender'
        FROM citizens C
        INNER JOIN citizens_in_clusters CC
        ON C.id = CC.citizen_id
        INNER JOIN clusters CSR
        ON CSR.id = CC.cluster_id
        INNER JOIN landmarks L
        ON L.id = CSR.landmark_id
        INNER JOIN (SELECT citizen_id, dose_type AS 'most_recent_dose', timestampdiff(HOUR, created_at, now()) as 'time_since_dose'
                FROM vaccination_historys
                WHERE created_at in (SELECT MAX(created_at) FROM vaccination_historys GROUP BY citizen_id)) VH
        ON VH.citizen_id = CC.citizen_id
        INNER JOIN(SELECT citizen_id, status AS 'most_recent_status'
                FROM health_historys
                WHERE created_at in (SELECT MAX(created_at) FROM health_historys GROUP BY citizen_id)) HH
        ON HH.citizen_id = CC.citizen_id
        WHERE CSR.id = {cluster_id}
        ''')

    result = cursor.fetchall()
    return result

    # SQL statement.
    '''
    get citizens in cluster backup working query
    SELECT L.name, C.nric, C.full_name, VH.most_recent_dose, HH.most_recent_status, C.address, C.mobile, C.date_of_birth, C.gender
    FROM citizens C
    INNER JOIN citizens_in_clusters CC
    ON C.id = CC.citizen_id
    INNER JOIN clusters CSR
    ON CSR.id = CC.cluster_id
    INNER JOIN landmarks L
    ON L.id = CSR.landmark_id
    INNER JOIN (SELECT citizen_id, dose_type AS 'most_recent_dose', timestampdiff(HOUR, created_at, now()) as 'time_since_dose'
            FROM vaccination_historys
            WHERE created_at in (SELECT MAX(created_at) FROM vaccination_historys GROUP BY citizen_id)) VH
    ON VH.citizen_id = CC.citizen_id
    INNER JOIN(SELECT citizen_id, status AS 'most_recent_status'
            FROM health_historys
            WHERE created_at in (SELECT MAX(created_at) FROM health_historys GROUP BY citizen_id)) HH
    ON HH.citizen_id = CC.citizen_id
    WHERE L.name = 'Bishan landmark 2'
    '''
