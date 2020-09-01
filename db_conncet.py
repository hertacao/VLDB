import mysql.connector
import psycopg2


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="vldb"
)

pgdb = psycopg2.connect(
    database="PVLDB",
    user="postgres",
    password="root",
    host="127.0.0.1",
    port="5432")

print("Database opened successfully")