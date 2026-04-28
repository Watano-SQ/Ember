import os
import sys
import datetime
# Add Ember to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from memory.db_pool import get_connection

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM message_list;")
        print("Total messages:", cur.fetchone()[0])
        
        cur.execute("SELECT id, sender, timestamp, text[:50] FROM message_list ORDER BY id DESC LIMIT 5;")
        print("Last 5 messages (Newest first):")
        for row in cur.fetchall():
            print(row)
            
        cur.execute("SELECT id, sender, timestamp, text[:50] FROM message_list ORDER BY id ASC LIMIT 5;")
        print("First 5 messages (Oldest first):")
        for row in cur.fetchall():
            print(row)
