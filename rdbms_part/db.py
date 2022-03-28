'''
This module help to encapulsate all functions and variables needed to connect
to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import mysql.connector


class DatabaseClient:
    '''Database Client to connect to MYSQL server.
    Args:
        host (str): The uri of the database.
        username (str): The username to log into the database.
        password (str): The password to log into the database.
        db_name (str): The which db you want to access in the database.
    '''

    def __init__(self, host, username, password, db_name):
        self.host = host
        self.username = username
        self.password = password
        self.db_name = db_name
        self.db = None
        self.cursor = None

    def connect(self):
        '''Connect to the database using crendential in class.
        Returns:
            bool: a bool of whether connect is successful.
        '''
        try:
            db = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.db_name,
                ssl_disabled=True

            )
            print(db)

            # If connected, populate db and cursor in class.
            self.db = db
            self.cursor = db.cursor(())
            return True

        except Exception as e:
            print(e)
            return False

    def refresh_connection(self):
        '''Refresh connect with the database.
        '''
        try:
            # Try to ping db and get connection back.
            print('ping and reconnect')
            self.db.ping(reconnect=True, attempts=3, delay=5)
        except mysql.connector.Error as err:
            # Error, try connecting again.
            print('error when connecting... Trying again')
            self.connect()

    def create(self, table_name, columns, values):
        '''Basic feature. Create a row in a table.
        Args:
        table_name (str): Name of table to insert into.
        columns (list of str): List of columns name to insert into.
        values (list): List of values name to insert into.

        Returns:
            bool: Bool of whether create is successful.
        '''
        # Refresh connection in case db connection is lost.
        self.refresh_connection()

        # Prepare strings for db query.
        column_str = ','.join(map(str, columns))

        # SQL statement.
        query = f'INSERT INTO {table_name} ({column_str}) VALUES {values}'

        # Execution.
        self.cursor.execute(query)
        self.db.commit()
        print(self.cursor.rowcount, 'record(s) affected')

        # If more than 1, inserted successfully.
        return self.cursor.rowcount > 0

    def create_many(self, table_name, columns, values):
        '''Basic feature. Create multiple rows in 1 statement.
        Args:
        table_name (str): Name of table to insert into.
        columns (list of str): List of columns name to insert into.
        values (list): List of values name to insert into.

        Returns:
            bool: Bool of whether create is successful.
        '''
        # Refresh connection in case db connection is lost.
        self.refresh_connection()

        # Prepare strings for db query.
        column_str = ''
        value_str = ''
        for column in columns:
            column_str += column + ','
            value_str += '%s,'

        # Remove ,.
        column_str = column_str[0:-1]
        value_str = value_str[0:-1]

        # SQL statement.
        query = f'INSERT INTO {table_name} ({column_str}) VALUES ({value_str})'
        print(values)

        # Execution.
        self.cursor.executemany(query, values)
        self.db.commit()
        print(self.cursor.rowcount, 'record(s) affected')

        # If more than 1, inserted successfully.
        return self.cursor.rowcount > 0

    def select_all(self, table_name):
        '''Basic feature. Select all columns in a table.
        Args:
        table_name (str): Name of table to insert into.

        Returns:
            list: List of rows that is selected from the db.
        '''

        # Refresh connection in case db connection is lost.
        self.refresh_connection()

        # SQL statement.
        query = f'SELECT * FROM {table_name}'

        # Execution.
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_by_id(self, table_name, id, changed_columns, new_values):
        '''Basic feature. Update row by id with new values to changed_columns.
        Args:
        table_name (str): Name of table to insert into.
        id (str/number): id of row to update.
        changed_columns (list): List of columns name to update in row.
        new_values (list): List of values name to update in row.

        Returns:
            bool: Bool of whether update is successful.
        '''
        # Refresh connection in case db connection is lost.
        self.refresh_connection()

        # Merge changed columns and new values together. Need to be same len.
        if len(changed_columns) == len(new_values):
            set_str = ''
            for i in range(len(changed_columns)):
                set_str += f'{changed_columns[i]} = "{new_values[i]}",'

            set_str = set_str[0:-1]

            # SQL statement.
            query = f'UPDATE {table_name} SET {set_str} WHERE id = {id}'

            # Execution.
            self.cursor.execute(query)
            self.db.commit()
            print(self.cursor.rowcount, 'record(s) affected')

            # If more than 1, inserted successfully.
            return self.cursor.rowcount > 0

        return False

    def delete_by_id(self, table_name, id):
        '''Basic feature. Delete row by id.
        Args:
        table_name (str): Name of table to insert into.

        Returns:
            bool: Bool of whether delete is successful.
        '''
        # Refresh connection in case db connection is lost.
        self.refresh_connection()

        # SQL statement.
        query = f'DELETE FROM {table_name} WHERE id = {id}'

        # Execution.
        self.cursor.execute(query)
        self.db.commit()
        print(self.cursor.rowcount, 'record(s) affected')

        # If more than 1, inserted successfully.
        return self.cursor.rowcount > 0

    def execute_statement(self, statement):
        '''Function to execute any statement to the db.
        Args:
        statement (str): query to execute in the db.

        Returns:
            cursor: db cursor so to manipulate/
        '''
        # Refresh connection in case db connection is lost.
        self.refresh_connection()

        # Execute statement.
        self.cursor.execute(statement)
        return self.cursor
