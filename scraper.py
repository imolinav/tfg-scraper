import psycopg2

hostname = 'localhost'
username = 'imolinav'
password = 'imolinav'
database = 'postgres'

connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
cur = connection.cursor()

cur.execute("""INSERT INTO cities (name, postal_code) values (%s, %s)""", ('Valencia', str(46016)))
connection.commit()