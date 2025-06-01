import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import logging
from config import DB_CONFIG
import re
from typing import Optional, Tuple, List
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_transfer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def parse_log_line(line: str) -> Optional[Tuple[datetime, str, str, int, str]]:
    """
    Parse a single line from the chatbot log file.
    Format: 2025-06-02 09:00:00 | query: text | response: text | satisfaction: 1/0 | [error_category]
    
    Args:
        line (str): A line from the log file
        
    Returns:
        Optional[Tuple]: (timestamp, query, response, satisfaction, error_category)
    """
    try:
        parts = line.strip().split(' | ')
        timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
        query = parts[1].split(': ')[1]
        response = parts[2].split(': ')[1]
        satisfaction = int(parts[3].split(': ')[1])
        error_category = 'success' if satisfaction == 1 else parts[4] if len(parts) > 4 else 'other_error'
        
        return timestamp, query, response, satisfaction, error_category
    except Exception as e:
        logging.error(f"Error parsing line: {line.strip()}")
        logging.error(f"Error details: {str(e)}")
        return None

def create_table(conn: psycopg2.extensions.connection) -> None:
    """
    Create the chatbot_logs table if it doesn't exist.
    
    Args:
        conn: PostgreSQL database connection
    """
    try:
        with conn.cursor() as cur:
            # Drop existing table if exists
            cur.execute("DROP TABLE IF EXISTS chatbot_logs")
            
            # Create new table
            cur.execute("""
                CREATE TABLE chatbot_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    satisfaction BOOLEAN NOT NULL,
                    error_category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
        logging.info("Table chatbot_logs created or already exists")
    except Exception as e:
        logging.error(f"Error creating table: {str(e)}")
        raise

def insert_batch(conn: psycopg2.extensions.connection, batch: List[Tuple]) -> None:
    """
    Insert a batch of records into the database.
    
    Args:
        conn: PostgreSQL database connection
        batch: List of tuples containing the data to insert
    """
    try:
        with conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO chatbot_logs (timestamp, query, response, satisfaction, error_category)
                VALUES (%s, %s, %s, %s, %s)
            """, batch)
        conn.commit()
        logging.info(f"Inserted batch of {len(batch)} records")
    except Exception as e:
        logging.error(f"Error inserting batch: {str(e)}")
        conn.rollback()
        raise

def transfer_data(log_file_path: str) -> None:
    """
    Transfer data from the log file to PostgreSQL database.
    
    Args:
        log_file_path (str): Path to the log file
    """
    conn = None
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("Connected to PostgreSQL database")
        
        # Create table if not exists
        create_table(conn)
        
        # Read and process log file
        batch_size = 1000
        batch = []
        total_processed = 0
        error_count = 0
        
        with open(log_file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                result = parse_log_line(line)
                if result:
                    batch.append(result)
                    total_processed += 1
                else:
                    error_count += 1
                
                if len(batch) >= batch_size:
                    insert_batch(conn, batch)
                    batch = []
                
                if line_num % 10000 == 0:
                    logging.info(f"Processed {line_num} lines...")
        
        # Insert any remaining records
        if batch:
            insert_batch(conn, batch)
        
        logging.info(f"Data transfer completed successfully")
        logging.info(f"Total records processed: {total_processed}")
        logging.info(f"Total errors: {error_count}")
        
    except Exception as e:
        logging.error(f"Error during data transfer: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed")

if __name__ == "__main__":
    try:
        log_file_path = "chatbot.log"
        transfer_data(log_file_path)
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        sys.exit(1)
