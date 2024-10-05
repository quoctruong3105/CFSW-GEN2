import psycopg2

class Database:
    def __init__(self, dbname):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user="svcfsw",
                password="cfsw12345",
                host="pg_db",
                port="5432"
            )
        except Exception as e:
            print(f"Failed to connect to the database: {e}")

    def insert(self, insert_query, data):
        print(insert_query)
        try:
            cursor = self.conn.cursor()
            cursor.executemany(insert_query, data)
            self.conn.commit()
            print(f"Inserted {cursor.rowcount} rows to successfully.")
        except Exception as e:
            print(f"Error occurred while inserting: {e}")
            pass
        finally:
            cursor.close()
