import redis
import bcrypt
import logging
from datetime import datetime

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role
        self.logged_in = False
        redis_client.set(f"user:{self.username}", self.role)
        logging.basicConfig(filename='user.log', level=logging.INFO, format='%(asctime)s %(message)s')

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def __repr__(self):
        return f"User(username={self.username}, role={self.role})"

    @staticmethod
    def validate_role(role):
        """Validate the user role."""
        if role not in ["admin", "trader", "viewer"]:
            logging.error(f"Invalid role: {role}")
            raise ValueError("Role must be either 'admin', 'trader', or 'viewer'")
        return True

    def change_password(self, old_password, new_password):
        """Change the user's password if the old password matches."""
        if self.check_password(old_password):
            self.password = self.hash_password(new_password)
            logging.info(f"Password changed for user: {self.username}")
        else:
            logging.warning(f"Failed password change attempt for user: {self.username}")
            raise ValueError("Old password does not match")

    def set_role(self, new_role):
        """Set a new role for the user."""
        self.validate_role(new_role)
        self.role = new_role
        redis_client.set(f"user:{self.username}", self.role)
        logging.info(f"Role changed to {new_role} for user: {self.username}")

    def login(self, password):
        """User login."""
        if self.check_password(password):
            self.logged_in = True
            logging.info(f"User logged in: {self.username}")
            return True
        logging.warning(f"Login failed for user: {self.username}")
        return False

    def logout(self):
        """User logout."""
        self.logged_in = False
        logging.info(f"User logged out: {self.username}")
