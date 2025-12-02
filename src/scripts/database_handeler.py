import sqlite3

class Database:
    def __init__(self, host_ip) -> None:
        self.connection = sqlite3.connect("users.db", check_same_thread=False)
        self.host_ip = host_ip
        
        self.connection.execute("""
            DROP TABLE IF EXISTS USERS
        """)
        
        self.connection.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            USER_NAME TEXT NOT NULL UNIQUE PRIMARY KEY,
            IP_ADDRESS TEXT NOT NULL,
            ADMIN BOOL NOT NULL DEFAULT 0,
            BANNED BOOL NOT NULL DEFAULT 0
        )""")
        
    def add_user(self, user_name: str, ip_address: str) -> None:
        admin = 1 if ip_address == "127.0.0.1" or ip_address == self.host_ip else 0
        self.connection.execute(f"""INSERT INTO USERS (USER_NAME, IP_ADDRESS, ADMIN, BANNED) VALUES (
            '{user_name}',
            '{ip_address}',
            {admin},
            0
        )""")
        
        self.connection.commit()
    
    def remove_user(self, user_name: str) -> None:
        self.connection.execute(f"""DELETE FROM USERS WHERE USER_NAME = '{user_name}'""")
        self.connection.commit()
    
    def get_users(self) -> list[str]:
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM USERS""")
        result = cursor.fetchall()
        
        return result
    
    def add_banned_user(self, ip_address: str) -> None:
        self.connection.execute(f"""UPDATE USERS SET BANNED = 1 WHERE IP_ADDRESS = '{ip_address}'""")
        self.connection.commit()
    
    def remove_banned_user(self, ip_address: str) -> None:
        self.connection.execute(f"""UPDATE USERS SET BANNED = 0 WHERE IP_ADDRESS = '{ip_address}'""")
        self.connection.commit()
    
    def get_banned_users(self) -> list[str]:
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM USERS WHERE BANNED = 1""")
        result = cursor.fetchall()
        
        return result
    
    def add_admin_user(self, user_name: str) -> None:
        self.connection.execute(f"""UPDATE USERS SET ADMIN = 1 WHERE USER_NAME = '{user_name}'""")
        self.connection.commit()
    
    def remove_admin_user(self, user_name: str) -> None:
        self.connection.execute(f"""UPDATE USERS SET ADMIN = 0 WHERE USER_NAME = '{user_name}'""")
        self.connection.commit()
    
    def get_admin_users(self) -> list[str]:
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM USERS WHERE ADMIN = 1""")
        result = cursor.fetchall()
        
        return result
    
    def get_name_by_ip(self, ip_address: str) -> list[str]:
        cursor = self.connection.cursor()
        cursor.execute(f"""SELECT USER_NAME FROM USERS WHERE IP_ADDRESS = '{ip_address}'""")
        result = cursor.fetchall()
        
        return list(sum(result, ()))
    
    def close_database(self) -> None:
        self.connection.close()