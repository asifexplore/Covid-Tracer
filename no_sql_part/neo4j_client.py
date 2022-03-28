from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable


class Neo4JDBClient:
    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    def connect_to_client(self):
        '''Connect to the server using credentials inside uri.
        Returns:
            bool: a bool of whether connect is successful.
        '''
        print('connect_to_client')
        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password))
            print('connected to neo4j client')
            return True

        except Exception as e:
            print(e)
            return False

    def update_citizen_status(self, citizen_id, status):
        '''updates citizen's most recent status in AuraDB.
        Returns:
            result record of citizen queries
        '''
        with self.driver.session() as session:
            result = session.write_transaction(
                self.run_citizen_status_update, citizen_id, status
            )
        return result

    @staticmethod
    def run_citizen_status_update(tx, citizen_id, status):
        '''static method required to run update_citizen_status query'''
        query = (f'''
            MATCH (c:Citizens  {{citizen_id:'{citizen_id}'}})
            SET c.most_recent_status = '{status}'
            RETURN c
        ''')
        status_update = tx.run(query)
        return status_update

    def insert_landmark_footprint(self, citizen_id, landmark_id):
        '''inserts citizen landmark footprints queries by citizen and landmark id.
        Returns:
            list containing citizen name, landmark name and date visited relationship.
        '''
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self.run_insert_landmark_footprint, citizen_id, landmark_id)
            result_string = []
            for data in result:
                result_string.append(data['c']['full_name'])
                result_string.append(data['l']['name'])
                result_string.append(data['r']['datetime'])
        return result_string

    @staticmethod
    def run_insert_landmark_footprint(tx, citizen_id, landmark_id):
        '''static method required to run insert_landmark_footprint'''
        query = (f'''
                MATCH (c:Citizens  {{citizen_id:'{citizen_id}'}})
                MATCH (l:Landmarks {{landmark_id:'{landmark_id}'}})
                MERGE (c)-[r:VISITED{{datetime:localdatetime.realtime('Singapore')}}]->(l)
                RETURN c, l, r
                ''')
        result = tx.run(query, citizen_id=citizen_id, landmark_id=landmark_id)
        try:
            return [{"c": row["c"], "l": row["l"], "r": row["r"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error(f'''{query} raised an error: \n {exception}'''.format(
                query=query, exception=exception))

    def detect_update_clusters(self):
        '''detect and update clusters advanced query.
        This function operates as a self query into AuraDB.
        No return is expected.
        '''
        with self.driver.session() as session:
            output = session.read_transaction(self.run_detect_update_clusters)
        return output

    @staticmethod
    def run_detect_update_clusters(tx):
        '''static method required to run detect and update clusters advanced query.
        Due to CQL limitations used for Neo4j Graph AuraDB, multiple queries were used to
        simulate behaviour similar to rbms implementation.
        '''
        # for each landmark, count number of infected citizens who have visited the landmark in the past 14 days.
        count_infected_query = (f'''
                MATCH(c:Citizens{{most_recent_status:'infected'}})-[r:VISITED]-(l:Landmarks)
                WHERE localdatetime.realtime('Singapore')-duration({{days:14}})<=r.datetime<=localdatetime.realtime('Singapore')
                return l, COUNT(r)
                ''')
        count_infected_output = tx.run(count_infected_query)
        num_infected = []
        end_output = []
        # for each landmark, detect and update clusters accordingly.
        for row in count_infected_output:
            # list[i][0] = landmark_id; list[i][1] = no. of infected found at landmark
            num_infected.append([row['l']['landmark_id'], row['COUNT(r)']])
        for i in range(len(num_infected)):
            if num_infected[i][1] > 10:
                create_cluster_query = (f'''
                    MATCH (l:Landmarks{{landmark_id:'{num_infected[i][0]}'}})
                    MERGE (l)-[r:CLUSTER_DETECTED]-(cls:Clusters{{status:'active'}})
                    ON CREATE SET cls += {{date_formed:date.statement('Singapore'), date_closed:''}}
                    RETURN l, r, cls
                    ''')
                create_cluster = tx.run(create_cluster_query)
                end_output.append(create_cluster)
            elif num_infected[i][1] <= 10:
                update_cluster_query = (f'''
                    MATCH (l:Landmarks{{landmark_id:'{num_infected[i][0]}'}})-[r:CLUSTER_DETECTED]-(cls:Clusters{{status:'active'}})
                    SET cls.status = 'closed', cls.date_closed = date.statement('Singapore')
                    RETURN l, r, cls
                ''')
                update_cluster = tx.run(update_cluster_query)
                end_output.append(update_cluster)
            else:
                end_output.append('no updates')
        return end_output

    def getClusterInfo(self):
        '''Function to fetch neo4j graph dabatase information.
        Returns:
            citizen, landmark, cluster nodes and relationships
        '''
        with self.driver.session() as session:
            result = session.read_transaction(self.run_getClusterInfo)
        return result

    @staticmethod
    def run_getClusterInfo(tx):
        '''static method required to run query to fetch AuraDB data.'''
        query = (f'''
            MATCH (cls:Clusters)-[r:CLUSTER_DETECTED]-(l:Landmarks)
            RETURN cls,r,l
        ''')
        result = tx.run(query)
        try:
            data_arr = []
            for row in result:
                data_arr.append([row['cls']['status'],
                                 row['cls'].id,
                                 row['l']['landmark_id'],
                                 row['l']['name'],
                                 row['cls']['date_formed'],
                                 row['cls']['date_closed']])
            return data_arr
        except ServiceUnavailable as exception:
            logging.error(f'''{query} raised an error: \n {exception}'''.format(
                query=query, exception=exception))

    def getCitizensInCluster(self, landmark_id):
        '''Function to fetch neo4j graph dabatase information.
        Returns:
            citizen, landmark, cluster nodes and relationships
        '''
        with self.driver.session() as session:
            result = session.read_transaction(
                self.run_getCitizensInCluster, landmark_id)
        return result

    @staticmethod
    def run_getCitizensInCluster(tx, landmark_id):
        '''static method required to run query to fetch AuraDB data.'''
        query = (f'''
            MATCH (l:Landmarks{{landmark_id:'{landmark_id}'}})-[r:VISITED]-(c:Citizens{{most_recent_status:'infected'}})
            return DISTINCT l, c
        ''')
        result = tx.run(query)
        try:
            data_arr = []
            for row in result:
                data_arr.append([row['c']['nric'],
                                 row['c']['full_name'],
                                 row['c']['most_recent_status'],
                                 row['c']['address'],
                                 row['c']['mobile'],
                                 row['c']['date_of_birth'],
                                 row['c']['gender'],
                                 ])
            return data_arr
        except ServiceUnavailable as exception:
            logging.error(f'''{query} raised an error: \n {exception}'''.format(
                query=query, exception=exception))

    '''Load CSV Queries used to upload MongoDB data into neo4j AuraDB'''
    # load landmarks csv.
    """
    MATCH (l:Landmarks) DELETE l;
    LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/GeraldHeng/2103-covid-tracer/development/helper/landmarks.csv?token=AN5P4L36OSSGHSO76IVZTK3BU54M2' AS ldata
    WITH ldata WHERE ldata._id IS NOT NULL
    MERGE (l:Landmarks{landmark_id:ldata._id, name: ldata.name, latitude:ldata.latitude, 
             longitude:ldata.longitude, danger_level:ldata.danger_level})
    """
    # load citizens csv.
    """
    MATCH (c:Citizens) DELETE c;
    LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/GeraldHeng/2103-covid-tracer/development/helper/citizens.csv?token=AN5P4L7YSCPOCRWBBGWC5XLBU5WRS' AS cdata
    WITH cdata WHERE cdata._id IS NOT NULL
    MERGE (c:Citizens{citizen_id:cdata._id, full_name:cdata.full_name, nric:cdata.nric, address:cdata.address, mobile:cdata.mobile,
             date_of_birth:cdata.date_of_birth, gender:cdata.gender})
    """
    """
    MATCH (c:Citizens{citizen_id:'619dc3090f14dd6e8ec0c412'})
    MATCH (l:Landmarks{landmark_id:'619dc42fa3b5e8ecfe7b6c0e'})
    RETURN c,l
    """
