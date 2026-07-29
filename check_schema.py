import psycopg2

conn = psycopg2.connect(
    dbname='smart_tourism',
    user='postgres',
    password='admin123',   # <-- replace with your actual postgres password
    host='localhost'
)
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='fact_reviews'")
for row in cur.fetchall():
    print(row)
conn.close()