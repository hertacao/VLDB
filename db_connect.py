import psycopg2
import sqlite3

pgdb = psycopg2.connect(
    database="PVLDB",
    user="postgres",
    password="root",
    host="127.0.0.1",
    port="5432")

dbfilestring = r"C:\Users\herta\OneDrive\Dokumente\Arbeit\PVLDBDB\pvldb.db"
sqlite = sqlite3.connect(dbfilestring)