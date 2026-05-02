import mysql.connector
conn = mysql.connector.connect(host='localhost', port=3307, user='root', password='admin', database='qr_access')
cur = conn.cursor(buffered=True)

cur.execute('SHOW TABLES')
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)

for t in tables:
    cur.execute(f'SHOW COLUMNS FROM {t}')
    cols = cur.fetchall()
    print(f'\n--- {t} ---')
    for c in cols:
        print(f'  {c[0]}')

conn.close()
