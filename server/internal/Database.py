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
        self.conn.commit()

    def reset_db(self):
        self.cursor.execute("DROP TABLE IF EXISTS user_groups")
        self.cursor.execute("DROP TABLE IF EXISTS users")
        self.cursor.execute("DROP TABLE IF EXISTS groups")
        self.conn.commit()
        self.start_db()

    def get_all_users(self):
        return self.cursor.execute("SELECT * FROM users").fetchall()
    
    def get_all_groups(self):
        return self.cursor.execute("SELECT * FROM groups").fetchall()
    
    def get_group_members(self, group_id):
        self.cursor.execute("""
            SELECT user_id FROM user_groups
            WHERE group_id = ?
        """, (group_id,))
        return self.cursor.fetchall()
    
    def create_user(self, id):
        try:
            self.cursor.execute("INSERT INTO users VALUES(?)", (id))
            self.conn.commit()
            return True
        except Exception as e:
            print("Error on create user on DB: ", e)
            return False
    
    def create_group(self, id):
        try:
            self.cursor.execute("INSERT INTO groups VALUES(?)", (id,))
            self.conn.commit()
            return True
        except Exception as e:
            return False

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