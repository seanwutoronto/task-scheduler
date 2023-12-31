# DB
import psycopg2
import psycopg2.extras as extras

def connect_to_postgres(
        POSTGRES_HOST,
        POSTGRES_DB,
        POSTGRES_PORT,
        POSTGRES_USER,
        POSTGRES_PASSWORD
        ):
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    cursor = conn.cursor()
    return conn, cursor


def close_connection_to_postgres(conn):
    conn.close()
    print('Postgres connection closed.')


def check_schema_exists(cursor, given_schema):
    cursor.execute("SELECT schema_name FROM information_schema.schemata;")
    schemas = cursor.fetchall()
    schemas = [_tuple[0] for _tuple in schemas]
    if given_schema in schemas:
        return True
    return False


def check_table_exists(cursor, given_schema, given_table):
    query_command = f'''
    SELECT EXISTS 
    (SELECT 1 FROM information_schema.tables WHERE 
    table_schema = '{given_schema}' AND table_name = '{given_table}');
    '''
    cursor.execute(query_command)
    if_exists = cursor.fetchone()[0]
    return if_exists


def create_empty_task_table(conn, cursor, given_schema, given_table):
    create_command = f'''
    CREATE TABLE {given_schema}.{given_table} (
        task_name TEXT NOT NULL PRIMARY KEY,
        task_type TEXT,
        task_description TEXT,
        frequency_type TEXT,
        at_month INT,
        at_week INT,
        at_day INT,
        at_hour INT
    );
    '''
    cursor.execute(create_command)
    conn.commit()
    print(f'Table: {given_table} created in {given_schema}.')


def query_table(cursor, given_schema, given_table):
    query = f"SELECT * FROM {given_schema}.{given_table};"
    cursor.execute(query)

    rows = cursor.fetchall()
    return rows


def upsert_to_table(conn, cursor, given_schema, given_table, input_data):
    cols_list = [
        'task_name', 'task_type', 'task_description',
        'frequency_type',
        'at_month', 'at_week', 'at_day', 'at_hour'
    ]
    cols = ','.join(cols_list).lower()
    query = 'INSERT INTO %s(%s) VALUES %%s' % (f'{given_schema}.{given_table}', cols)
    query = '''
    INSERT INTO %s(%s) VALUES %%s
    ON CONFLICT (task_name) DO UPDATE SET 
    task_type = EXCLUDED.task_type,
    task_description = EXCLUDED.task_description,
    frequency_type = EXCLUDED.frequency_type,
    at_month = EXCLUDED.at_month,
    at_week = EXCLUDED.at_week,
    at_day = EXCLUDED.at_day,
    at_hour = EXCLUDED.at_hour;
    ''' % (f'{given_schema}.{given_table}', cols)
    extras.execute_values(cursor, query, [input_data])
    conn.commit()



# General
def connection_error(error_message):
    print(error_message)