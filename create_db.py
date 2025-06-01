import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DB_CONFIG

def create_database():
    conn = None
    try:
        # Connect to default postgres database first
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cur:
            # Check if database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname='chatbot_metrics'")
            exists = cur.fetchone()
            
            if not exists:
                cur.execute('CREATE DATABASE chatbot_metrics')
                print("Database chatbot_metrics created successfully!")
            else:
                print("Database chatbot_metrics already exists!")
        
        # Connect to the created database to create tables
        conn.close()
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            # Create tables
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    satisfaction BOOLEAN NOT NULL,
                    error_category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_logs(timestamp);
                CREATE INDEX IF NOT EXISTS idx_satisfaction ON chat_logs(satisfaction);
                CREATE INDEX IF NOT EXISTS idx_error_category ON chat_logs(error_category);
            """)
            
            conn.commit()
            print("Tables created successfully!")
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()
