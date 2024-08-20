import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("interzap.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

    def start_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS groups(id TEXT PRIMARY KEY)")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_groups(
                user_id TEXT,
                group_id TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(group_id) REFERENCES groups(id),
                PRIMARY KEY(user_id, group_id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_messages(
                receiver_id TEXT,
                message TEXT,
                timestamp INTEGER,
                FOREIGN KEY(receiver_id) REFERENCES users(id)
            )
        """)
        self.conn.commit()

    def reset_db(self):
        self.cursor.execute("DROP TABLE IF EXISTS user_groups")
        self.cursor.execute("DROP TABLE IF EXISTS users")
        self.cursor.execute("DROP TABLE IF EXISTS groups")
        self.cursor.execute("DROP TABLE IF EXISTS pending_messages")
        self.conn.commit()
        self.start_db()

    # Users
    def get_all_users(self):
        return self.cursor.execute("SELECT * FROM users").fetchall()
    
    def create_user(self, id):
        try:
            self.cursor.execute("INSERT INTO users VALUES(?)", (id,))
            self.conn.commit()
            return True
        except Exception as e:
            print("Error on create user on DB: ", e)
            return False
    
    # Groups
    def get_all_groups(self):
        return self.cursor.execute("SELECT * FROM groups").fetchall()
    
    def create_group(self, id):
        try:
            self.cursor.execute("INSERT INTO groups VALUES(?)", (id,))
            self.conn.commit()
            return True
        except Exception as e:
            return False
    
    def get_group_members(self, group_id):
        self.cursor.execute("""
            SELECT user_id FROM user_groups
            WHERE group_id = ?
        """, (group_id,))
        return self.cursor.fetchall()

    def add_user_to_group(self, user_id, group_id):
        try:
            self.cursor.execute("INSERT INTO user_groups VALUES(?, ?)", (user_id, group_id))
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def get_users_in_group(self, group_id):
        self.cursor.execute("""
            SELECT users.id FROM users
            JOIN user_groups ON users.id = user_groups.user_id
            WHERE user_groups.group_id = ?
        """, (group_id,))
        return self.cursor.fetchall()
    
    # Pending messages
    def add_pending_message(self, receiver_id, message, time):
        try:
            self.cursor.execute("""
                INSERT INTO pending_messages (receiver_id, message, timestamp)
                VALUES (?, ?, ?)
            """, (receiver_id, message, int(time)))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error on adding pending message to DB: {e}")
            return False

    def get_pending_messages(self, user_id):
        return self.cursor.execute("""
            SELECT message FROM pending_messages
            WHERE receiver_id = ?
            ORDER BY timestamp ASC
        """, (user_id,)).fetchall()

    def delete_pending_messages(self, user_id):
        self.cursor.execute("""
            DELETE FROM pending_messages
            WHERE receiver_id = ?
        """, (user_id,))
        self.conn.commit()