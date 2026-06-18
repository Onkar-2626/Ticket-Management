import os
import psycopg2
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL
)

@contextmanager
def get_db():
    conn = pool.getconn()
    cursor = conn.cursor()        # ✅ Create cursor manually
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()            # ✅ Close cursor after yield
        pool.putconn(conn)        # ✅ Return connection to pool

def init_db():
    with get_db() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer (
                cust_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                pass VARCHAR(255) NOT NULL,
                phone_no VARCHAR(15) NOT NULL,
                gender VARCHAR(10) NOT NULL,
                age INTEGER NOT NULL
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS booking (
                bid SERIAL PRIMARY KEY,
                cust_id INTEGER REFERENCES customer(cust_id) ON DELETE CASCADE,
                source VARCHAR(100) NOT NULL,
                destination VARCHAR(100) NOT NULL,
                ticket_status VARCHAR(20) NOT NULL
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment (
                bid INTEGER REFERENCES booking(bid) ON DELETE CASCADE,
                cust_id INTEGER REFERENCES customer(cust_id) ON DELETE CASCADE,
                payment_status VARCHAR(20) NOT NULL
            );
        ''')