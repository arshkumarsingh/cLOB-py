# user.py
import bcrypt

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def __repr__(self):
        return f"User(username={self.username}, role={self.role})"
